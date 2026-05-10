"""用户档案管理工具 - 使用原生requests调用Supabase REST API"""
import json
import os
import requests
from langchain.tools import tool


def get_supabase_headers():
    """获取Supabase请求头"""
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_ANON_KEY", "")
    
    if not supabase_url or not supabase_key:
        # 尝试扣子平台的内置环境变量
        supabase_url = os.getenv("COZE_SUPABASE_URL", supabase_url)
        supabase_key = os.getenv("COZE_SUPABASE_ANON_KEY", supabase_key)
    
    return {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}"
    }


def get_supabase_url():
    """获取Supabase URL"""
    supabase_url = os.getenv("SUPABASE_URL", "")
    if not supabase_url:
        supabase_url = os.getenv("COZE_SUPABASE_URL", "")
    return supabase_url


@tool
def get_user_profile() -> str:
    """获取用户档案信息"""
    try:
        headers = get_supabase_headers()
        base_url = get_supabase_url()
        
        if not base_url:
            return json.dumps({
                "success": False,
                "message": "数据库未配置"
            }, ensure_ascii=False)
        
        response = requests.get(
            f"{base_url}/rest/v1/user_profile",
            headers=headers,
            params={"select": "*", "limit": 1}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                profile = data[0]
                return json.dumps({
                    "success": True,
                    "data": {
                        "height": profile.get("height", ""),
                        "weight": profile.get("weight", ""),
                        "body_type": profile.get("body_type", ""),
                        "skin_tone": profile.get("skin_tone", ""),
                        "style_preference": profile.get("style_preference", ""),
                        "city": profile.get("city", "")
                    }
                }, ensure_ascii=False)
        
        return json.dumps({
            "success": False,
            "message": "尚未创建用户档案"
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
        style_preference: 风格偏好
        city: 所在城市
    """
    try:
        headers = get_supabase_headers()
        base_url = get_supabase_url()
        
        if not base_url:
            return json.dumps({
                "success": False,
                "message": "数据库未配置"
            }, ensure_ascii=False)
        
        # 查询是否已有档案
        response = requests.get(
            f"{base_url}/rest/v1/user_profile",
            headers=headers,
            params={"select": "id", "limit": 1}
        )
        
        profile_data = {
            "height": height,
            "weight": weight,
            "body_type": body_type,
            "skin_tone": skin_tone,
            "style_preference": style_preference,
            "city": city
        }
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                # 更新
                user_id = data[0]["id"]
                update_response = requests.patch(
                    f"{base_url}/rest/v1/user_profile?id=eq.{user_id}",
                    headers={**headers, "Prefer": "return=minimal"},
                    json=profile_data
                )
                if update_response.status_code in [200, 204]:
                    return json.dumps({
                        "success": True,
                        "message": "用户档案已更新",
                        "data": profile_data
                    }, ensure_ascii=False)
            else:
                # 创建
                create_response = requests.post(
                    f"{base_url}/rest/v1/user_profile",
                    headers={**headers, "Prefer": "return=minimal"},
                    json=profile_data
                )
                if create_response.status_code in [200, 201, 204]:
                    return json.dumps({
                        "success": True,
                        "message": "用户档案已创建",
                        "data": profile_data
                    }, ensure_ascii=False)
        
        return json.dumps({
            "success": False,
            "message": "保存失败"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"更新用户档案失败: {str(e)}"
        }, ensure_ascii=False)
