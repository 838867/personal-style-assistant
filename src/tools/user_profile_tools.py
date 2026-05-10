"""用户档案管理工具"""
import json
from typing import Optional
from langchain.tools import tool
from storage.database.supabase_client import get_supabase_client


@tool
def get_user_profile() -> str:
    """获取用户档案信息"""
    try:
        client = get_supabase_client()
        response = client.table("user_profile").select("*").limit(1).execute()
        
        if response.data and len(response.data) > 0:
            profile = response.data[0]
            return json.dumps({
                "success": True,
                "data": {
                    "height": str(profile.get("height", "")),
                    "weight": str(profile.get("weight", "")),
                    "body_type": profile.get("body_type", ""),
                    "skin_tone": profile.get("skin_tone", ""),
                    "style_preference": profile.get("style_preference", ""),
                    "city": profile.get("city", "")
                }
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "success": False,
                "message": "尚未创建用户档案，请先创建"
            }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"查询用户档案失败: {str(e)}"
        }, ensure_ascii=False)


@tool
def update_user_profile(
    height: float,
    weight: float,
    body_type: str,
    skin_tone: str,
    style_preference: str,
    city: str
) -> str:
    """更新用户档案信息

    Args:
        height: 身高(cm)
        weight: 体重(kg)
        body_type: 体型(偏瘦/正常/偏胖/肥胖)
        skin_tone: 肤色(偏白/正常/偏黑)
        style_preference: 风格偏好(简约休闲/商务正装/运动风/时尚潮流)
        city: 所在城市
    """
    try:
        client = get_supabase_client()
        
        # 查询是否已有档案
        existing = client.table("user_profile").select("id").limit(1).execute()
        
        profile_data = {
            "height": height,
            "weight": weight,
            "body_type": body_type,
            "skin_tone": skin_tone,
            "style_preference": style_preference,
            "city": city
        }
        
        if existing.data and len(existing.data) > 0:
            # 更新
            user_id = existing.data[0]["id"]
            response = client.table("user_profile").update(profile_data).eq("id", user_id).execute()
            message = "用户档案已更新"
        else:
            # 创建
            response = client.table("user_profile").insert(profile_data).execute()
            message = "用户档案已创建"
        
        return json.dumps({
            "success": True,
            "message": message,
            "data": profile_data
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"更新用户档案失败: {str(e)}"
        }, ensure_ascii=False)
