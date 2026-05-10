"""
天气查询工具
Weather Query Tool
"""
from langchain.tools import tool
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context

@tool
def get_weather(city: str) -> str:
    """
    查询实时天气信息。
    
    Args:
        city: 城市名称（必填），例如"北京"、"上海"、"深圳"
    
    Returns:
        天气信息，包含温度、湿度、风力、穿衣建议等
    """
    ctx = new_context(method="get_weather")
    client = SearchClient(ctx=ctx)
    
    try:
        # 搜索天气信息
        query = f"{city}今天天气温度湿度空气质量"
        response = client.web_search_with_summary(query=query, count=3)
        
        if not response.web_items:
            return f"抱歉，暂时无法获取 {city} 的天气信息"
        
        # 提取搜索结果中的天气信息
        weather_info = []
        for item in response.web_items:
            if item.summary:
                weather_info.append(item.summary)
            elif item.snippet:
                weather_info.append(item.snippet)
        
        if not weather_info:
            return f"抱歉，暂时无法获取 {city} 的详细天气信息"
        
        result = f"🌤️ {city} 今日天气\n\n"
        result += weather_info[0]
        
        # 添加穿搭建议
        result += "\n\n👔 穿搭建议："
        
        # 根据天气信息判断穿搭
        summary_lower = weather_info[0].lower()
        
        if '雨' in summary_lower or '雪' in summary_lower:
            result += "\n- 建议带伞或穿防水外套"
            result += "\n- 鞋子选择防滑款式"
        if '热' in summary_lower or '高温' in summary_lower or '30' in summary_lower:
            result += "\n- 建议穿透气轻薄衣物"
            result += "\n- 做好防晒措施"
        if '冷' in summary_lower or '降温' in summary_lower or '10' in summary_lower:
            result += "\n- 建议穿保暖外套"
            result += "\n- 可以叠穿保暖衣物"
        if '风' in summary_lower:
            result += "\n- 建议穿防风外套"
        
        return result
        
    except Exception as e:
        return f"查询天气时出错: {str(e)}"


@tool
def get_weather_forecast(city: str, days: int = 3) -> str:
    """
    查询未来天气预报。
    
    Args:
        city: 城市名称（必填），例如"北京"、"上海"
        days: 预报天数（默认3天），可选1-7
    
    Returns:
        未来天气预报
    """
    ctx = new_context(method="get_weather_forecast")
    client = SearchClient(ctx=ctx)
    
    try:
        # 搜索天气预报
        query = f"{city}未来{days}天天气预报"
        response = client.web_search_with_summary(query=query, count=3)
        
        if not response.web_items:
            return f"抱歉，暂时无法获取 {city} 的天气预报"
        
        # 提取搜索结果
        forecast_info = []
        for item in response.web_items:
            if item.summary:
                forecast_info.append(item.summary)
            elif item.snippet:
                forecast_info.append(item.snippet)
        
        if not forecast_info:
            return f"抱歉，暂时无法获取 {city} 的详细天气预报"
        
        result = f"📅 {city} 未来{days}天天气预报\n\n"
        result += forecast_info[0]
        
        return result
        
    except Exception as e:
        return f"查询天气预报时出错: {str(e)}"


@tool
def get_weather_outfit_suggestion(city: str) -> str:
    """
    根据天气给出穿搭建议。
    
    Args:
        city: 城市名称（必填）
    
    Returns:
        详细的穿搭建议
    """
    ctx = new_context(method="get_weather_outfit_suggestion")
    client = SearchClient(ctx=ctx)
    
    try:
        # 获取当前天气
        query = f"{city}今天天气温度湿度"
        response = client.web_search_with_summary(query=query, count=3)
        
        if not response.web_items:
            return f"抱歉，暂时无法获取 {city} 的天气信息来给出穿搭建议"
        
        weather_info = ""
        for item in response.web_items:
            if item.summary:
                weather_info = item.summary
                break
            elif item.snippet:
                weather_info = item.snippet
                break
        
        if not weather_info:
            return f"抱歉，暂时无法获取 {city} 的详细天气信息"
        
        result = f"👗 {city} 今日穿搭建议\n\n"
        result += f"当前天气：{weather_info}\n\n"
        
        # 根据天气信息生成穿搭建议
        weather_lower = weather_info.lower()
        
        # 温度判断
        temp_suggestion = ""
        if '雨' in weather_lower or '雪' in weather_lower:
            temp_suggestion = "🌧️ 雨天穿搭：\n"
            temp_suggestion += "- 上装：防水外套或冲锋衣 + 长袖T恤\n"
            temp_suggestion += "- 下装：牛仔裤或工装裤（避免浅色）\n"
            temp_suggestion += "- 鞋子：防水靴或防滑运动鞋\n"
            temp_suggestion += "- 配饰：雨伞、防滑鞋套\n\n"
        elif '热' in weather_lower or '高温' in weather_lower or '30' in weather_lower or '35' in weather_lower:
            temp_suggestion = "☀️ 高温穿搭：\n"
            temp_suggestion += "- 上装：透气短袖或背心 + 防晒衫\n"
            temp_suggestion += "- 下装：短裤或轻薄长裤\n"
            temp_suggestion += "- 鞋子：凉鞋或透气运动鞋\n"
            temp_suggestion += "- 配饰：太阳镜、防晒帽、冰袖\n\n"
        elif '冷' in weather_lower or '降温' in weather_lower or '10' in weather_lower or '5' in weather_lower or '0' in weather_lower:
            temp_suggestion = "❄️ 寒冷穿搭：\n"
            temp_suggestion += "- 上装：保暖内衣 + 毛衣/卫衣 + 羽绒服/厚外套\n"
            temp_suggestion += "- 下装：保暖裤或加绒牛仔裤\n"
            temp_suggestion += "- 鞋子：保暖棉靴或加绒运动鞋\n"
            temp_suggestion += "- 配饰：围巾、手套、帽子、保温杯\n\n"
        else:
            temp_suggestion = "🌤️ 温和天气穿搭：\n"
            temp_suggestion += "- 上装：长袖T恤或薄款毛衣 + 夹克/风衣\n"
            temp_suggestion += "- 下装：牛仔裤或休闲裤\n"
            temp_suggestion += "- 鞋子：舒适运动鞋或休闲皮鞋\n"
            temp_suggestion += "- 配饰：轻薄围巾或帽子\n\n"
        
        result += temp_suggestion
        result += "💡 小贴士：可以根据个人风格和场合适当调整哦！"
        
        return result
        
    except Exception as e:
        return f"生成穿搭建议时出错: {str(e)}"
