"""
食物仓库管理工具 - 记录用户身边的食物、缺少的食物建议采购
"""
import json
import logging
from typing import Optional
from datetime import datetime
from langchain.tools import tool
from storage.database.supabase_client import get_supabase_client
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context

logger = logging.getLogger(__name__)


@tool
def add_food_to_inventory(
    user_id: str,
    food_name: str,
    category: str,
    calories_per_100g: Optional[float] = None,
    protein_per_100g: Optional[float] = None,
    carbs_per_100g: Optional[float] = None,
    fat_per_100g: Optional[float] = None,
    unit: str = "100g",
    unit_weight: Optional[float] = 100.0,
    in_stock: bool = True,
    purchase_channel: Optional[str] = None,
    notes: Optional[str] = None
) -> str:
    """
    添加食物到食物仓库。
    
    Args:
        user_id: 用户唯一标识（如"小明"）
        food_name: 食物名称（如"鸡胸肉"）
        category: 食物类别（蛋白质/碳水/蔬菜/水果/饮品/调味品/其他）
        calories_per_100g: 每100g热量(kcal)
        protein_per_100g: 每100g蛋白质(g)
        carbs_per_100g: 每100g碳水化合物(g)
        fat_per_100g: 每100g脂肪(g)
        unit: 计量单位（g/个/杯/碗/袋）
        unit_weight: 单位重量(g)
        in_stock: 是否在库存（True=有，False=需要购买）
        purchase_channel: 购买渠道（如"超市/网购/菜市场"）
        notes: 备注
    
    Returns:
        添加结果
    
    Example:
        >>> add_food_to_inventory("小明", "鸡胸肉", "蛋白质", calories_per_100g=133, protein_per_100g=31, in_stock=True)
    """
    ctx = request_context.get() or new_context(method="add_food_to_inventory")
    
    try:
        client = get_supabase_client()
        
        # 检查是否已存在
        existing = client.table("food_inventory").select("id").eq("user_id", user_id).eq("food_name", food_name).execute()
        
        if existing.data:
            return f"食物【{food_name}】已在仓库中，请使用update_food_inventory更新数量。"
        
        # 插入新记录
        data = {
            "user_id": user_id,
            "food_name": food_name,
            "category": category,
            "calories_per_100g": calories_per_100g,
            "protein_per_100g": protein_per_100g,
            "carbs_per_100g": carbs_per_100g,
            "fat_per_100g": fat_per_100g,
            "unit": unit,
            "unit_weight": unit_weight,
            "in_stock": in_stock,
            "purchase_channel": purchase_channel,
            "notes": notes
        }
        
        response = client.table("food_inventory").insert(data).execute()
        
        if response.data:
            item: dict = response.data[0]  # type: ignore
            item_id = item.get("id")
            stock_status = "✅ 在库存" if in_stock else "❌ 需要购买"
            return f"食物【{food_name}】已添加到仓库！\n- ID: {item_id}\n- 类别: {category}\n- 状态: {stock_status}"
        else:
            return "添加失败，请重试。"
        
    except Exception as e:
        logger.error(f"Error adding food to inventory: {e}")
        return f"添加失败: {str(e)}"


@tool
def get_food_inventory(
    user_id: str,
    category: Optional[str] = None,
    in_stock_only: bool = False
) -> str:
    """
    查询用户的食物仓库。
    
    Args:
        user_id: 用户唯一标识
        category: 可选，按类别筛选（蛋白质/碳水/蔬菜/水果/饮品/调味品/其他）
        in_stock_only: 只显示在库存的食物
    
    Returns:
        食物仓库列表
    
    Example:
        >>> get_food_inventory("小明", category="蛋白质")
    """
    ctx = request_context.get() or new_context(method="get_food_inventory")
    
    try:
        client = get_supabase_client()
        
        query = client.table("food_inventory").select("*").eq("user_id", user_id)
        
        if category:
            query = query.eq("category", category)
        
        if in_stock_only:
            query = query.eq("in_stock", True)
        
        response = query.order("category").order("food_name").execute()
        
        if not response.data:
            return "食物仓库为空，请先添加食物。"
        
        # 按类别分组
        categories = {}
        for item in response.data:  # type: ignore[union-attr]
            item_dict: dict = item  # type: ignore[assignment]
            cat = item_dict.get("category", "其他")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)
        
        output = "## 🏪 食物仓库\n\n"
        
        for cat, items in categories.items():
            cat_emoji = {
                "蛋白质": "🥩",
                "碳水": "🍚",
                "蔬菜": "🥬",
                "水果": "🍎",
                "饮品": "🥤",
                "调味品": "🧂",
                "其他": "📦"
            }.get(cat, "📦")
            
            output += f"### {cat_emoji} {cat}（{len(items)}种）\n\n"
            
            for item in items:
                stock_icon = "✅" if item.get("in_stock") else "❌"
                cal = item.get("calories_per_100g", "?")
                pro = item.get("protein_per_100g", "?")
                
                output += f"- {stock_icon} **{item.get('food_name')}**"
                if cal:
                    output += f" | 🔥{cal}kcal"
                if pro:
                    output += f" | 💪{pro}g蛋白"
                output += "\n"
            
            output += "\n"
        
        # 统计
        data: list = response.data  # type: ignore
        total_items = len(data)
        in_stock_count = sum(1 for item in data if item.get("in_stock"))
        need_buy_count = total_items - in_stock_count
        
        output += f"**总计**: {total_items}种食物\n"
        output += f"- ✅ 在库存: {in_stock_count}种\n"
        output += f"- ❌ 需要购买: {need_buy_count}种\n"
        
        return output.strip()
        
    except Exception as e:
        logger.error(f"Error getting food inventory: {e}")
        return f"查询失败: {str(e)}"


@tool
def update_food_inventory_item(
    user_id: str,
    food_name: str,
    in_stock: Optional[bool] = None,
    unit_weight: Optional[float] = None,
    purchase_channel: Optional[str] = None,
    notes: Optional[str] = None
) -> str:
    """
    更新食物仓库中的物品状态。
    
    Args:
        user_id: 用户唯一标识
        food_name: 食物名称
        in_stock: 是否在库存（True=有，False=需要购买）
        unit_weight: 单位重量更新
        purchase_channel: 购买渠道更新
        notes: 备注更新
    
    Returns:
        更新结果
    
    Example:
        >>> update_food_inventory_item("小明", "鸡胸肉", in_stock=False)
    """
    ctx = request_context.get() or new_context(method="update_food_inventory_item")
    
    try:
        client = get_supabase_client()
        
        # 查找食物
        existing: list = client.table("food_inventory").select("id, food_name").eq("user_id", user_id).eq("food_name", food_name).execute()  # type: ignore
        
        if not existing:
            return f"未找到食物【{food_name}】，请先添加到仓库。"
        
        item_id = existing[0].get("id")
        
        # 构建更新数据
        update_data = {}
        if in_stock is not None:
            update_data["in_stock"] = in_stock
        if unit_weight is not None:
            update_data["unit_weight"] = unit_weight
        if purchase_channel is not None:
            update_data["purchase_channel"] = purchase_channel
        if notes is not None:
            update_data["notes"] = notes
        
        if not update_data:
            return "没有需要更新的字段。"
        
        response: list = client.table("food_inventory").update(update_data).eq("id", item_id).execute()  # type: ignore
        
        if response:
            stock_status = "已入库" if in_stock else "已标记为需要购买"
            return f"食物【{food_name}】{stock_status}，更新成功！"
        else:
            return "更新失败，请重试。"
        
    except Exception as e:
        logger.error(f"Error updating food inventory: {e}")
        return f"更新失败: {str(e)}"


@tool
def get_shopping_suggestions(
    user_id: str,
    nutrition_goal: Optional[str] = None,
    diet_plan_id: Optional[int] = None
) -> str:
    """
    根据饮食目标和现有食物，推荐需要购买的食物。
    
    Args:
        user_id: 用户唯一标识
        nutrition_goal: 营养目标描述（如"高蛋白低碳水"）
        diet_plan_id: 可选，关联的饮食计划ID
    
    Returns:
        购物建议列表
    
    Example:
        >>> get_shopping_suggestions("小明", nutrition_goal="高蛋白低碳水")
    """
    ctx = request_context.get() or new_context(method="get_shopping_suggestions")
    
    try:
        client = get_supabase_client()
        
        # 获取现有食物
        existing: list = client.table("food_inventory").select("*").eq("user_id", user_id).execute()  # type: ignore
        existing_foods = {item.get("food_name"): item for item in existing}
        
        # 获取饮食计划中的目标食物（如果有）
        target_foods = []
        if diet_plan_id:
            plan_response: list = client.table("diet_plans").select("target_foods").eq("id", diet_plan_id).execute()  # type: ignore
            if plan_response and len(plan_response) > 0:
                first_plan = plan_response[0]
                if isinstance(first_plan, dict) and first_plan.get("target_foods"):
                    target_foods = first_plan.get("target_foods", [])
        
        # 常见健康食物推荐列表
        recommended_foods = {
            "蛋白质": [
                {"name": "鸡胸肉", "calories": 133, "protein": 31, "channel": "超市/菜市场"},
                {"name": "三文鱼", "calories": 208, "protein": 20, "channel": "超市/海鲜市场"},
                {"name": "鸡蛋", "calories": 155, "protein": 13, "channel": "超市/便利店"},
                {"name": "豆腐", "calories": 81, "protein": 8, "channel": "超市/菜市场"},
                {"name": "虾", "calories": 99, "protein": 24, "channel": "超市/海鲜市场"},
                {"name": "牛肉", "calories": 250, "protein": 26, "channel": "超市/菜市场"},
            ],
            "碳水": [
                {"name": "糙米", "calories": 111, "carbs": 23, "channel": "超市"},
                {"name": "燕麦", "calories": 68, "carbs": 12, "channel": "超市"},
                {"name": "红薯", "calories": 86, "carbs": 20, "channel": "菜市场/超市"},
                {"name": "全麦面包", "calories": 247, "carbs": 41, "channel": "超市/面包店"},
                {"name": "藜麦", "calories": 120, "carbs": 21, "channel": "超市/网购"},
            ],
            "蔬菜": [
                {"name": "西兰花", "calories": 34, "fiber": 2.6, "channel": "菜市场/超市"},
                {"name": "菠菜", "calories": 23, "fiber": 2.2, "channel": "菜市场/超市"},
                {"name": "胡萝卜", "calories": 41, "fiber": 2.8, "channel": "菜市场/超市"},
                {"name": "番茄", "calories": 18, "fiber": 1.2, "channel": "菜市场/超市"},
                {"name": "黄瓜", "calories": 15, "fiber": 0.5, "channel": "菜市场/超市"},
            ],
            "水果": [
                {"name": "香蕉", "calories": 89, "carbs": 23, "channel": "水果店/超市"},
                {"name": "苹果", "calories": 52, "carbs": 14, "channel": "水果店/超市"},
                {"name": "蓝莓", "calories": 57, "carbs": 14, "channel": "超市/网购"},
                {"name": "牛油果", "calories": 160, "fat": 15, "channel": "超市/水果店"},
            ]
        }
        
        # 找出缺少的食物
        suggestions = {"需要购买": [], "建议补充": []}
        
        for category, foods in recommended_foods.items():
            has_in_stock = any(
                existing_foods.get(f.get("name")) and existing_foods.get(f.get("name")).get("in_stock")  # type: ignore
                for f in foods
            )
            
            if not has_in_stock:
                # 找出库存中没有的食物
                for food in foods:
                    if food.get("name") not in existing_foods:
                        suggestions["需要购买"].append({**food, "category": category})
                    elif not existing_foods.get(food.get("name")).get("in_stock"):  # type: ignore
                        suggestions["建议补充"].append({**food, "category": category})
        
        # 格式化输出
        output = "## 🛒 购物建议\n\n"
        
        if nutrition_goal:
            output += f"**营养目标**: {nutrition_goal}\n\n"
        
        if suggestions["需要购买"]:
            output += "### 🔴 推荐购买\n\n"
            for item in suggestions["需要购买"][:8]:  # 限制数量
                cat_emoji = {"蛋白质": "🥩", "碳水": "🍚", "蔬菜": "🥬", "水果": "🍎"}.get(item["category"], "📦")
                output += f"- {cat_emoji} **{item['name']}** ({item['category']})\n"
                output += f"  - 热量: {item.get('calories', '?')}kcal/100g"
                if item.get("protein"):
                    output += f" | 蛋白: {item.get('protein')}g"
                if item.get("carbs"):
                    output += f" | 碳水: {item.get('carbs')}g"
                output += f"\n  - 购买渠道: {item.get('channel', '未知')}\n\n"
        
        if suggestions["建议补充"]:
            output += "### 🟡 库存不足，建议补充\n\n"
            for item in suggestions["建议补充"][:5]:
                cat_emoji = {"蛋白质": "🥩", "碳水": "🍚", "蔬菜": "🥬", "水果": "🍎"}.get(item["category"], "📦")
                output += f"- {cat_emoji} **{item['name']}** - {item.get('channel', '未知')}\n"
        
        if not suggestions["需要购买"] and not suggestions["建议补充"]:
            output += "🎉 您的食物仓库已经很完善了！\n"
        
        return output.strip()
        
    except Exception as e:
        logger.error(f"Error getting shopping suggestions: {e}")
        return f"获取建议失败: {str(e)}"


@tool
def delete_food_from_inventory(
    user_id: str,
    food_name: str
) -> str:
    """
    从食物仓库删除食物。
    
    Args:
        user_id: 用户唯一标识
        food_name: 食物名称
    
    Returns:
        删除结果
    
    Example:
        >>> delete_food_from_inventory("小明", "过期食品")
    """
    ctx = request_context.get() or new_context(method="delete_food_from_inventory")
    
    try:
        client = get_supabase_client()
        
        response = client.table("food_inventory").delete().eq("user_id", user_id).eq("food_name", food_name).execute()
        
        if response.data:
            return f"食物【{food_name}】已从仓库中删除。"
        else:
            return f"未找到食物【{food_name}】，请检查名称是否正确。"
        
    except Exception as e:
        logger.error(f"Error deleting food from inventory: {e}")
        return f"删除失败: {str(e)}"
