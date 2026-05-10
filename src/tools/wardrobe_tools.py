"""
衣橱管理工具
Wardrobe Management Tools
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
def add_wardrobe_item(
    user_id: str,
    item_name: str,
    category: str,
    color: Optional[str] = None,
    brand: Optional[str] = None,
    season: Optional[str] = None,
    style: Optional[str] = None,
    occasion: Optional[str] = None,
    purchase_date: Optional[str] = None,
    price: Optional[float] = None,
    notes: Optional[str] = None
) -> str:
    """添加衣橱物品。"""
    ctx = request_context.get() or new_context(method="add_wardrobe_item")
    client = get_supabase_client()
    
    data = {
        "user_id": user_id,
        "item_name": item_name,
        "category": category,
        "color": color,
        "brand": brand,
        "season": season,
        "style": style,
        "occasion": occasion,
        "purchase_date": purchase_date,
        "price": price,
        "notes": notes
    }
    
    data = {k: v for k, v in data.items() if v is not None}
    
    try:
        response = client.table('wardrobe').insert(data).execute()
        items = _parse_response_data(response)
        if items:
            return f"衣橱物品添加成功！ID: {items[0].get('id', 'unknown')}"
        return "衣橱物品添加成功"
    except APIError as e:
        raise Exception(f"添加衣橱物品失败: {e.message}")


@tool
def query_wardrobe(
    user_id: str,
    category: Optional[str] = None,
    color: Optional[str] = None,
    season: Optional[str] = None,
    style: Optional[str] = None,
    occasion: Optional[str] = None,
    limit: int = 50
) -> str:
    """查询衣橱物品。"""
    ctx = request_context.get() or new_context(method="query_wardrobe")
    client = get_supabase_client()
    
    try:
        query = client.table('wardrobe').select('*')
        
        if category:
            query = query.eq('category', category)
        if color:
            query = query.eq('color', color)
        if season:
            query = query.eq('season', season)
        if style:
            query = query.eq('style', style)
        if occasion:
            query = query.eq('occasion', occasion)
        
        response = query.limit(limit).execute()
        items = _parse_response_data(response)
        
        if not items:
            return "衣橱中没有任何物品"
        
        result = f"衣橱物品列表（共 {len(items)} 件）：\n"
        
        for idx, item in enumerate(items, 1):
            if isinstance(item, dict):
                result += f"\n{idx}. {item.get('item_name', '未知')}\n"
                result += f"   类别: {item.get('category', '未分类')}\n"
                result += f"   颜色: {item.get('color', '未设置')}\n"
                result += f"   品牌: {item.get('brand', '未设置')}\n"
                result += f"   季节: {item.get('season', '未设置')}\n"
                result += f"   风格: {item.get('style', '未设置')}\n"
                result += f"   场合: {item.get('occasion', '未设置')}\n"
        
        return result
    except Exception as e:
        return f"查询衣橱物品失败: {str(e)}"


@tool
def update_wardrobe_item(
    item_id: int,
    user_id: str,
    item_name: Optional[str] = None,
    category: Optional[str] = None,
    color: Optional[str] = None,
    brand: Optional[str] = None,
    season: Optional[str] = None,
    style: Optional[str] = None,
    occasion: Optional[str] = None,
    purchase_date: Optional[str] = None,
    price: Optional[float] = None,
    notes: Optional[str] = None,
    is_active: Optional[bool] = None
) -> str:
    """更新衣橱物品。"""
    ctx = request_context.get() or new_context(method="update_wardrobe_item")
    client = get_supabase_client()
    
    update_data = {}
    if item_name is not None:
        update_data["item_name"] = item_name
    if category is not None:
        update_data["category"] = category
    if color is not None:
        update_data["color"] = color
    if brand is not None:
        update_data["brand"] = brand
    if season is not None:
        update_data["season"] = season
    if style is not None:
        update_data["style"] = style
    if occasion is not None:
        update_data["occasion"] = occasion
    if purchase_date is not None:
        update_data["purchase_date"] = purchase_date
    if price is not None:
        update_data["price"] = price
    if notes is not None:
        update_data["notes"] = notes
    if is_active is not None:
        update_data["is_active"] = is_active
    
    if not update_data:
        return "没有需要更新的数据"
    
    try:
        response = client.table('wardrobe').update(update_data).eq('id', item_id).execute()
        items = _parse_response_data(response)
        if items:
            return f"衣橱物品更新成功！ID: {items[0].get('id', 'unknown')}"
        return "衣橱物品更新成功"
    except APIError as e:
        raise Exception(f"更新衣橱物品失败: {e.message}")


@tool
def record_item_wear(
    item_id: int,
    user_id: str,
    wear_date: Optional[str] = None,
    occasion: Optional[str] = None,
    notes: Optional[str] = None
) -> str:
    """记录物品穿着。"""
    ctx = request_context.get() or new_context(method="record_item_wear")
    client = get_supabase_client()
    
    try:
        item_response = client.table('wardrobe').select('wear_count').eq('id', item_id).maybe_single().execute()
        items = _parse_response_data(item_response)
        current_count = 0
        if items:
            current_count = items[0].get('wear_count', 0) or 0
        
        update_data = {
            "wear_count": current_count + 1,
            "last_worn": wear_date
        }
        
        client.table('wardrobe').update(update_data).eq('id', item_id).execute()
        
        return f"穿着记录成功！物品 {item_id} 今日已穿着"
    except APIError as e:
        raise Exception(f"记录穿着失败: {e.message}")
