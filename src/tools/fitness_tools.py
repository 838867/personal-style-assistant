"""
健身规划工具
Fitness Planning Tools
"""
from typing import Optional, Dict, Any, List
from langchain.tools import tool
from postgrest.exceptions import APIError
from storage.database.supabase_client import get_supabase_client
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context


def _parse_response_data(response) -> List[Dict[str, Any]]:
    """安全解析 Supabase 响应数据"""
    try:
        data = response.data
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        else:
            return []
    except Exception:
        return []


@tool
def create_fitness_plan(
    user_id: str,
    plan_name: str,
    goal: str,
    duration_weeks: int,
    frequency_per_week: int,
    exercises: str,
    target_calories: int,
    notes: Optional[str] = None
) -> str:
    """创建健身计划。"""
    ctx = request_context.get() or new_context(method="create_fitness_plan")
    client = get_supabase_client()
    
    data = {
        "plan_name": plan_name,
        "goal": goal,
        "duration_weeks": duration_weeks,
        "frequency_per_week": frequency_per_week,
        "exercises": exercises,
        "target_calories": target_calories,
        "notes": notes
    }
    
    data = {k: v for k, v in data.items() if v is not None}
    
    try:
        response = client.table('fitness_plan').insert(data).execute()
        items = _parse_response_data(response)
        if items:
            return f"健身计划创建成功！ID: {items[0].get('id', 'unknown')}"
        return "健身计划创建成功"
    except APIError as e:
        raise Exception(f"创建健身计划失败: {e.message}")


@tool
def get_fitness_plan(
    user_id: str,
    is_active: bool = True,
    limit: int = 10
) -> str:
    """获取健身计划列表。"""
    ctx = request_context.get() or new_context(method="get_fitness_plan")
    client = get_supabase_client()
    
    try:
        query = client.table('fitness_plan').select('*')
        
        if is_active:
            query = query.eq('is_active', True)
        
        response = query.limit(limit).execute()
        items = _parse_response_data(response)
        
        if not items:
            return "没有找到健身计划"
        
        result = f"健身计划列表（共 {len(items)} 个）：\n"
        
        for idx, plan in enumerate(items, 1):
            if isinstance(plan, dict):
                result += f"\n{idx}. {plan.get('plan_name', '未知')}\n"
                result += f"   目标: {plan.get('goal', '未设置')}\n"
                result += f"   持续: {plan.get('duration_weeks', 0)} 周\n"
                result += f"   频率: 每周 {plan.get('frequency_per_week', 0)} 次\n"
                result += f"   目标消耗: {plan.get('target_calories', 0)} kcal\n"
                result += f"   训练内容: {plan.get('exercises', '未设置')}\n"
        
        return result
    except Exception as e:
        return f"查询健身计划失败: {str(e)}"


@tool
def record_fitness(
    user_id: str,
    plan_id: int,
    log_date: str,
    duration_minutes: int,
    calories_burned: int,
    exercises_completed: str,
    notes: Optional[str] = None
) -> str:
    """记录健身记录。"""
    ctx = request_context.get() or new_context(method="record_fitness")
    client = get_supabase_client()
    
    data = {
        "user_id": user_id,
        "plan_id": plan_id,
        "log_date": log_date,
        "duration_minutes": duration_minutes,
        "calories_burned": calories_burned,
        "exercises_completed": exercises_completed,
        "notes": notes
    }
    
    data = {k: v for k, v in data.items() if v is not None}
    
    try:
        response = client.table('daily_exercise_log').insert(data).execute()
        items = _parse_response_data(response)
        if items:
            return f"健身记录保存成功！ID: {items[0].get('id', 'unknown')}"
        return "健身记录保存成功"
    except APIError as e:
        raise Exception(f"保存健身记录失败: {e.message}")


@tool
def get_daily_exercise_log(
    user_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 30
) -> str:
    """获取健身记录。"""
    ctx = request_context.get() or new_context(method="get_daily_exercise_log")
    client = get_supabase_client()
    
    try:
        query = client.table('daily_exercise_log').select('*')
        
        if start_date:
            query = query.gte('log_date', start_date)
        if end_date:
            query = query.lte('log_date', end_date)
        
        response = query.order('log_date', desc=True).limit(limit).execute()
        items = _parse_response_data(response)
        
        if not items:
            return "没有找到健身记录"
        
        result = f"健身记录列表（共 {len(items)} 条）：\n"
        
        total_calories = 0
        total_duration = 0
        
        for idx, record in enumerate(items, 1):
            if isinstance(record, dict):
                calories = record.get('calories_burned', 0) or 0
                duration = record.get('duration_minutes', 0) or 0
                total_calories += calories
                total_duration += duration
                
                result += f"\n{idx}. {record.get('log_date', '未知')}\n"
                result += f"   时长: {duration} 分钟\n"
                result += f"   消耗: {calories} kcal\n"
                result += f"   内容: {record.get('exercises_completed', '未设置')}\n"
        
        result += f"\n汇总：总消耗 {total_calories} kcal，总时长 {total_duration} 分钟"
        
        return result
    except Exception as e:
        return f"查询健身记录失败: {str(e)}"
