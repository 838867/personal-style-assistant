"""饮食管理工具"""

from datetime import datetime
from typing import Any, Dict
from langchain.tools import tool
from postgrest.exceptions import APIError
from storage.database.supabase_client import get_supabase_client
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context


@tool
def create_diet_plan(
    goal: str,
    daily_calories: int,
    protein_ratio: float,
    carb_ratio: float,
    fat_ratio: float,
    plan_content: str = ""
) -> str:
    """
    创建饮食计划

    Args:
        goal: 饮食目标（减脂/增肌/维持）
        daily_calories: 每日目标热量(千卡)
        protein_ratio: 蛋白质占比(0-1)
        carb_ratio: 碳水化合物占比(0-1)
        fat_ratio: 脂肪占比(0-1)
        plan_content: 饮食计划详细内容，如果为空则自动生成

    Returns:
        str: 创建结果提示
    """
    ctx = request_context.get() or new_context(method="create_diet_plan")
    try:
        client = get_supabase_client()

        client.table('diet_plans').insert({
            'goal': goal,
            'daily_calories': daily_calories,
            'protein_ratio': protein_ratio,
            'carb_ratio': carb_ratio,
            'fat_ratio': fat_ratio,
            'plan_content': plan_content
        }).execute()

        protein_percent = int(protein_ratio * 100)
        carb_percent = int(carb_ratio * 100)
        fat_percent = int(fat_ratio * 100)

        return f"✓ 饮食计划已创建：{goal}，每日{daily_calories}千卡（蛋白质{protein_percent}%，碳水{carb_percent}%，脂肪{fat_percent}%）"
    except APIError as e:
        raise Exception(f"创建饮食计划失败: {e.message}")


@tool
def get_diet_plan() -> str:
    """
    获取当前饮食计划

    Returns:
        str: 饮食计划详细信息
    """
    ctx = request_context.get() or new_context(method="get_diet_plan")
    try:
        client = get_supabase_client()
        response = client.table('diet_plans').select('*').order('id', desc=True).limit(1).execute()

        if not response.data:
            return "未找到饮食计划，请先使用 create_diet_plan 创建计划"

        plan = response.data[0]
        if not isinstance(plan, dict):
            return "数据格式错误"

        protein_percent = int(float(plan.get('protein_ratio', 0)) * 100)
        carb_percent = int(float(plan.get('carb_ratio', 0)) * 100)
        fat_percent = int(float(plan.get('fat_ratio', 0)) * 100)

        return f"""
饮食计划：
- 目标：{plan.get('goal', '未知')}
- 每日目标热量：{plan.get('daily_calories', '未知')} 千卡
- 营养配比：蛋白质{protein_percent}%，碳水化合物{carb_percent}%，脂肪{fat_percent}%
- 计划内容：{plan.get('plan_content', '未知')}
- 创建时间：{plan.get('created_at', '未知')}
"""
    except APIError as e:
        raise Exception(f"查询饮食计划失败: {e.message}")


@tool
def log_diet(
    meal_type: str,
    food_name: str,
    calories: float,
    protein: float = 0,
    notes: str = ""
) -> str:
    """
    记录每日饮食

    Args:
        meal_type: 餐次（早餐/午餐/晚餐/加餐）
        food_name: 食物名称
        calories: 热量(千卡)
        protein: 蛋白质(g)，可选
        notes: 备注（可选）

    Returns:
        str: 记录结果提示
    """
    ctx = request_context.get() or new_context(method="log_diet")
    try:
        client = get_supabase_client()

        client.table('diet_records').insert({
            'log_date': datetime.now().isoformat(),
            'meal_type': meal_type,
            'food_name': food_name,
            'calories': calories,
            'protein': protein if protein > 0 else None,
            'notes': notes
        }).execute()

        protein_str = f"，蛋白质{protein}g" if protein > 0 else ""
        return f"✓ 已记录{meal_type}：{food_name}，{calories}千卡{protein_str}"
    except APIError as e:
        raise Exception(f"记录饮食失败: {e.message}")


@tool
def get_diet_log(days: int = 7) -> str:
    """
    获取饮食记录

    Args:
        days: 获取最近多少天的记录，默认7天

    Returns:
        str: 饮食记录列表
    """
    ctx = request_context.get() or new_context(method="get_diet_log")
    try:
        client = get_supabase_client()

        response = client.table('diet_records').select('*').order('log_date', desc=True).limit(days * 20).execute()

        if not response.data:
            return "未找到饮食记录"

        # 按日期分组统计
        date_stats: Dict[str, Any] = {}
        for item in response.data:
            if not isinstance(item, dict):
                continue
            log_date_str = str(item.get('log_date', ''))[:10]  # 只取日期部分
            if log_date_str not in date_stats:
                date_stats[log_date_str] = {
                    'total_calories': 0,
                    'total_protein': 0,
                    'meals': []
                }
            date_stats[log_date_str]['total_calories'] += item.get('calories', 0)
            date_stats[log_date_str]['total_protein'] += item.get('protein', 0)
            protein_str = f"，蛋白质{item.get('protein')}g" if item.get('protein') else ""
            date_stats[log_date_str]['meals'].append(
                f"  {item.get('meal_type')}：{item.get('food_name')}，{item.get('calories')}千卡{protein_str}"
            )

        result = []
        for date, stats in list(date_stats.items())[:days]:
            meal_list = "\n".join(stats['meals'])
            protein_str = f"，蛋白质{stats['total_protein']}g" if stats['total_protein'] > 0 else ""
            result.append(f"- {date}\n  总热量：{stats['total_calories']}千卡{protein_str}\n{meal_list}")

        return f"饮食记录（最近{days}天）：\n" + "\n".join(result)
    except APIError as e:
        raise Exception(f"查询饮食记录失败: {e.message}")


@tool
def analyze_diet_and_exercise(days: int = 7) -> str:
    """
    分析饮食和锻炼数据，给出建议

    Args:
        days: 分析最近多少天的数据，默认7天

    Returns:
        str: 分析结果和建议
    """
    ctx = request_context.get() or new_context(method="analyze_diet_and_exercise")
    try:
        client = get_supabase_client()

        # 获取饮食记录
        diet_response = client.table('diet_records').select('*').order('log_date', desc=True).limit(days * 20).execute()

        # 获取锻炼记录
        exercise_response = client.table('daily_exercise_log').select('*').order('log_date', desc=True).limit(days * 10).execute()

        # 获取饮食计划
        diet_plan_response = client.table('diet_plans').select('*').order('id', desc=True).limit(1).execute()

        # 统计数据
        total_calories_in = 0.0
        total_calories_out = 0.0
        total_protein = 0.0
        exercise_count = 0
        total_workout_time = 0

        if diet_response.data:
            for item in diet_response.data:
                if isinstance(item, dict):
                    total_calories_in += float(item.get('calories', 0))
                    total_protein += float(item.get('protein', 0))

        if exercise_response.data:
            for item in exercise_response.data:
                if isinstance(item, dict):
                    total_calories_out += float(item.get('calories_burned', 0))
                    exercise_count += 1
                    total_workout_time += int(item.get('duration', 0))

        avg_calories_per_day = int(total_calories_in / days) if days > 0 else 0
        avg_workout_per_day = int(total_workout_time / days) if days > 0 else 0
        protein_per_day = int(total_protein / days) if days > 0 else 0

        target_calories = 0
        if diet_plan_response.data and isinstance(diet_plan_response.data[0], dict):
            target_calories = float(diet_plan_response.data[0].get('daily_calories', 0))

        # 生成建议
        suggestions = []
        if target_calories > 0:
            if avg_calories_per_day > target_calories * 1.1:
                suggestions.append(f"⚠️ 平均每日热量摄入({avg_calories_per_day}千卡)超过目标({target_calories}千卡)10%以上，建议减少高热量食物")
            elif avg_calories_per_day < target_calories * 0.9:
                suggestions.append(f"⚠️ 平均每日热量摄入({avg_calories_per_day}千卡)低于目标({target_calories}千卡)10%以上，建议适当增加营养摄入")

        if avg_workout_per_day < 30:
            suggestions.append("💪 建议增加运动量，目标是每天至少30分钟")
        elif avg_workout_per_day >= 30 and avg_workout_per_day < 60:
            suggestions.append("✅ 运动量良好，保持当前节奏")
        else:
            suggestions.append("🏆 运动量优秀！继续保持")

        if protein_per_day < 50:
            suggestions.append("🥩 蛋白质摄入偏低，建议增加鸡蛋、鸡胸肉、豆制品等高蛋白食物")

        result = f"""
📊 最近{days}天数据统计：
- 平均每日热量摄入：{avg_calories_per_day} 千卡
- 平均每日蛋白质摄入：{protein_per_day} g
- 平均每日运动时长：{avg_workout_per_day} 分钟
- 总运动次数：{exercise_count} 次
- 总消耗热量：{int(total_calories_out)} 千卡

💡 建议：
{chr(10).join(suggestions) if suggestions else "继续保持良好的饮食习惯！"}
"""
        return result
    except APIError as e:
        raise Exception(f"分析数据失败: {e.message}")
