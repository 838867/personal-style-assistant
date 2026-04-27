"""天气查询工具"""

from langchain.tools import tool
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context


@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的实时天气信息

    Args:
        city: 城市名称（如：扬州、北京、上海等）

    Returns:
        str: 天气信息，包括温度、天气状况、湿度等
    """
    ctx = request_context.get() or new_context(method="get_weather")

    try:
        client = SearchClient(ctx=ctx)
        # 搜索实时天气信息
        query = f"{city}天气 温度 湿度 今天"
        response = client.web_search(query=query, count=3, need_summary=True)

        if not response.web_items:
            return f"未能获取{city}的天气信息，请稍后重试"

        # 提取天气信息
        weather_info = []
        for item in response.web_items[:2]:  # 只取前2个结果
            if item.summary:
                weather_info.append(item.summary)
            elif item.snippet:
                weather_info.append(item.snippet)

        if weather_info:
            return f"{city}天气信息：\n" + "\n".join(weather_info)
        else:
            return f"未能解析{city}的天气信息"

    except Exception as e:
        raise Exception(f"查询天气失败: {str(e)}")
