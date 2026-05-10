"""体型分析工具 - 通过照片分析体型、脸型、肤色"""
import os
import json
from langchain.tools import tool
from coze_coding_dev_sdk.llm import LLMClient, LLMConfig

# 获取API配置
API_KEY = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
BASE_URL = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
MODEL_NAME = "doubao-seed-1-8-251228"


@tool
def get_body_analysis_from_photo(
    image_url: str,
    question: str = "请分析这个人的体型、脸型和肤色特征"
) -> str:
    """
    从照片分析体型、脸型和肤色。
    
    Args:
        image_url: 用户照片的URL
        question: 分析问题描述
    
    Returns:
        体型、脸型、肤色分析结果
    """
    # 构建分析提示
    analysis_prompt = """你是一个专业的形象顾问。请分析这张照片中人物的身体特征：

1. **体型类型**：判断是苹果型、梨型、沙漏型、矩形型（直筒型）、倒三角型、H型、O型中的哪一种
2. **脸型类型**：判断是圆脸、方脸、长脸、椭圆脸（鹅蛋脸）、心形脸（倒三角）、菱形脸中的哪一种
3. **肤色特征**：判断肤色色调（冷色调/暖色调/中性）和肤色深浅（白皙/自然/小麦/健康/深色）
4. **身材特点**：分析身高视觉感受、体型优劣势、适合的穿搭风格方向

请用JSON格式返回分析结果，包含以下字段：
- body_type: 体型类型
- face_type: 脸型类型
- skin_tone: 肤色深浅描述
- skin_undertone: 肤色色调（冷/暖/中性）
- height_perception: 身高视觉感受
- body_pros: 身材优势列表
- body_cons: 需要注意的问题列表
- style_direction: 适合的风格方向列表"""

    try:
        config = LLMConfig(
            api_key=API_KEY,
            base_url=BASE_URL,
            model=MODEL_NAME
        )
        client = LLMClient(config)
        
        # 使用图片URL作为额外信息
        response = client.invoke(
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": analysis_prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }],
            model=MODEL_NAME,
            max_tokens=2000
        )
        
        # 解析AI响应
        if hasattr(response, 'content'):
            content = response.content
        elif hasattr(response, 'text'):
            content = response.text
        else:
            content = str(response)
        
        # 尝试提取JSON
        try:
            content_str = str(content)
            # 尝试从响应中提取JSON
            if "```json" in content_str:
                start = content_str.find("```json") + 7
                end = content_str.find("```", start)
                result = json.loads(content_str[start:end])
            elif "{" in content_str and "}" in content_str:
                start = content_str.find("{")
                end = content_str.rfind("}") + 1
                result = json.loads(content_str[start:end])
            else:
                result = {"raw_analysis": content_str}
        except:
            result = {"raw_analysis": str(content)}
        
        # 格式化输出
        body_pros = result.get('body_pros', [])
        body_cons = result.get('body_cons', [])
        style_direction = result.get('style_direction', [])
        
        # 确保列表项都是字符串
        if isinstance(body_pros, list):
            body_pros_str = '\n'.join([f"- {str(p)}" for p in body_pros])
        else:
            body_pros_str = str(body_pros)
            
        if isinstance(body_cons, list):
            body_cons_str = '\n'.join([f"- {str(p)}" for p in body_cons])
        else:
            body_cons_str = str(body_cons)
            
        if isinstance(style_direction, list):
            style_str = '\n'.join([f"- {str(s)}" for s in style_direction])
        else:
            style_str = str(style_direction)
        
        return f"""📊 体型分析报告

**体型类型**：{result.get('body_type', '分析中')}
**脸型类型**：{result.get('face_type', '分析中')}
**肤色特征**：{result.get('skin_tone', '分析中')}（{result.get('skin_undertone', '分析中')}）
**身高感受**：{result.get('height_perception', '分析中')}

**身材优势**：
{body_pros_str}

**需要注意**：
{body_cons_str}

**推荐风格**：
{style_str}

---
💡 分析结果仅供参考，如需更精确的判断建议结合实际测量数据。"""
        
    except Exception as e:
        return f"分析失败: {str(e)}"


@tool
def save_body_analysis_to_profile(
    user_id: str,
    body_type: str,
    face_type: str,
    skin_tone: str,
    skin_undertone: str = None,
    height_perception: str = None,
    body_pros: str = None,
    body_cons: str = None,
    style_direction: str = None
) -> str:
    """
    将体型分析结果保存到用户档案。
    
    Args:
        user_id: 用户ID
        body_type: 体型类型
        face_type: 脸型类型
        skin_tone: 肤色描述
        skin_undertone: 肤色色调
        height_perception: 身高视觉感受
        body_pros: 身材优势（JSON字符串格式）
        body_cons: 身材劣势（JSON字符串格式）
        style_direction: 风格方向（JSON字符串格式）
    
    Returns:
        保存结果
    """
    from storage.database.supabase_client import get_supabase_client
    
    supabase = get_supabase_client()
    
    # 解析JSON字段
    pros_list = json.loads(body_pros) if body_pros else []
    cons_list = json.loads(body_cons) if body_cons else []
    style_list = json.loads(style_direction) if style_direction else []
    
    update_data = {
        "body_type": body_type,
        "face_type": face_type,
        "skin_tone": skin_tone,
    }
    
    if skin_undertone:
        update_data["skin_undertone"] = skin_undertone
    if height_perception:
        update_data["height_perception"] = height_perception
    if pros_list:
        update_data["body_pros"] = json.dumps(pros_list)
    if cons_list:
        update_data["body_cons"] = json.dumps(cons_list)
    if style_list:
        update_data["style_direction"] = json.dumps(style_list)
    
    result = supabase.table("user_profiles").update(update_data).eq("user_id", user_id).execute()
    
    if result.data:
        return f"✅ 体型分析结果已保存到用户档案！\n\n保存内容：\n- 体型：{body_type}\n- 脸型：{face_type}\n- 肤色：{skin_tone}\n- 色调：{skin_undertone or '未指定'}"
    else:
        return "❌ 保存失败：未找到用户档案，请先创建用户档案"
