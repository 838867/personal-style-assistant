"""
饮食管理工具
Diet Management Tools
"""
import logging
from typing import Optional, Dict, Any, List
from langchain.tools import tool
from postgrest.exceptions import APIError
from storage.database.supabase_client import get_supabase_client
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context

logger = logging.getLogger(__name__)


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
def create_diet_plan(
    user_id: str,
    plan_name: str,
    goal: str,
    duration_weeks: int,
    daily_calorie_target: int,
    macronutrient_ratio: str,
    meals_per_day: int,
    notes: Optional[str] = None
) -> str:
    """创建饮食计划。"""
    ctx = request_context.get() or new_context(method="create_diet_plan")
    client = get_supabase_client()
    
    data = {
        "user_id": user_id,
        "plan_name": plan_name,
        "goal": goal,
        "duration_weeks": duration_weeks,
        "daily_calorie_target": daily_calorie_target,
        "macronutrient_ratio": macronutrient_ratio,
        "meals_per_day": meals_per_day,
        "notes": notes
    }
    
    data = {k: v for k, v in data.items() if v is not None}
    
    try:
        response = client.table('diet_plans').insert(data).execute()
        items = _parse_response_data(response)
        if items:
            return f"饮食计划创建成功！ID: {items[0].get('id', 'unknown')}"
        return "饮食计划创建成功"
    except APIError as e:
        raise Exception(f"创建饮食计划失败: {e.message}")


@tool
def get_diet_plans(
    user_id: str,
    is_active: bool = True,
    limit: int = 10
) -> str:
    """获取饮食计划列表。"""
    ctx = request_context.get() or new_context(method="get_diet_plans")
    client = get_supabase_client()
    
    try:
        query = client.table('diet_plans').select('*').eq('user_id', user_id)
        
        if is_active:
            query = query.eq('is_active', True)
        
        response = query.limit(limit).execute()
        items = _parse_response_data(response)
        
        if not items:
            return "没有找到饮食计划"
        
        result = f"饮食计划列表（共 {len(items)} 个）：\n"
        
        for idx, plan in enumerate(items, 1):
            if isinstance(plan, dict):
                result += f"\n{idx}. {plan.get('plan_name', '未知')}\n"
                result += f"   目标: {plan.get('goal', '未设置')}\n"
                result += f"   持续: {plan.get('duration_weeks', 0)} 周\n"
                result += f"   每日目标: {plan.get('daily_calorie_target', 0)} kcal\n"
                result += f"   营养素比例: {plan.get('macronutrient_ratio', '未设置')}\n"
                result += f"   每日餐数: {plan.get('meals_per_day', 0)} 餐\n"
        
        return result
    except Exception as e:
        return f"查询饮食计划失败: {str(e)}"


@tool
def record_diet(
    user_id: str,
    plan_id: Optional[int] = None,
    meal_date: str = None,
    meal_type: str = None,
    food_items: str = None,
    calories: int = None,
    protein: float = None,
    carbs: float = None,
    fat: float = None,
    notes: Optional[str] = None
) -> str:
    """记录饮食。"""
    import datetime
    ctx = request_context.get() or new_context(method="record_diet")
    client = get_supabase_client()
    
    # 处理默认值
    if meal_date is None:
        meal_date = datetime.datetime.now().strftime('%Y-%m-%d')
    if meal_type is None:
        meal_type = "午餐"
    if food_items is None:
        food_items = ""
    if calories is None:
        calories = 0
    if protein is None:
        protein = 0.0
    if carbs is None:
        carbs = 0.0
    if fat is None:
        fat = 0.0
    
    # 检查plan_id是否有效
    effective_plan_id = None
    if plan_id and plan_id > 0:
        # 验证计划是否存在
        try:
            response = client.table('diet_plans').select('id').eq('id', plan_id).maybe_single().execute()
            items = _parse_response_data(response)
            if items:
                effective_plan_id = plan_id
        except Exception:
            pass
    
    data = {
        "user_id": user_id,
        "plan_id": effective_plan_id,
        "meal_date": meal_date,
        "meal_type": meal_type,
        "food_items": food_items,
        "calories": calories,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "notes": notes
    }
    
    data = {k: v for k, v in data.items() if v is not None}
    
    try:
        response = client.table('diet_records').insert(data).execute()
        items = _parse_response_data(response)
        if items:
            return f"饮食记录保存成功！ID: {items[0].get('id', 'unknown')}"
        return "饮食记录保存成功"
    except APIError as e:
        raise Exception(f"保存饮食记录失败: {e.message}")


@tool
def get_diet_records(
    user_id: str,
    meal_date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 30
) -> str:
    """获取饮食记录。"""
    ctx = request_context.get() or new_context(method="get_diet_records")
    client = get_supabase_client()
    
    try:
        query = client.table('diet_records').select('*').eq('user_id', user_id)
        
        if meal_date:
            query = query.eq('meal_date', meal_date)
        else:
            if start_date:
                query = query.gte('meal_date', start_date)
            if end_date:
                query = query.lte('meal_date', end_date)
        
        response = query.order('meal_date', desc=True).limit(limit).execute()
        items = _parse_response_data(response)
        
        if not items:
            return "没有找到饮食记录"
        
        result = f"饮食记录列表（共 {len(items)} 条）：\n"
        
        for idx, record in enumerate(items, 1):
            if isinstance(record, dict):
                result += f"\n{idx}. {record.get('meal_date', '未知')} {record.get('meal_type', '')}\n"
                result += f"   食物: {record.get('food_items', '未设置')}\n"
                result += f"   卡路里: {record.get('calories', 0)} kcal\n"
                result += f"   蛋白质: {record.get('protein', 0)}g  碳水: {record.get('carbs', 0)}g  脂肪: {record.get('fat', 0)}g\n"
        
        return result
    except Exception as e:
        return f"查询饮食记录失败: {str(e)}"


@tool
def get_daily_nutrition_summary(user_id: str, target_date: str) -> str:
    """获取每日营养摘要。"""
    ctx = request_context.get() or new_context(method="get_daily_nutrition_summary")
    client = get_supabase_client()
    
    try:
        response = client.table('diet_records').select('*').eq('user_id', user_id).eq('meal_date', target_date).execute()
        items = _parse_response_data(response)
        
        if not items:
            return f"{target_date} 没有饮食记录"
        
        total_calories = 0
        total_protein = 0.0
        total_carbs = 0.0
        total_fat = 0.0
        
        meal_details = []
        
        for record in items:
            if isinstance(record, dict):
                calories = record.get('calories', 0) or 0
                protein = record.get('protein', 0) or 0.0
                carbs = record.get('carbs', 0) or 0.0
                fat = record.get('fat', 0) or 0.0
                
                total_calories += calories
                total_protein += protein
                total_carbs += carbs
                total_fat += fat
                
                meal_details.append(f"{record.get('meal_type', '')}: {record.get('food_items', '')}")
        
        result = f"📅 {target_date} 营养摘要\n"
        result += f"{'='*30}\n"
        result += f"总摄入:\n"
        result += f"  卡路里: {total_calories} kcal\n"
        result += f"  蛋白质: {total_protein}g\n"
        result += f"  碳水: {total_carbs}g\n"
        result += f"  脂肪: {total_fat}g\n"
        result += f"{'='*30}\n"
        result += f"餐次明细:\n"
        for detail in meal_details:
            result += f"  • {detail}\n"
        
        return result
    except Exception as e:
        return f"获取营养摘要失败: {str(e)}"


@tool
def get_detailed_nutrition_analysis(
    user_id: str,
    target_date: str
) -> str:
    """
    获取详细的每日营养分析和建议。
    
    Args:
        user_id: 用户唯一标识
        target_date: 日期 (YYYY-MM-DD格式)
    
    Returns:
        详细的营养分析报告和建议
    
    Example:
        >>> get_detailed_nutrition_analysis("小明", "2024-01-15")
    """
    ctx = request_context.get() or new_context(method="get_detailed_nutrition_analysis")
    client = get_supabase_client()
    
    try:
        # 获取饮食记录
        response = client.table('diet_records').select('*').eq('user_id', user_id).eq('meal_date', target_date).execute()
        items = _parse_response_data(response)
        
        # 获取用户档案（获取营养目标）
        profile_response = client.table('user_profiles').select('*').eq('user_id', user_id).execute()
        profile_data = _parse_response_data(profile_response)
        
        # 获取饮食计划
        plan_response = client.table('diet_plans').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(1).execute()
        plan_data = _parse_response_data(plan_response)
        
        # 计算今日摄入
        total_calories = 0
        total_protein = 0.0
        total_carbs = 0.0
        total_fat = 0.0
        meals_by_type = {}
        
        for record in items:
            if isinstance(record, dict):
                calories = record.get('calories', 0) or 0
                protein = record.get('protein', 0) or 0.0
                carbs = record.get('carbs', 0) or 0.0
                fat = record.get('fat', 0) or 0.0
                
                total_calories += calories
                total_protein += protein
                total_carbs += carbs
                total_fat += fat
                
                meal_type = record.get('meal_type', '其他')
                if meal_type not in meals_by_type:
                    meals_by_type[meal_type] = []
                meals_by_type[meal_type].append(record)
        
        # 获取目标值
        daily_calorie_target = 2000
        protein_ratio = 0.30
        carbs_ratio = 0.40
        fat_ratio = 0.30
        
        if profile_data and isinstance(profile_data[0], dict):
            profile = profile_data[0]
            daily_calorie_target = profile.get('daily_calorie_intake_target') or 2000
        
        if plan_data and isinstance(plan_data[0], dict):
            plan = plan_data[0]
            target_calories = plan.get('target_calories')
            if target_calories:
                daily_calorie_target = target_calories
        
        # 计算百分比
        calorie_percent = (total_calories / daily_calorie_target * 100) if daily_calorie_target > 0 else 0
        protein_calories = total_protein * 4
        carbs_calories = total_carbs * 4
        fat_calories = total_fat * 9
        total_macro_calories = protein_calories + carbs_calories + fat_calories
        
        if total_macro_calories > 0:
            actual_protein_ratio = protein_calories / total_macro_calories
            actual_carbs_ratio = carbs_calories / total_macro_calories
            actual_fat_ratio = fat_calories / total_macro_calories
        else:
            actual_protein_ratio = 0.33
            actual_carbs_ratio = 0.33
            actual_fat_ratio = 0.33
        
        # 构建输出
        output = f"""## 📊 {target_date} 营养详细分析

### 🔥 热量分析

| 项目 | 目标 | 实际 | 完成度 |
|------|------|------|--------|
| 每日热量 | {daily_calorie_target} kcal | {total_calories} kcal | {calorie_percent:.1f}% |

"""
        
        # 热量状态判断
        calorie_diff = total_calories - daily_calorie_target
        if abs(calorie_diff) <= 200:
            calorie_status = "✅ 热量摄入适中"
        elif calorie_diff > 0:
            calorie_status = f"⚠️ 热量超标 {abs(calorie_diff)} kcal"
        else:
            calorie_status = f"📉 热量缺口 {abs(calorie_diff)} kcal"
        
        output += f"{calorie_status}\n\n"
        
        output += f"""### 💪 营养素比例分析

| 营养素 | 实际占比 | 推荐范围 | 评价 |
|--------|----------|----------|------|
| 蛋白质 | {actual_protein_ratio*100:.1f}% | 20-35% | {"✅" if 0.2 <= actual_protein_ratio <= 0.35 else "⚠️"} |
| 碳水 | {actual_carbs_ratio*100:.1f}% | 40-55% | {"✅" if 0.4 <= actual_carbs_ratio <= 0.55 else "⚠️"} |
| 脂肪 | {actual_fat_ratio*100:.1f}% | 20-35% | {"✅" if 0.2 <= actual_fat_ratio <= 0.35 else "⚠️"} |

"""
        
        output += f"""### 📈 详细数据

| 营养素 | 实际摄入 | 来源 |
|--------|----------|------|
| 蛋白质 | {total_protein:.1f}g | {protein_calories:.0f} kcal |
| 碳水 | {total_carbs:.1f}g | {carbs_calories:.0f} kcal |
| 脂肪 | {total_fat:.1f}g | {fat_calories:.0f} kcal |

"""
        
        # 餐次分析
        if meals_by_type:
            output += "### 🍽️ 餐次分布\n\n"
            for meal_type in ['早餐', '午餐', '晚餐', '加餐']:
                if meal_type in meals_by_type:
                    meal_records = meals_by_type[meal_type]
                    meal_calories = sum(r.get('calories', 0) or 0 for r in meal_records)
                    meal_protein = sum(r.get('protein', 0) or 0 for r in meal_records)
                    meal_carbs = sum(r.get('carbs', 0) or 0 for r in meal_records)
                    meal_fat = sum(r.get('fat', 0) or 0 for r in meal_records)
                    
                    meal_emoji = {
                        '早餐': '🌅',
                        '午餐': '☀️',
                        '晚餐': '🌙',
                        '加餐': '🍎'
                    }.get(meal_type, '🍽️')
                    
                    output += f"{meal_emoji} **{meal_type}**: {meal_calories} kcal | P:{meal_protein:.0f}g C:{meal_carbs:.0f}g F:{meal_fat:.0f}g\n"
            output += "\n"
        
        # 生成建议
        output += "### 💡 营养建议\n\n"
        
        suggestions = []
        
        # 热量建议
        if calorie_diff > 500:
            suggestions.append("热量摄入偏高，建议减少高脂肪、高糖食物")
        elif calorie_diff < -500:
            suggestions.append("热量摄入偏低，可以适当增加健康碳水来源")
        
        # 蛋白质建议
        protein_percent_of_cal = (total_protein * 4 / total_calories * 100) if total_calories > 0 else 0
        if protein_percent_of_cal < 15:
            suggestions.append("蛋白质摄入偏低，建议增加鸡胸肉、鱼、蛋、豆制品")
        elif protein_percent_of_cal > 35:
            suggestions.append("蛋白质比例偏高，注意适量减少，增加蔬菜摄入")
        
        # 碳水建议
        carbs_percent_of_cal = (total_carbs * 4 / total_calories * 100) if total_calories > 0 else 0
        if carbs_percent_of_cal < 40:
            suggestions.append("碳水摄入偏低，建议增加燕麦、糙米、红薯等复合碳水")
        elif carbs_percent_of_cal > 60:
            suggestions.append("碳水比例偏高，可以减少精制碳水，增加蔬菜比例")
        
        # 脂肪建议
        fat_percent_of_cal = (total_fat * 9 / total_calories * 100) if total_calories > 0 else 0
        if fat_percent_of_cal > 35:
            suggestions.append("脂肪摄入偏高，建议减少油炸食品，选择清蒸/水煮烹饪方式")
        
        # 餐次建议
        if '早餐' not in meals_by_type:
            suggestions.append("⚠️ 未记录早餐，早餐对代谢很重要，建议养成吃早餐的习惯")
        
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                output += f"{i}. {suggestion}\n"
        else:
            output += "🎉 营养摄入均衡，继续保持！\n"
        
        return output.strip()
        
    except Exception as e:
        logger.error(f"Error in get_detailed_nutrition_analysis: {e}")
        return f"分析失败: {str(e)}"


@tool
def get_nutrition_recommendations(
    user_id: str,
    target_date: str = None
) -> str:
    """
    获取营养改善建议。
    
    Args:
        user_id: 用户唯一标识
        target_date: 可选，日期 (YYYY-MM-DD格式)，默认为今天
    
    Returns:
        营养改善建议
    
    Example:
        >>> get_nutrition_recommendations("小明", "2024-01-15")
    """
    ctx = request_context.get() or new_context(method="get_nutrition_recommendations")
    client = get_supabase_client()
    
    try:
        if not target_date:
            from datetime import datetime
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        # 获取用户档案
        profile_response = client.table('user_profiles').select('*').eq('user_id', user_id).execute()
        profile_data = _parse_response_data(profile_response)
        
        # 获取最近的饮食记录（最近7天）
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        week_response = client.table('diet_records').select('*').eq('user_id', user_id).gte('meal_date', start_date).lte('meal_date', end_date).execute()
        week_data = _parse_response_data(week_response)
        
        # 获取目标值
        daily_calorie_target = 2000
        if profile_data and isinstance(profile_data[0], dict):
            profile = profile_data[0]
            daily_calorie_target = profile.get('daily_calorie_intake_target') or 2000
            fitness_goal = profile.get('fitness_goal', '')
        
        # 计算7天平均
        total_week_calories = sum(r.get('calories', 0) or 0 for r in week_data)
        total_week_protein = sum(r.get('protein', 0) or 0 for r in week_data)
        total_week_carbs = sum(r.get('carbs', 0) or 0 for r in week_data)
        total_week_fat = sum(r.get('fat', 0) or 0 for r in week_data)
        
        days_with_records = len(set(r.get('meal_date') for r in week_data if r.get('meal_date')))
        if days_with_records == 0:
            days_with_records = 1
        
        avg_daily_calories = total_week_calories / days_with_records
        avg_daily_protein = total_week_protein / days_with_records
        avg_daily_carbs = total_week_carbs / days_with_records
        avg_daily_fat = total_week_fat / days_with_records
        
        # 生成建议
        output = f"""## 🎯 营养改善建议

### 📅 近{days_with_records}天饮食概况

| 指标 | 日均摄入 | 目标 | 状态 |
|------|----------|------|------|
| 热量 | {avg_daily_calories:.0f} kcal | {daily_calorie_target} kcal | {"✅" if abs(avg_daily_calories - daily_calorie_target) < 300 else "⚠️"} |
| 蛋白质 | {avg_daily_protein:.0f}g | {daily_calorie_target * 0.25 / 4:.0f}g | {"✅" if avg_daily_protein > 60 else "⚠️"} |
| 碳水 | {avg_daily_carbs:.0f}g | {daily_calorie_target * 0.45 / 4:.0f}g | {"✅" if 150 < avg_daily_carbs < 300 else "⚠️"} |
| 脂肪 | {avg_daily_fat:.0f}g | {daily_calorie_target * 0.30 / 9:.0f}g | {"✅" if 40 < avg_daily_fat < 80 else "⚠️"} |

"""
        
        # 具体建议
        output += "### 💡 个性化建议\n\n"
        
        recommendations = []
        
        # 热量趋势
        if avg_daily_calories > daily_calorie_target * 1.1:
            recommendations.append("📈 热量摄入持续偏高，建议：\n   - 用清蒸、水煮替代油炸\n   - 减少含糖饮料和甜食\n   - 增加蔬菜比例，减少主食量")
        elif avg_daily_calories < daily_calorie_target * 0.9:
            recommendations.append("📉 热量摄入持续偏低，建议：\n   - 适当增加健康碳水（燕麦、糙米、红薯）\n   - 训练日增加能量摄入\n   - 可以少食多餐")
        
        # 蛋白质
        if avg_daily_protein < 60:
            recommendations.append("💪 蛋白质摄入偏低，建议：\n   - 每餐优先吃蛋白质（鸡胸肉、鱼、蛋）\n   - 训练后补充乳清蛋白\n   - 增加豆制品摄入")
        elif avg_daily_protein > 150:
            recommendations.append("⚠️ 蛋白质摄入偏高，注意肾脏负担，增加蔬菜和水的摄入")
        
        # 碳水质量
        if avg_daily_carbs > 350:
            recommendations.append("🍚 碳水偏高，建议：\n   - 用糙米、全麦替代精米白面\n   - 控制主食份量\n   - 增加蔬菜作为填充")
        elif avg_daily_carbs < 100:
            recommendations.append("⚠️ 碳水偏低，可能影响运动表现，建议适量增加复合碳水")
        
        # 脂肪质量
        if avg_daily_fat > 80:
            recommendations.append("🥑 脂肪摄入偏高，建议：\n   - 减少油炸食品\n   - 选择橄榄油、坚果等优质脂肪\n   - 避免动物内脏等高胆固醇食物")
        elif avg_daily_fat < 30:
            recommendations.append("⚠️ 脂肪偏低，可能影响脂溶性维生素吸收，建议适量补充坚果、牛油果")
        
        # 食物替换建议
        output += "### 🔄 食物替换建议\n\n"
        replacements = [
            ("白米饭 → 糙米/藜麦", "增加膳食纤维和B族维生素"),
            ("白面包 → 全麦面包", "更持久的能量释放"),
            ("薯片 → 坚果(适量)", "健康脂肪替代空热量"),
            ("可乐 → 无糖茶/黑咖啡", "零热量选择"),
            ("薯条 → 烤蔬菜", "减少油脂摄入"),
            ("冰淇淋 → 希腊酸奶", "高蛋白替代"),
        ]
        
        for new, benefit in replacements:
            output += f"- {new}: {benefit}\n"
        
        output += "\n"
        
        if recommendations:
            for rec in recommendations:
                output += rec + "\n\n"
        else:
            output += "🎉 饮食结构良好！继续保持健康饮食习惯。\n"
        
        return output.strip()
        
    except Exception as e:
        logger.error(f"Error in get_nutrition_recommendations: {e}")
        return f"生成建议失败: {str(e)}"
