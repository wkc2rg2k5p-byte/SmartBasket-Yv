"""
AI 服务模块 - 接入智谱AI (GLM-4-Flash)
"""
import json
import random
import requests
from config import OPENAI_API_KEY, OPENAI_BASE_URL, USE_MOCK_AI

class AIService:
    def __init__(self):
        self.use_mock = USE_MOCK_AI
        if self.use_mock:
            print("[AI服务] 使用模拟模式（无API Key）")
        else:
            print("[AI服务] 使用智谱AI (GLM-4-Flash)")

    def generate_recipe(self, members, chat_history):
        """生成菜谱"""
        if self.use_mock:
            return self._mock_generate_recipe(members, chat_history)
        else:
            return self._call_real_api(members, chat_history)

    def _analyze_needs(self, members, chat_history):
        """分析家庭成员需求（仅用于模拟模式）"""
        # 分析健康情况
        has_hypertension = any('高血压' in str(m.get('diseases', [])) for m in members)
        has_diabetes = any('糖尿病' in str(m.get('diseases', [])) for m in members)
        has_child = any(m.get('age', 0) < 18 for m in members)
        has_elderly = any(m.get('age', 60) > 60 for m in members)
        
        # 分析聊天记录
        chat_text = ' '.join([msg['message'] for msg in chat_history]).lower() if chat_history else ''
        want_meat = any(word in chat_text for word in ['肉', '荤', '鱼', '鸡', '牛', '排骨'])
        want_vege = any(word in chat_text for word in ['素', '菜', '蔬菜', '绿', '清淡'])
        want_spicy = '辣' in chat_text
        want_sweet = '甜' in chat_text
        
        return {
            'has_hypertension': has_hypertension,
            'has_diabetes': has_diabetes,
            'has_child': has_child,
            'has_elderly': has_elderly,
            'want_meat': want_meat,
            'want_vege': want_vege,
            'want_spicy': want_spicy,
            'want_sweet': want_sweet,
            'chat_text': chat_text
        }

    def _mock_generate_recipe(self, members, chat_history):
        """模拟生成菜谱（基于规则）"""
        needs = self._analyze_needs(members, chat_history)
        dishes = []
        
        # 根据需求推荐菜品
        
        # 1. 主菜
        if needs['has_hypertension'] and not needs['want_spicy']:
            dishes.append({
                "name": "清蒸鲈鱼",
                "ingredients": ["鲈鱼 1条（约500g）", "葱 2根", "姜 1块", "蒸鱼豉油 2勺", "料酒 1勺"],
                "steps": "1. 鲈鱼处理干净，划几刀，抹料酒腌制10分钟\n2. 盘底铺葱姜，放上鱼，水开后蒸8-10分钟\n3. 倒掉蒸出的水，撒上葱丝，淋上热油和蒸鱼豉油",
                "nutrition": "优质蛋白，低脂肪，富含Omega-3",
                "suitable_for": ["高血压患者", "老人", "儿童"],
                "cooking_time": "20分钟"
            })
        elif needs['want_meat'] and needs['want_spicy']:
            dishes.append({
                "name": "小炒肉",
                "ingredients": ["五花肉 300g", "青椒 3个", "蒜 3瓣", "生抽 2勺", "老抽 1勺", "料酒 1勺"],
                "steps": "1. 五花肉切片，青椒切块\n2. 热锅下肉煸炒出油\n3. 下蒜和青椒炒香，调入酱油即可",
                "nutrition": "蛋白质、维生素丰富",
                "suitable_for": ["成年人"],
                "cooking_time": "15分钟"
            })
        elif needs['want_meat']:
            dishes.append({
                "name": "西红柿炒蛋",
                "ingredients": ["西红柿 2个", "鸡蛋 3个", "糖 1勺", "盐 适量", "葱 适量"],
                "steps": "1. 鸡蛋打散炒熟盛出\n2. 西红柿切块炒出汁\n3. 倒入鸡蛋，加糖盐调味，撒葱花",
                "nutrition": "蛋白质、维生素丰富，老少皆宜",
                "suitable_for": ["全家人"],
                "cooking_time": "10分钟"
            })
        else:
            dishes.append({
                "name": "蒜蓉西兰花",
                "ingredients": ["西兰花 1颗", "大蒜 5瓣", "盐 适量", "蚝油 1勺"],
                "steps": "1. 西兰花切小朵，焯水2分钟捞出\n2. 蒜切末，热锅爆香\n3. 下西兰花翻炒，调入蚝油和盐即可",
                "nutrition": "富含维生素C和膳食纤维",
                "suitable_for": ["减肥人群", "所有人"],
                "cooking_time": "10分钟"
            })
        
        # 2. 配菜
        if not needs['want_vege'] or len(dishes) < 2:
            if needs['has_child']:
                dishes.append({
                    "name": "上汤娃娃菜",
                    "ingredients": ["娃娃菜 2颗", "火腿 50g", "皮蛋 1个", "蒜 2瓣", "高汤 适量"],
                    "steps": "1. 娃娃菜洗净切半\n2. 热锅爆香蒜和火腿\n3. 加高汤和娃娃菜煮5分钟\n4. 加皮蛋丁煮2分钟即可",
                    "nutrition": "清淡鲜美，适合儿童",
                    "suitable_for": ["儿童", "老人"],
                    "cooking_time": "15分钟"
                })
            else:
                dishes.append({
                    "name": "凉拌黄瓜",
                    "ingredients": ["黄瓜 2根", "蒜 3瓣", "醋 2勺", "生抽 1勺", "香油 适量", "辣椒油 少许"],
                    "steps": "1. 黄瓜拍碎切段\n2. 蒜切末，与调料混合\n3. 拌匀腌制10分钟即可",
                    "nutrition": "清爽开胃，低热量",
                    "suitable_for": ["减肥人群", "夏季食用"],
                    "cooking_time": "10分钟"
                })
        
        # 3. 汤品
        if needs['has_child'] or needs['has_elderly']:
            if needs['has_hypertension']:
                dishes.append({
                    "name": "冬瓜虾皮汤",
                    "ingredients": ["冬瓜 300g", "虾皮 20g", "葱 适量", "盐 少许", "香油 几滴"],
                    "steps": "1. 冬瓜去皮切片\n2. 水烧开下冬瓜煮5分钟\n3. 加虾皮和少许盐，撒葱花出锅",
                    "nutrition": "低钠清淡，利尿消肿",
                    "suitable_for": ["高血压患者", "减肥人群"],
                    "cooking_time": "10分钟"
                })
            else:
                dishes.append({
                    "name": "玉米排骨汤",
                    "ingredients": ["排骨 300g", "玉米 1根", "胡萝卜 1根", "姜 3片", "盐 适量"],
                    "steps": "1. 排骨焯水去血沫\n2. 所有材料放入砂锅，大火烧开转小火煲1小时\n3. 出锅前调味",
                    "nutrition": "补钙养胃，增强体质",
                    "suitable_for": ["儿童", "老人", "需要补钙者"],
                    "cooking_time": "70分钟"
                })
        
        # 生成建议
        suggestions = f"根据您家{len(members)}位成员的情况推荐："
        if needs['has_hypertension']:
            suggestions += "菜品以清蒸、少盐为主，适合血压控制。"
        if needs['has_child']:
            suggestions += "包含营养丰富的汤品和易消化的菜品。"
        if needs['want_vege']:
            suggestions += "蔬菜搭配充足，营养均衡。"
        
        return {
            "dishes": dishes,
            "suggestions": suggestions,
            "note": "【演示模式】基于家庭成员健康档案智能推荐。配置API Key后可获得AI生成菜谱。"
        }

    def _call_real_api(self, members, chat_history):
        """调用智谱AI生成菜谱"""
        # 1. 准备家庭成员信息
        members_info = ""
        for m in members:
            diseases = m.get('diseases', [])
            dislikes = m.get('dislikes', [])
            likes = m.get('likes', [])
            members_info += f"- {m['name']}，{m.get('age', '?')}岁"
            if diseases:
                members_info += f"，疾病：{','.join(diseases)}"
            if dislikes:
                members_info += f"，忌口：{','.join(dislikes)}"
            if likes:
                members_info += f"，喜欢：{','.join(likes)}"
            members_info += "\n"
        
        # 2. 准备聊天记录（最近10条）
        chat_text = ""
        for msg in chat_history[-10:]:
            chat_text += f"{msg.get('user_name', '用户')}: {msg['message']}\n"
        
        # 3. 构建提示词
        prompt = f"""你是一个家庭营养师。请根据以下家庭成员信息和聊天记录，推荐一份适合全家的晚餐菜谱（2-3道菜）。

【家庭成员】
{members_info}

【聊天记录】
{chat_text}

【要求】
1. 避开所有忌口和过敏食材
2. 考虑疾病情况（如高血压需低盐、糖尿病需控糖）
3. 菜品要家常、易操作
4. 返回严格的JSON格式，不要有其他文字

【返回格式】
{{
  "dishes": [
    {{
      "name": "菜名",
      "ingredients": ["食材1 数量", "食材2 数量"],
      "steps": "简要步骤，用数字编号",
      "nutrition": "营养特点",
      "cooking_time": "分钟数"
    }}
  ],
  "suggestions": "给这个家庭的综合建议"
}}"""

        # 4. 调用智谱API
        url = f"{OPENAI_BASE_URL}chat/completions"
        headers = {
            "Authorization": f"Bearer {"7888abfec6244444ae3eeb42e44332a9.zMRYQmetj5RGdRjP"}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "glm-4-flash",
            "messages": [
                {"role": "system", "content": "你是专业的家庭营养师，擅长根据家庭成员健康状况推荐菜品。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            result = response.json()
            
            # 提取AI返回的内容
            content = result['choices'][0]['message']['content']
            
            # 清理可能的markdown标记
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # 解析JSON
            recipe = json.loads(content)
            return recipe
            
        except Exception as e:
            print(f"AI调用失败: {e}")
            # 失败时回退到模拟模式
            return self._mock_generate_recipe(members, chat_history)

    def generate_weekly_report(self, stats, members):
        """生成周报"""
        total_meals = stats['total_meals']
        dish_ranking = stats['dish_ranking']
        
        # 营养分析
        protein_dishes = ['鸡', '鱼', '肉', '排骨', '牛', '蛋', '虾']
        vege_dishes = ['菜', '花', '瓜', '茄', '豆', '菇', '笋']
        
        protein_count = sum(1 for d in dish_ranking if any(m in d[0] for m in protein_dishes))
        vege_count = sum(1 for d in dish_ranking if any(m in d[0] for m in vege_dishes))
        
        analysis = {
            "summary": f"本周共记录 {total_meals} 餐，菜品丰富度良好。",
            "dish_ranking": dish_ranking,
            "nutrition_analysis": {
                "protein_intake": "充足" if protein_count >= 3 else "偏少",
                "vegetable_intake": "充足" if vege_count >= 3 else "偏少",
                "variety_score": min(len(dish_ranking) * 10, 100)
            },
            "suggestions": []
        }
        
        # 个性化建议
        for member in members:
            if '高血压' in str(member.get('diseases', [])):
                analysis['suggestions'].append(
                    f"👨‍⚕️ {member['name']}（高血压）：建议继续低盐饮食，本周可多采用蒸煮烹饪方式。"
                )
            if member.get('goal') == '减肥':
                analysis['suggestions'].append(
                    f"💪 {member['name']}（减肥目标）：建议控制主食摄入，增加蔬菜比例至每餐50%。"
                )
            if member.get('age', 0) < 18:
                analysis['suggestions'].append(
                    f"🧒 {member['name']}（成长期）：保证每日蛋白质和钙的摄入，建议每日1杯牛奶+1个鸡蛋。"
                )
        
        if not analysis['suggestions']:
            analysis['suggestions'].append("✅ 本周饮食搭配均衡，建议保持。下周可以尝试更多深海鱼类和豆制品。")
        
        return analysis

ai_service = AIService()