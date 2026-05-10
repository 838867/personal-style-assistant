"""用户档案管理工具"""
from typing import Optional, Dict, Any
from langchain.tools import tool
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context
from storage.database.supabase_client import get_supabase_client


@tool
def get_user_profile() -> str:
    """获取用户档案。返回用户的个人信息和体型数据。"""
    ctx = request_context.get() or new_context(method="get_user_profile")
    client = get_supabase_client()
    
    try:
        response = client.table("user_profile").select("*").limit(1).execute()
        data = response.json()
        
        if not data or not data.get("data"):
            return "未找到用户档案。请先创建用户档案。"
        
        user = data["data"][0]
        
        result = f"""用户档案信息：
- 身高: {user.get('height', '未知')} cm
- 体重: {user.get('weight', '未知')} kg
- 体脂率: {user.get('body_fat_rate', '未知')}%
- 体型: {user.get('body_type', '未知')}
- 肤色: {user.get('skin_tone', '未知')}
- 风格偏好: {user.get('style_preference', '未知')}
- 城市: {user.get('city', '未知')}
- 创建时间: {user.get('created_at', '未知')}"""
        
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
        existing_data = existing.json()
        
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
        
        if existing_data and existing_data.get("data"):
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
