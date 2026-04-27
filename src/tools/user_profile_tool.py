"""用户档案管理工具"""

from typing import Any, Dict
from langchain.tools import tool
from postgrest.exceptions import APIError
from storage.database.supabase_client import get_supabase_client
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context


@tool
def get_user_profile() -> str:
    """
    获取用户当前档案信息

    Returns:
        str: 用户档案的 JSON 字符串，包含身高、体重、体型、肤色、风格偏好、所在城市等信息
    """
    ctx = request_context.get() or new_context(method="get_user_profile")
    try:
        client = get_supabase_client()
        response = client.table('user_profile').select('*').order('id', desc=True).limit(1).execute()

        if not response.data:
            return "未找到用户档案，请先使用 update_user_profile 创建档案"

        profile = response.data[0]
        if not isinstance(profile, dict):
            return "数据格式错误"

        return f"""
用户档案：
- 身高：{profile.get('height', '未知')} cm
- 体重：{profile.get('weight', '未知')} kg
- 体脂率：{profile.get('body_fat_rate', '未知')}%
- 体型：{profile.get('body_type', '未知')}
- 肤色：{profile.get('skin_tone', '未知')}
- 风格偏好：{profile.get('style_preference', '未知')}
- 所在城市：{profile.get('city', '未知')}
- 更新时间：{profile.get('updated_at', '未知')}
"""
    except APIError as e:
        raise Exception(f"查询用户档案失败: {e.message}")


@tool
def update_user_profile(
    height: float,
    weight: float,
    body_type: str,
    skin_tone: str,
    style_preference: str,
    city: str,
    body_fat_rate: float = 0
) -> str:
    """
    更新用户档案信息

    Args:
        height: 身高（厘米）
        weight: 体重（公斤）
        body_type: 体型（如：梨形身材、苹果型身材、沙漏型身材等）
        skin_tone: 肤色（如：暖色调、冷色调、中性色）
        style_preference: 风格偏好（如：休闲商务风、简约风、复古风等）
        city: 所在城市（如：江苏省扬州市）
        body_fat_rate: 体脂率（%），可选

    Returns:
        str: 更新结果提示
    """
    ctx = request_context.get() or new_context(method="update_user_profile")
    try:
        client = get_supabase_client()

        # 查询是否已有档案
        existing = client.table('user_profile').select('id').execute()

        update_data = {
            'height': height,
            'weight': weight,
            'body_type': body_type,
            'skin_tone': skin_tone,
            'style_preference': style_preference,
            'city': city
        }

        # 如果提供了体脂率，则添加到更新数据中
        if body_fat_rate > 0:
            update_data['body_fat_rate'] = body_fat_rate

        if existing.data:
            # 更新已有档案（取最新的一条）
            last_item = existing.data[-1]
            profile_id = last_item['id'] if isinstance(last_item, dict) else None
            if profile_id:
                client.table('user_profile').update(update_data).eq('id', profile_id).execute()
                fat_str = f"，体脂率{body_fat_rate}%" if body_fat_rate > 0 else ""
                return f"✓ 用户档案已更新：身高 {height}cm，体重 {weight}kg，体型 {body_type}{fat_str}"
        else:
            # 创建新档案
            client.table('user_profile').insert(update_data).execute()
            fat_str = f"，体脂率{body_fat_rate}%" if body_fat_rate > 0 else ""
            return f"✓ 用户档案已创建：身高 {height}cm，体重 {weight}kg，体型 {body_type}{fat_str}"

    except APIError as e:
        raise Exception(f"更新用户档案失败: {e.message}")
