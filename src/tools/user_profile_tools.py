"""用户档案管理工具"""
import json
from typing import Optional, Dict, Any, List
from langchain.tools import tool
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context
from storage.database.supabase_client import get_supabase_client


def safe_get(data: Any, key: str, default: str = "未知") -> str:
    """安全获取字典值"""
    if isinstance(data, dict):
        value = data.get(key)
        if value is not None:
            return str(value)
    return default


@tool
def get_user_profile() -> str:
    """获取用户档案。返回用户的个人信息和体型数据。"""
    ctx = request_context.get() or new_context(method="get_user_profile")
    client = get_supabase_client()
    
    try:
        response = client.table("user_profile").select("*").limit(1).execute()
        raw_data = response.json()
        
        # 解析 JSON 字符串
        if isinstance(raw_data, str):
            data = json.loads(raw_data)
        else:
            data = raw_data
        
        if not data or not data.get("data"):
            return "未找到用户档案。请先创建用户档案。"
        
        user = data["data"][0]
        
        result = f"""用户档案信息：
- 身高: {safe_get(user, 'height')} cm
- 体重: {safe_get(user, 'weight')} kg
- 体脂率: {safe_get(user, 'body_fat_rate')}%
- 体型: {safe_get(user, 'body_type')}
- 肤色: {safe_get(user, 'skin_tone')}
- 风格偏好: {safe_get(user, 'style_preference')}
- 城市: {safe_get(user, 'city')}
- 创建时间: {safe_get(user, 'created_at')}"""
        
        return result
        
    except Exception as e:
        return f"查询用户档案失败: {str(e)}"


@tool
def create_or_update_user_profile(
    height: Optional[float] = None,
    weight: Optional[float] = None,
    body_fat_rate: Optional[float] = None,
    body_type: Optional[str] = None,
    skin_tone: Optional[str] = None,
    style_preference: Optional[str] = None,
    city: Optional[str] = None
) -> str:
    """创建或更新用户档案。如果已有档案则更新，否则创建新的。"""
    ctx = request_context.get() or new_context(method="create_or_update_user_profile")
    client = get_supabase_client()
    
    try:
        # 检查是否已有档案
        existing = client.table("user_profile").select("id").limit(1).execute()
        existing_raw = existing.json()
        
        # 解析 JSON 字符串
        if isinstance(existing_raw, str):
            existing_data = json.loads(existing_raw)
        else:
            existing_data = existing_raw
        
        data: Dict[str, Any] = {}
        if height is not None:
            data["height"] = height
        if weight is not None:
            data["weight"] = weight
        if body_fat_rate is not None:
            data["body_fat_rate"] = body_fat_rate
        if body_type is not None:
            data["body_type"] = body_type
        if skin_tone is not None:
            data["skin_tone"] = skin_tone
        if style_preference is not None:
            data["style_preference"] = style_preference
        if city is not None:
            data["city"] = city
        
        if not data:
            return "请提供至少一个要更新的字段。"
        
        if existing_data and existing_data.get("data") and len(existing_data["data"]) > 0:
            # 更新现有档案
            record_id = existing_data["data"][0]["id"]
            client.table("user_profile").update(data).eq("id", record_id).execute()
            return f"用户档案已更新！\n\n更新内容：\n" + "\n".join([f"- {k}: {v}" for k, v in data.items()])
        else:
            # 创建新档案
            client.table("user_profile").insert(data).execute()
            return f"用户档案已创建！\n\n基本信息：\n" + "\n".join([f"- {k}: {v}" for k, v in data.items()])
        
    except Exception as e:
        return f"更新用户档案失败: {str(e)}"
