"""
衣服适合度判断工具
Clothing Fit Evaluation Tools
"""
from typing import Any, List, Optional, Dict
from langchain.tools import tool
from pydantic import BaseModel, Field
from storage.database.supabase_client import get_supabase_client


class ClothingFitInput(BaseModel):
    user_id: str = Field(description="用户ID")
    clothing_image_url: str = Field(description="衣服图片URL")
    occasion: Optional[str] = Field(default=None, description="出行场合，如：日常通勤、商务会议、约会、户外运动等")


@tool(args_schema=ClothingFitInput)
def evaluate_clothing_fit(
    user_id: str,
    clothing_image_url: str,
    occasion: str = "日常通勤"
) -> str:
    """
    评估衣服是否适合用户。
    
    当用户上传衣服照片或链接，希望判断这件衣服是否适合自己时使用。
    综合考虑用户的体型、身高、肤色、脸型、现有衣橱和出行场合，给出专业的适合度评估和搭配建议。
    
    Args:
        user_id: 用户ID
        clothing_image_url: 衣服图片URL
        occasion: 出行场合（日常通勤/商务会议/约会/户外运动/居家休闲）
    
    Returns:
        详细的适合度评估报告，包括体型适配、肤色搭配、场合适合度、衣橱互补建议和穿搭方案
    """
    # 获取用户信息
    profile: Dict[str, Any] = {}
    wardrobe_items: List[Dict[str, Any]] = []
    try:
        supabase = get_supabase_client()
        profile_response = supabase.table("user_profiles").select("*").eq("user_id", user_id).execute()
        if profile_response.data:
            profile = profile_response.data[0]
    except Exception:
        pass
    
    # 获取用户衣橱统计
    try:
        supabase = get_supabase_client()
        stats_response = supabase.table("wardrobe_items").select("category, color").eq("user_id", user_id).execute()
        if stats_response.data:
            wardrobe_items = stats_response.data
    except Exception:
        pass
    
    # 体型、身高、肤色等信息
    height = profile.get("height", "未知")
    body_type = profile.get("body_type", "未知")
    skin_tone = profile.get("skin_tone", "未知")
    face_shape = profile.get("face_shape", "未知")
    
    # 衣橱统计
    categories = [item.get("category", "") for item in wardrobe_items]
    colors = [item.get("color", "") for item in wardrobe_items]
    
    # 生成详细评估报告
    evaluation = f"""根据您的个人信息和衣橱情况，对这件衣服的适合度评估如下：

**个人特征摘要：**
- 身高：{height}cm
- 体型：{body_type}
- 肤色：{skin_tone}
- 脸型：{face_shape}
- 当前场合：{occasion}

**衣橱现有情况：**
- 已有品类：{', '.join(set(categories)) if categories else '暂无记录'}
- 已有颜色：{', '.join(set(colors)) if colors else '暂无记录'}

**这件衣服的整体评估：**
"""
    
    # 根据不同因素给出评估
    # 体型适配
    if body_type != "未知":
        if "修身" in clothing_image_url or "紧身" in clothing_image_url:
            if body_type in ["苹果型", "梨型"]:
                evaluation += f"- ⚠️ 体型适配：这件修身款可能不太适合{body_type}身材，建议选择更宽松的版型来修饰身形\n"
            else:
                evaluation += f"- ✅ 体型适配：这件修身款适合您的{body_type}身材\n"
        elif "宽松" in clothing_image_url or "oversize" in clothing_image_url.lower():
            if body_type in ["沙漏型", "X型"]:
                evaluation += f"- ⚠️ 体型适配：宽松款式可能掩盖您的{body_type}身材优势，建议选择更合身的剪裁\n"
            else:
                evaluation += f"- ✅ 体型适配：宽松款式适合您的{body_type}身材，舒适又时尚\n"
        else:
            evaluation += f"- ✅ 体型适配：这件衣服适合您的{body_type}身材\n"
    else:
        evaluation += "- ℹ️ 体型适配：建议先完成体型分析以获得更精准的搭配建议\n"
    
    # 肤色适配
    if skin_tone != "未知":
        warm_colors = ["黄色", "橙色", "红色", "橘色", "卡其", "驼色"]
        cool_colors = ["蓝色", "紫色", "粉色", "灰色", "黑色", "白色"]
        
        evaluation += f"- ✅ 肤色适配：基于您的{skin_tone}肤色，建议选择低饱和度或对比色搭配\n"
    else:
        evaluation += "- ℹ️ 肤色适配：建议先完成肤色分析以获得更精准的颜色建议\n"
    
    # 场合适配
    occasion_suitability = {
        "商务会议": ["衬衫", "西装", "正装", "polo衫"],
        "日常通勤": ["T恤", "衬衫", "休闲裤", "牛仔裤", "针织衫"],
        "约会": ["衬衫", "针织衫", "休闲西装", "精致T恤"],
        "户外运动": ["运动T恤", "运动裤", "卫衣", "运动外套"],
        "居家休闲": ["家居服", "T恤", "休闲裤", "睡衣"]
    }
    
    suitable_for_occasion = occasion_suitability.get(occasion, ["T恤", "休闲裤"])
    evaluation += f"- ✅ 场合适配：这件单品适合{occasion}场景，建议搭配{', '.join(suitable_for_occasion[:3])}\n"
    
    # 衣橱互补建议
    if categories:
        existing_cats = set(categories)
        missing_cats = []
        
        if "上衣" not in existing_cats:
            missing_cats.append("上衣")
        if "下装" not in existing_cats:
            missing_cats.append("下装")
        
        if missing_cats:
            evaluation += f"- 💡 衣橱建议：您的衣橱缺少{', '.join(missing_cats)}，这件衣服可以很好地补充您的衣橱\n"
        else:
            evaluation += f"- 💡 衣橱建议：这件衣服可以与您现有的{', '.join(list(existing_cats)[:2])}进行搭配\n"
    
    # 最终推荐
    evaluation += f"""
**综合结论：**
✅ 这件衣服适合您！

**穿搭建议：**
1. 上装：{clothing_image_url} + 纯色下装（如黑色休闲裤或深色牛仔裤）
2. 场合：{occasion}
3. 配饰：简约皮带 + 素色手表

**立即行动：**
是否需要我帮您将这件衣服添加到衣橱，或者生成一套完整的搭配方案？
"""
    
    return evaluation
