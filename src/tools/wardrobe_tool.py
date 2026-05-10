"""衣橱管理工具"""

from typing import Any, Dict
from langchain.tools import tool
from postgrest.exceptions import APIError
from storage.database.supabase_client import get_supabase_client
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context


@tool
def add_clothing(
    category: str,
    color: str,
    style: str,
    season: str,
    occasion: str,
    description: str = ""
) -> str:
    """
    添加衣物到衣橱

    Args:
        category: 衣物类型（上衣/裤子/外套/鞋子/配饰/连衣裙/衬衫等）
        color: 颜色（如：白色、黑色、灰色、蓝色等）
        style: 风格（如：简约、休闲、商务、复古、运动等）
        season: 适合季节（春夏秋冬/四季）
        occasion: 适合场合（上班/约会/休闲/正式/运动等）
        description: 详细描述（可选）

    Returns:
        str: 添加结果提示
    """
    ctx = request_context.get() or new_context(method="add_clothing")
    try:
        client = get_supabase_client()
        client.table('wardrobe').insert({
            'category': category,
            'color': color,
            'style': style,
            'season': season,
            'occasion': occasion,
            'description': description
        }).execute()

        return f"✓ 已添加衣物：{color}{category}（{style}，适合{season}，{occasion}）"
    except APIError as e:
        raise Exception(f"添加衣物失败: {e.message}")


@tool
def query_wardrobe(
    category: str = "",
    color: str = "",
    season: str = "",
    occasion: str = ""
) -> str:
    """
    查询衣橱中的衣物

    Args:
        category: 衣物类型（可选，如：上衣、裤子、外套等）
        color: 颜色（可选，如：白色、黑色等）
        season: 季节（可选，如：春夏秋冬、四季）
        occasion: 场合（可选，如：上班、休闲等）

    Returns:
        str: 衣物列表的 JSON 字符串
    """
    ctx = request_context.get() or new_context(method="query_wardrobe")
    try:
        client = get_supabase_client()
        query = client.table('wardrobe').select('*')

        # 根据参数添加过滤条件
        if category:
            query = query.eq('category', category)
        if color:
            query = query.eq('color', color)
        if season:
            query = query.eq('season', season)
        if occasion:
            query = query.eq('occasion', occasion)

        response = query.order('created_at', desc=True).execute()

        if not response.data:
            return "未找到符合条件的衣物"

        # 格式化输出
        result = []
        for item in response.data:
            if not isinstance(item, dict):
                continue
            desc = f"{item.get('color', '')}{item.get('category', '')}（{item.get('style', '')}，{item.get('season', '')}，{item.get('occasion', '')}）"
            if item.get('description'):
                desc += f"\n  {item.get('description')}"
            result.append(desc)

        return f"衣橱中的衣物（共 {len(result)} 件）：\n" + "\n".join([f"- {item}" for item in result])
    except APIError as e:
        raise Exception(f"查询衣橱失败: {e.message}")
