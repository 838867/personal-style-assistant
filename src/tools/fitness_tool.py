"""健身管理工具"""

from datetime import datetime
from typing import Any, Dict
from langchain.tools import tool
from postgrest.exceptions import APIError
from storage.database.supabase_client import get_supabase_client
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context


@tool
def create_fitness_plan(
    goal: str,
    weekly_workout_days: int,
    workout_duration: int,
    intensity: str,
    target_weight: float = 0,
    plan_content: str = ""
) -> str:
    """
    创建健身计划

    Args:
        goal: 健身目标（减脂/增肌/塑形/维持）
        weekly_workout_days: 每周训练天数
        workout_duration: 每次训练时长(分钟)
        intensity: 强度（低/中/高）
        target_weight: 目标体重(kg)，可选
        plan_content: 健身计划详细内容，如果为空则自动生成

    Returns:
        str: 创建结果提示
    """
    ctx = request_context.get() or new_context(method="create_fitness_plan")
    try:
        client = get_supabase_client()

        client.table('fitness_plan').insert({
            'goal': goal,
            'target_weight': target_weight if target_weight > 0 else None,
            'weekly_workout_days': weekly_workout_days,
            'workout_duration': workout_duration,
            'intensity': intensity,
            'plan_content': plan_content
        }).execute()

        return f"✓ 健身计划已创建：{goal}，每周{weekly_workout_days}天，每次{workout_duration}分钟，强度{intensity}"
    except APIError as e:
        raise Exception(f"创建健身计划失败: {e.message}")


@tool
def get_fitness_plan() -> str:
    """
    获取当前健身计划

    Returns:
        str: 健身计划详细信息
    """
    ctx = request_context.get() or new_context(method="get_fitness_plan")
    try:
        client = get_supabase_client()
        response = client.table('fitness_plan').select('*').order('id', desc=True).limit(1).execute()

        if not response.data:
            return "未找到健身计划，请先使用 create_fitness_plan 创建计划"

        plan = response.data[0]
        if not isinstance(plan, dict):
            return "数据格式错误"

        return f"""
健身计划：
- 目标：{plan.get('goal', '未知')}
- 目标体重：{plan.get('target_weight', '未设置')} kg
- 每周训练天数：{plan.get('weekly_workout_days', '未知')} 天
- 每次训练时长：{plan.get('workout_duration', '未知')} 分钟
- 强度：{plan.get('intensity', '未知')}
- 计划内容：{plan.get('plan_content', '未知')}
- 创建时间：{plan.get('created_at', '未知')}
"""
    except APIError as e:
        raise Exception(f"查询健身计划失败: {e.message}")


@tool
def log_exercise(
    exercise_name: str,
    duration: int,
    intensity: str,
    calories_burned: float = 0,
    notes: str = ""
) -> str:
    """
    记录每日锻炼

    Args:
        exercise_name: 运动名称（如：跑步、力量训练、瑜伽等）
        duration: 运动时长（分钟）
        intensity: 强度（低/中/高）
        calories_burned: 消耗热量（千卡），可选
        notes: 备注（可选）

    Returns:
        str: 记录结果提示
    """
    ctx = request_context.get() or new_context(method="log_exercise")
    try:
        client = get_supabase_client()

        client.table('daily_exercise_log').insert({
            'log_date': datetime.now().isoformat(),
            'exercise_name': exercise_name,
            'duration': duration,
            'calories_burned': calories_burned if calories_burned > 0 else None,
            'intensity': intensity,
            'notes': notes
        }).execute()

        return f"✓ 已记录锻炼：{exercise_name}，{duration}分钟，强度{intensity}"
    except APIError as e:
        raise Exception(f"记录锻炼失败: {e.message}")


@tool
def get_exercise_log(days: int = 7) -> str:
    """
    获取锻炼记录

    Args:
        days: 获取最近多少天的记录，默认7天

    Returns:
        str: 锻炼记录列表
    """
    ctx = request_context.get() or new_context(method="get_exercise_log")
    try:
        client = get_supabase_client()

        response = client.table('daily_exercise_log').select('*').order('log_date', desc=True).limit(days * 10).execute()

        if not response.data:
            return "未找到锻炼记录"

        result = []
        for item in response.data:
            if not isinstance(item, dict):
                continue
            calories_str = f"，消耗{item.get('calories_burned')}千卡" if item.get('calories_burned') else ""
            notes_str = f"\n  备注：{item.get('notes')}" if item.get('notes') else ""
            result.append(f"- {item.get('log_date')} {item.get('exercise_name')}，{item.get('duration')}分钟，{item.get('intensity')}强度{calories_str}{notes_str}")

        return f"锻炼记录（最近{days}天）：\n" + "\n".join(result[:days * 5])
    except APIError as e:
        raise Exception(f"查询锻炼记录失败: {e.message}")
