# Coze 平台配置指南

## 个人成长伙伴 Agent - Coze 部署配置

---

## 📋 准备工作

### 1. 创建 Supabase 数据库

1. 访问 https://supabase.com
2. 注册并登录
3. 点击「New Project」创建新项目
4. 等待数据库创建完成（约2分钟）
5. 进入项目后，点击「SQL Editor」
6. 复制下面的建表 SQL 并执行

---

## 🗄️ 数据库建表 SQL

在 Supabase SQL Editor 中执行以下 SQL：

```sql
-- ============================================
-- 个人成长伙伴 Agent - 数据库建表
-- ============================================

-- 1. 用户档案表
CREATE TABLE IF NOT EXISTS user_profile (
    id SERIAL PRIMARY KEY,
    height DECIMAL(5,2) NOT NULL COMMENT '身高(cm)',
    weight DECIMAL(5,2) NOT NULL COMMENT '体重(kg)',
    body_fat_rate DECIMAL(5,2) COMMENT '体脂率(%)',
    body_type VARCHAR(50) NOT NULL COMMENT '体型',
    skin_tone VARCHAR(50) NOT NULL COMMENT '肤色',
    style_preference VARCHAR(100) NOT NULL COMMENT '风格偏好',
    city VARCHAR(100) NOT NULL COMMENT '所在城市',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 衣橱表
CREATE TABLE IF NOT EXISTS wardrobe (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL COMMENT '衣物类型(上衣/裤子/外套/鞋子/配饰)',
    color VARCHAR(50) NOT NULL COMMENT '颜色',
    style VARCHAR(100) NOT NULL COMMENT '风格',
    season VARCHAR(50) NOT NULL COMMENT '适合季节(春夏秋冬/四季)',
    occasion VARCHAR(100) NOT NULL COMMENT '适合场合(上班/约会/休闲/正式)',
    image_url VARCHAR(500) COMMENT '衣服图片URL',
    brand VARCHAR(100) COMMENT '品牌',
    price DECIMAL(10,2) COMMENT '价格',
    purchase_date DATE COMMENT '购买日期',
    description VARCHAR(500) COMMENT '详细描述',
    wear_count INTEGER DEFAULT 0 COMMENT '穿着次数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 穿衣记录表
CREATE TABLE IF NOT EXISTS wear_record (
    id SERIAL PRIMARY KEY,
    wardrobe_id INTEGER REFERENCES wardrobe(id) ON DELETE CASCADE,
    wear_date DATE NOT NULL COMMENT '穿着日期',
    occasion VARCHAR(100) COMMENT '场合',
    notes VARCHAR(500) COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 健身计划表
CREATE TABLE IF NOT EXISTS fitness_plan (
    id SERIAL PRIMARY KEY,
    goal VARCHAR(100) NOT NULL COMMENT '健身目标(减脂/增肌/塑形/维持)',
    target_weight DECIMAL(5,2) COMMENT '目标体重(kg)',
    weekly_workout_days INTEGER NOT NULL COMMENT '每周训练天数',
    workout_duration INTEGER NOT NULL COMMENT '每次训练时长(分钟)',
    intensity VARCHAR(50) NOT NULL COMMENT '强度(低/中/高)',
    plan_content TEXT NOT NULL COMMENT '健身计划详细内容',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 每日锻炼记录表
CREATE TABLE IF NOT EXISTS daily_exercise_log (
    id SERIAL PRIMARY KEY,
    log_date DATE NOT NULL COMMENT '记录日期',
    exercise_name VARCHAR(100) NOT NULL COMMENT '运动名称',
    duration INTEGER NOT NULL COMMENT '运动时长(分钟)',
    calories_burned DECIMAL(10,2) COMMENT '消耗热量(千卡)',
    intensity VARCHAR(50) NOT NULL COMMENT '强度(低/中/高)',
    notes VARCHAR(500) COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. 饮食计划表
CREATE TABLE IF NOT EXISTS diet_plan (
    id SERIAL PRIMARY KEY,
    goal VARCHAR(100) NOT NULL COMMENT '饮食目标(减脂/增肌/维持)',
    daily_calories INTEGER NOT NULL COMMENT '每日目标热量(千卡)',
    protein_ratio DECIMAL(3,2) NOT NULL COMMENT '蛋白质占比(0-1)',
    carb_ratio DECIMAL(3,2) NOT NULL COMMENT '碳水化合物占比(0-1)',
    fat_ratio DECIMAL(3,2) NOT NULL COMMENT '脂肪占比(0-1)',
    plan_content TEXT NOT NULL COMMENT '饮食计划详细内容',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. 每日饮食记录表
CREATE TABLE IF NOT EXISTS daily_diet_log (
    id SERIAL PRIMARY KEY,
    log_date DATE NOT NULL COMMENT '记录日期',
    meal_type VARCHAR(50) NOT NULL COMMENT '餐次(早餐/午餐/晚餐/加餐)',
    food_name VARCHAR(200) NOT NULL COMMENT '食物名称',
    calories DECIMAL(10,2) NOT NULL COMMENT '热量(千卡)',
    protein DECIMAL(10,2) COMMENT '蛋白质(g)',
    carbs DECIMAL(10,2) COMMENT '碳水化合物(g)',
    fat DECIMAL(10,2) COMMENT '脂肪(g)',
    notes VARCHAR(500) COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. 食物仓库表
CREATE TABLE IF NOT EXISTS food_inventory (
    id SERIAL PRIMARY KEY,
    food_name VARCHAR(200) NOT NULL COMMENT '食物名称',
    category VARCHAR(100) COMMENT '食物类别',
    calories_per_100g DECIMAL(10,2) COMMENT '每100g热量(千卡)',
    protein_per_100g DECIMAL(10,2) COMMENT '每100g蛋白质(g)',
    in_stock BOOLEAN DEFAULT TRUE COMMENT '是否有货',
    quantity VARCHAR(100) COMMENT '数量/剩余量',
    notes VARCHAR(500) COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 索引
-- ============================================
CREATE INDEX IF NOT EXISTS idx_user_profile_city ON user_profile(city);
CREATE INDEX IF NOT EXISTS idx_wardrobe_category ON wardrobe(category);
CREATE INDEX IF NOT EXISTS idx_wardrobe_season ON wardrobe(season);
CREATE INDEX IF NOT EXISTS idx_wardrobe_occasion ON wardrobe(occasion);
CREATE INDEX IF NOT EXISTS idx_fitness_plan_goal ON fitness_plan(goal);
CREATE INDEX IF NOT EXISTS idx_diet_plan_goal ON diet_plan(goal);
CREATE INDEX IF NOT EXISTS idx_daily_diet_log_date ON daily_diet_log(log_date);
CREATE INDEX IF NOT EXISTS idx_daily_exercise_log_date ON daily_exercise_log(log_date);
CREATE INDEX IF NOT EXISTS idx_food_inventory_category ON food_inventory(category);

-- ============================================
-- 开启 RLS（行级安全策略）
-- ============================================
ALTER TABLE user_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE wardrobe ENABLE ROW LEVEL SECURITY;
ALTER TABLE wear_record ENABLE ROW LEVEL SECURITY;
ALTER TABLE fitness_plan ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_exercise_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE diet_plan ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_diet_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE food_inventory ENABLE ROW LEVEL SECURITY;

-- 允许所有操作（开发环境）
CREATE POLICY "Allow all" ON user_profile FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all" ON wardrobe FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all" ON wear_record FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all" ON fitness_plan FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all" ON daily_exercise_log FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all" ON diet_plan FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all" ON daily_diet_log FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all" ON food_inventory FOR ALL USING (true) WITH CHECK (true);
```

执行完成后，你会看到 `Success` 提示。

---

## 🔧 Coze 平台配置步骤

### 第一步：登录 Coze

1. 访问 https://www.coze.cn
2. 使用手机号/微信登录

### 第二步：创建 Bot

1. 点击左侧菜单「Bot」
2. 点击右上角「创建 Bot」
3. 填写信息：
   - **Bot 名称**：个人成长伙伴
   - **Bot 描述**：你的专属形象顾问，提供穿搭、体型分析、健身饮食建议
   - **图标**：上传一张图片（可选）

### 第三步：配置 Bot

#### 3.1 角色设定（System Prompt）

复制下面的内容到「角色设定」框：

```
# 角色定义
你是专业的个人形象成长伙伴，专注于穿搭建议、体型分析、健身规划和饮食管理。

## 核心能力

### 1. 体型分析（AI驱动）
- **照片分析**：上传个人全身照，AI自动识别体型、脸型、肤色
- **档案更新**：分析结果自动保存到用户档案
- **持续学习**：支持用户手动调整或补充信息

### 2. 智能穿搭推荐
- **多维度匹配**：综合考虑体型、身高、肤色、脸型、出行场合
- **风格多样**：不局限于单一风格，为用户提供多元化选择
- **场景适配**：职场、日常、约会、运动等不同场合穿搭建议

### 3. 衣橱管理（支持图片）
- **图片上传**：记录衣服照片，自动识别品类
- **网购登记**：记录购买渠道、价格、品牌、购买时间
- **穿着记录**：追踪每件衣服的使用频率

### 4. 衣服适合度判断
- **AI分析**：上传网购衣服照片，智能判断是否适合用户
- **综合评估**：结合用户体型、身高、肤色、脸型、场合给出建议
- **具体理由**：解释为什么适合/不适合，给出改进建议

### 5. 健身规划
- **个性化计划**：基于体型、体脂率、健身目标制定计划
- **进度追踪**：记录锻炼数据，追踪进展
- **动态调整**：根据用户反馈和身体变化调整计划

### 6. 饮食管理
- **营养追踪**：记录每餐饮食，自动计算热量和营养素
- **每日统计**：热量摄入、蛋白质/碳水/脂肪比例分析
- **智能建议**：热量缺口分析、营养比例优化、食物替换建议
- **食物仓库**：记录身边常吃食物，缺少时建议采购

### 7. 天气穿搭
- **实时天气**：获取当前天气和预报
- **智能建议**：根据天气、用户档案、场合推荐穿搭

## 思考模式
在回复用户前，先进行深度思考：
1. 用户的需求是什么？
2. 需要调用哪些工具获取信息？
3. 如何综合分析给出最佳建议？
4. 回复是否简洁、有帮助、实用？

## 响应规则
1. **速度优先**：回答简洁，3-7句话完成核心建议
2. **主动确认**：重要变化时询问"是否更新档案？"
3. **渐进建议**：每次给1-2个可立即执行的建议
4. **本地化**：考虑当地气候条件和用户所在地
5. **图片优先**：涉及衣服/体型时，优先使用图片分析

## 交互原则
1. **温暖专业**：语气亲切友好，像朋友聊天，但提供专业的建议
2. **循序渐进**：不追求一步到位，而是帮助用户逐步成长
3. **因人而异**：尊重每个人的独特性，提供个性化建议
4. **实用导向**：建议要落地、可执行，不是空泛的理论
5. **积极鼓励**：多给予正面反馈，帮助用户建立自信

## 禁止行为
- 不评价用户的外貌，只关注穿搭和形象
- 不强加审美标准，尊重个人选择
- 不提供超出能力范围的医疗/健身建议
- 不使用过于专业晦涩的术语，保持通俗易懂
```

#### 3.2 添加插件

在「插件」标签页，点击「添加插件」：

**必需插件**：
1. **天气查询** - 搜索「心知天气」或「和风天气」
2. **数据库** - 使用 Supabase 插件

**Supabase 配置**：
- Project URL: `https://你的项目.supabase.co`（在 Supabase 设置中获取）
- API Key: `你的 anon key`（在 Supabase 设置 > API 中获取）

#### 3.3 配置工作流

在「工作流」标签页，创建以下工作流：

**工作流1: 创建用户档案**
```json
{
  "name": "create_user_profile",
  "description": "创建用户档案",
  "input": {
    "height": "number",
    "weight": "number",
    "body_type": "string",
    "skin_tone": "string",
    "style_preference": "string",
    "city": "string"
  },
  "output": {
    "success": "boolean",
    "message": "string"
  }
}
```

**工作流2: 查询衣橱**
```json
{
  "name": "query_wardrobe",
  "description": "查询衣橱物品",
  "input": {
    "category": "string (optional)",
    "season": "string (optional)",
    "occasion": "string (optional)"
  },
  "output": {
    "items": "array"
  }
}
```

**工作流3: 记录饮食**
```json
{
  "name": "log_diet",
  "description": "记录每日饮食",
  "input": {
    "meal_type": "string",
    "food_name": "string",
    "calories": "number",
    "protein": "number (optional)",
    "carbs": "number (optional)",
    "fat": "number (optional)"
  },
  "output": {
    "success": "boolean",
    "message": "string"
  }
}
```

### 第四步：获取 Supabase 连接信息

1. 登录 Supabase
2. 进入你的项目
3. 点击右上角「Settings」
4. 点击「API」
5. 复制以下信息：
   - `Project URL`
   - `anon public` key
   - `service_role` key

### 第五步：发布 Bot

1. 点击右上角「发布」
2. 填写发布说明（如：初始版本）
3. 选择发布范围：
   - 「仅自己」- 测试用
   - 「所有用户」- 公开
4. 点击「发布」

### 第六步：在豆包中使用

1. 打开豆包 App
2. 点击左上角头像
3. 点击「我的 Bot」
4. 找到「个人成长伙伴」
5. 开始使用！

---

## 📝 工具配置清单

如果你需要手动配置每个工具，参考以下清单：

| 工具名称 | 功能 | 输入参数 |
|---------|------|---------|
| create_user_profile | 创建用户档案 | height, weight, body_type, skin_tone, style_preference, city |
| get_user_profile | 获取用户信息 | 无 |
| update_user_profile | 更新用户信息 | height?, weight?, body_fat_rate?, body_type?, skin_tone?, style_preference?, city? |
| add_wardrobe_item | 添加衣橱物品 | category, color, style, season, occasion, image_url?, brand?, price? |
| query_wardrobe_items | 查询衣橱 | category?, season?, occasion? |
| update_wardrobe_item | 更新衣物 | id, category?, color?, style?, season?, occasion? |
| record_item_wear | 记录穿着 | wardrobe_id, wear_date, occasion? |
| analyze_body_from_photo | 体型分析 | photo_url |
| check_clothing_fit | 衣服适合度 | photo_url, occasion |
| create_fitness_plan | 创建健身计划 | goal, weekly_workout_days, workout_duration, intensity |
| get_fitness_plans | 获取健身计划 | 无 |
| record_fitness | 记录锻炼 | exercise_name, duration, calories_burned, intensity |
| get_fitness_records | 获取锻炼记录 | start_date?, end_date? |
| create_diet_plan | 创建饮食计划 | goal, daily_calories, protein_ratio, carb_ratio, fat_ratio |
| get_diet_plans | 获取饮食计划 | 无 |
| record_diet | 记录饮食 | meal_type, food_name, calories, protein?, carbs?, fat? |
| get_diet_records | 查询饮食记录 | start_date?, end_date? |
| get_daily_nutrition_summary | 每日营养摘要 | date |
| get_detailed_nutrition_analysis | 详细营养分析 | start_date, end_date |
| get_nutrition_recommendations | 营养建议 | 无 |
| add_food_item | 添加食物 | food_name, category?, calories_per_100g?, protein_per_100g? |
| get_food_inventory | 获取食物仓库 | category? |
| update_food_item | 更新食物 | id, in_stock?, quantity? |
| get_shopping_suggestions | 采购建议 | 无 |
| get_weather | 天气查询 | city |
| get_weather_forecast | 天气预报 | city, days? |
| get_weather_outfit_suggestion | 天气穿搭 | city, occasion? |

---

## ⚠️ 注意事项

1. **数据安全**：生产环境请修改 RLS 策略，不要使用 `Allow all`
2. **API 密钥**：妥善保管 Supabase 的 service_role key，不要暴露在前端
3. **图片存储**：建议使用云存储（如七牛云、阿里云OSS）存储衣服照片

---

## 🆘 常见问题

**Q: 工具调用失败怎么办？**
A: 检查 Supabase 连接配置是否正确，确保 API Key 没有过期。

**Q: 如何添加更多功能？**
A: 在 Coze 平台的工作流中添加新的工作流节点。

**Q: 能否接入其他数据库？**
A: 可以，只需修改 Supabase 配置为你的数据库连接信息。

---

**祝你配置成功！** 🎉
