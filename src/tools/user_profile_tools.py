"""
用户档案管理工具
User Profile Management Tools
"""
import json
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
def create_user_profile(
    user_id: str,
    name: Optional[str] = None,
    age: Optional[int] = None,
    gender: Optional[str] = None,
    height: Optional[float] = None,
    weight: Optional[float] = None,
    body_fat: Optional[float] = None,
    body_type: Optional[str] = None,
    style_preference: Optional[str] = None,
    location: Optional[str] = None,
    occupation: Optional[str] = None,
    fitness_goal: Optional[str] = None,
    diet_preference: Optional[str] = None,
    daily_calorie_intake: Optional[int] = None,
    daily_calorie_burn: Optional[int] = None,
    metadata_json: Optional[Dict[str, Any]] = None
) -> str:
    """创建用户档案。"""
    ctx = request_context.get() or new_context(method="create_user_profile")
    client = get_supabase_client()
    
    data = {
        "user_id": user_id,
        "name": name,
        "age": age,
        "gender": gender,
        "height": height,
        "weight": weight,
        "body_fat": body_fat,
        "body_type": body_type,
        "style_preference": style_preference,
        "location": location,
        "occupation": occupation,
        "fitness_goal": fitness_goal,
        "diet_preference": diet_preference,
        "daily_calorie_intake": daily_calorie_intake,
        "daily_calorie_burn": daily_calorie_burn,
        "metadata": json.dumps(metadata_json) if metadata_json else None
    }
    
    data = {k: v for k, v in data.items() if v is not None}
    
    try:
        response = client.table('user_profile').insert(data).execute()
        items = _parse_response_data(response)
        if items:
            record_id = items[0].get('id', 'unknown')
            return f"用户档案创建成功！ID: {record_id}"
        return "用户档案创建成功"
    except APIError as e:
        raise Exception(f"创建用户档案失败: {e.message}")


@tool
def get_user_profile(user_id: str) -> str:
    """查询用户档案。"""
    ctx = request_context.get() or new_context(method="get_user_profile")
    client = get_supabase_client()
    
    try:
        response = client.table('user_profile').select('*').maybe_single().execute()
        profile = _parse_response_data(response)
        
        if not profile:
            return "未找到该用户档案"
        
        p = profile[0]
        result = f"用户档案信息：\n"
        result += f"- 姓名: {p.get('name', '未设置')}\n"
        result += f"- 年龄: {p.get('age', '未设置')}\n"
        result += f"- 性别: {p.get('gender', '未设置')}\n"
        result += f"- 身高: {p.get('height', '未设置')} cm\n"
        result += f"- 体重: {p.get('weight', '未设置')} kg\n"
        result += f"- 体脂率: {p.get('body_fat', '未设置')}%\n"
        result += f"- 体型类型: {p.get('body_type', '未设置')}\n"
        result += f"- 风格偏好: {p.get('style_preference', '未设置')}\n"
        result += f"- 所在城市: {p.get('location', '未设置')}\n"
        result += f"- 职业: {p.get('occupation', '未设置')}\n"
        result += f"- 健身目标: {p.get('fitness_goal', '未设置')}\n"
        result += f"- 饮食偏好: {p.get('diet_preference', '未设置')}\n"
        result += f"- 每日热量摄入目标: {p.get('daily_calorie_intake', '未设置')} kcal\n"
        result += f"- 每日热量消耗目标: {p.get('daily_calorie_burn', '未设置')} kcal"
        
        return result
    except Exception as e:
        return f"查询用户档案失败: {str(e)}"


@tool
def update_user_profile(
    user_id: str,
    name: Optional[str] = None,
    age: Optional[int] = None,
    gender: Optional[str] = None,
    height: Optional[float] = None,
    weight: Optional[float] = None,
    body_fat: Optional[float] = None,
    body_type: Optional[str] = None,
    style_preference: Optional[str] = None,
    location: Optional[str] = None,
    occupation: Optional[str] = None,
    fitness_goal: Optional[str] = None,
    diet_preference: Optional[str] = None,
    daily_calorie_intake: Optional[int] = None,
    daily_calorie_burn: Optional[int] = None,
    metadata_json: Optional[Dict[str, Any]] = None
) -> str:
    """更新用户档案。"""
    ctx = request_context.get() or new_context(method="update_user_profile")
    client = get_supabase_client()
    
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if age is not None:
        update_data["age"] = age
    if gender is not None:
        update_data["gender"] = gender
    if height is not None:
        update_data["height"] = height
    if weight is not None:
        update_data["weight"] = weight
    if body_fat is not None:
        update_data["body_fat"] = body_fat
    if body_type is not None:
        update_data["body_type"] = body_type
    if style_preference is not None:
        update_data["style_preference"] = style_preference
    if location is not None:
        update_data["location"] = location
    if occupation is not None:
        update_data["occupation"] = occupation
    if fitness_goal is not None:
        update_data["fitness_goal"] = fitness_goal
    if diet_preference is not None:
        update_data["diet_preference"] = diet_preference
    if daily_calorie_intake is not None:
        update_data["daily_calorie_intake"] = daily_calorie_intake
    if daily_calorie_burn is not None:
        update_data["daily_calorie_burn"] = daily_calorie_burn
    if metadata_json is not None:
        update_data["metadata"] = json.dumps(metadata_json)
    
    if not update_data:
        return "没有需要更新的数据"
    
    try:
        response = client.table('user_profile').update(update_data).execute()
        items = _parse_response_data(response)
        if items:
            return f"用户档案更新成功！ID: {items[0].get('id', 'unknown')}"
        return "用户档案更新成功"
    except APIError as e:
        raise Exception(f"更新用户档案失败: {e.message}")
