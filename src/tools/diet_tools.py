"""
饮食管理工具
Diet Management Tools
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
def create_diet_plan(
    user_id: str,
    plan_name: str,
    goal: str,
    duration_weeks: int,
    daily_calorie_target: int,
    macronutrient_ratio: str,
    meals_per_day: int,
    notes: Optional[str] = None
) -> str:
    """创建饮食计划。"""
    ctx = request_context.get() or new_context(method="create_diet_plan")
    client = get_supabase_client()
    
    data = {
        "user_id": user_id,
        "plan_name": plan_name,
        "goal": goal,
        "duration_weeks": duration_weeks,
        "daily_calorie_target": daily_calorie_target,
        "macronutrient_ratio": macronutrient_ratio,
        "meals_per_day": meals_per_day,
        "notes": notes
    }
    
    data = {k: v for k, v in data.items() if v is not None}
    
    try:
        response = client.table('diet_plans').insert(data).execute()
        items = _parse_response_data(response)
        if items:
            return f"饮食计划创建成功！ID: {items[0].get('id', 'unknown')}"
        return "饮食计划创建成功"
    except APIError as e:
        raise Exception(f"创建饮食计划失败: {e.message}")


@tool
def get_diet_plans(
    user_id: str,
    is_active: bool = True,
    limit: int = 10
) -> str:
    """获取饮食计划列表。"""
    ctx = request_context.get() or new_context(method="get_diet_plans")
    client = get_supabase_client()
    
    try:
        query = client.table('diet_plans').select('*').eq('user_id', user_id)
        
        if is_active:
            query = query.eq('is_active', True)
        
        response = query.limit(limit).execute()
        items = _parse_response_data(response)
        
        if not items:
            return "没有找到饮食计划"
        
        result = f"饮食计划列表（共 {len(items)} 个）：\n"
        
        for idx, plan in enumerate(items, 1):
            if isinstance(plan, dict):
                result += f"\n{idx}. {plan.get('plan_name', '未知')}\n"
                result += f"   目标: {plan.get('goal', '未设置')}\n"
                result += f"   持续: {plan.get('duration_weeks', 0)} 周\n"
                result += f"   每日目标: {plan.get('daily_calorie_target', 0)} kcal\n"
                result += f"   营养素比例: {plan.get('macronutrient_ratio', '未设置')}\n"
                result += f"   每日餐数: {plan.get('meals_per_day', 0)} 餐\n"
        
        return result
    except Exception as e:
        return f"查询饮食计划失败: {str(e)}"


@tool
def record_diet(
    user_id: str,
    plan_id: Optional[int] = None,
    meal_date: str = None,
    meal_type: str = None,
    food_items: str = None,
    calories: int = None,
    protein: float = None,
    carbs: float = None,
    fat: float = None,
    notes: Optional[str] = None
) -> str:
    """记录饮食。"""
    import datetime
    ctx = request_context.get() or new_context(method="record_diet")
    client = get_supabase_client()
    
    # 处理默认值
    if meal_date is None:
        meal_date = datetime.datetime.now().strftime('%Y-%m-%d')
    if meal_type is None:
        meal_type = "午餐"
    if food_items is None:
        food_items = ""
    if calories is None:
        calories = 0
    if protein is None:
        protein = 0.0
    if carbs is None:
        carbs = 0.0
    if fat is None:
        fat = 0.0
    
    # 检查plan_id是否有效
    effective_plan_id = None
    if plan_id and plan_id > 0:
        # 验证计划是否存在
        try:
            response = client.table('diet_plans').select('id').eq('id', plan_id).maybe_single().execute()
            items = _parse_response_data(response)
            if items:
                effective_plan_id = plan_id
        except Exception:
            pass
    
    data = {
        "user_id": user_id,
        "plan_id": effective_plan_id,
        "meal_date": meal_date,
        "meal_type": meal_type,
        "food_items": food_items,
        "calories": calories,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "notes": notes
    }
    
    data = {k: v for k, v in data.items() if v is not None}
    
    try:
        response = client.table('diet_records').insert(data).execute()
        items = _parse_response_data(response)
        if items:
            return f"饮食记录保存成功！ID: {items[0].get('id', 'unknown')}"
        return "饮食记录保存成功"
    except APIError as e:
        raise Exception(f"保存饮食记录失败: {e.message}")


@tool
def get_diet_records(
    user_id: str,
    meal_date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 30
) -> str:
    """获取饮食记录。"""
    ctx = request_context.get() or new_context(method="get_diet_records")
    client = get_supabase_client()
    
    try:
        query = client.table('diet_records').select('*').eq('user_id', user_id)
        
        if meal_date:
            query = query.eq('meal_date', meal_date)
        else:
            if start_date:
                query = query.gte('meal_date', start_date)
            if end_date:
                query = query.lte('meal_date', end_date)
        
        response = query.order('meal_date', desc=True).limit(limit).execute()
        items = _parse_response_data(response)
        
        if not items:
            return "没有找到饮食记录"
        
        result = f"饮食记录列表（共 {len(items)} 条）：\n"
        
        for idx, record in enumerate(items, 1):
            if isinstance(record, dict):
                result += f"\n{idx}. {record.get('meal_date', '未知')} {record.get('meal_type', '')}\n"
                result += f"   食物: {record.get('food_items', '未设置')}\n"
                result += f"   卡路里: {record.get('calories', 0)} kcal\n"
                result += f"   蛋白质: {record.get('protein', 0)}g  碳水: {record.get('carbs', 0)}g  脂肪: {record.get('fat', 0)}g\n"
        
        return result
    except Exception as e:
        return f"查询饮食记录失败: {str(e)}"


@tool
def get_daily_nutrition_summary(user_id: str, target_date: str) -> str:
    """获取每日营养摘要。"""
    ctx = request_context.get() or new_context(method="get_daily_nutrition_summary")
    client = get_supabase_client()
    
    try:
        response = client.table('diet_records').select('*').eq('user_id', user_id).eq('meal_date', target_date).execute()
        items = _parse_response_data(response)
        
        if not items:
            return f"{target_date} 没有饮食记录"
        
        total_calories = 0
        total_protein = 0.0
        total_carbs = 0.0
        total_fat = 0.0
        
        meal_details = []
        
        for record in items:
            if isinstance(record, dict):
                calories = record.get('calories', 0) or 0
                protein = record.get('protein', 0) or 0.0
                carbs = record.get('carbs', 0) or 0.0
                fat = record.get('fat', 0) or 0.0
                
                total_calories += calories
                total_protein += protein
                total_carbs += carbs
                total_fat += fat
                
                meal_details.append(f"{record.get('meal_type', '')}: {record.get('food_items', '')}")
        
        result = f"📅 {target_date} 营养摘要\n"
        result += f"{'='*30}\n"
        result += f"总摄入:\n"
        result += f"  卡路里: {total_calories} kcal\n"
        result += f"  蛋白质: {total_protein}g\n"
        result += f"  碳水: {total_carbs}g\n"
        result += f"  脂肪: {total_fat}g\n"
        result += f"{'='*30}\n"
        result += f"餐次明细:\n"
        for detail in meal_details:
            result += f"  • {detail}\n"
        
        return result
    except Exception as e:
        return f"获取营养摘要失败: {str(e)}"
