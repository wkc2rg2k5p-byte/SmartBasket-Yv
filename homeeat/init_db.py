"""
HomeEat 数据库初始化脚本
创建所有表并插入测试数据
"""
import os
import sys
import json
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config
from models import db, User, Family, Recipe, Ingredient, RecipeRecord, ChatMessage, ShoppingList, WeeklyReport

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


def init_database():
    """初始化数据库并插入测试数据"""
    with app.app_context():
        # 删除旧数据库
        db_path = os.path.join(os.path.dirname(__file__), 'homeeat.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print("已删除旧数据库")

        # 创建所有表
        db.create_all()
        print("数据库表创建成功")

        # ========== 1. 创建家庭 ==========
        family1 = Family(
            name='幸福之家',
            invite_code='HAPPY2024',
            description='我们是一个热爱美食的温馨家庭',
            avatar='https://picsum.photos/seed/family1/200'
        )
        family2 = Family(
            name='美味小窝',
            invite_code='YUMMY2024',
            description='吃货一家人，每天都要吃好吃的',
            avatar='https://picsum.photos/seed/family2/200'
        )
        db.session.add_all([family1, family2])
        db.session.flush()
        print("家庭数据创建成功")

        # ========== 2. 创建用户 ==========
        admin = User(
            username='admin',
            password=generate_password_hash('123456'),
            role='admin',
            nickname='系统管理员',
            avatar='https://randomuser.me/api/portraits/men/32.jpg',
            gender='男',
            age=35,
            height=175,
            weight=70
        )

        test_user = User(
            username='test',
            password=generate_password_hash('123456'),
            role='user',
            nickname='张妈妈',
            avatar='https://randomuser.me/api/portraits/women/44.jpg',
            gender='女',
            age=38,
            height=163,
            weight=55,
            diseases='',
            allergies='海鲜过敏',
            special_diet='低盐饮食',
            taste_likes='清淡,微辣,酸甜',
            taste_dislikes='虾,螃蟹,生蚝',
            health_goal='均衡营养，控制体重',
            family_id=family1.id,
            is_family_admin=True
        )

        user3 = User(
            username='zhangba',
            password=generate_password_hash('123456'),
            role='user',
            nickname='张爸爸',
            avatar='https://randomuser.me/api/portraits/men/46.jpg',
            gender='男',
            age=40,
            height=178,
            weight=80,
            diseases='高血压',
            allergies='',
            special_diet='低盐低脂',
            taste_likes='麻辣,红烧,烧烤',
            taste_dislikes='苦瓜,芹菜',
            health_goal='控制血压，减重',
            family_id=family1.id,
            is_family_admin=False
        )

        user4 = User(
            username='xiaoming',
            password=generate_password_hash('123456'),
            role='user',
            nickname='小明',
            avatar='https://randomuser.me/api/portraits/men/3.jpg',
            gender='男',
            age=12,
            height=155,
            weight=45,
            diseases='',
            allergies='花生过敏',
            special_diet='',
            taste_likes='甜,炸鸡,可乐',
            taste_dislikes='胡萝卜,花生',
            health_goal='长高长壮',
            family_id=family1.id,
            is_family_admin=False
        )

        user5 = User(
            username='lili',
            password=generate_password_hash('123456'),
            role='user',
            nickname='李丽',
            avatar='https://randomuser.me/api/portraits/women/26.jpg',
            gender='女',
            age=32,
            height=165,
            weight=52,
            diseases='',
            allergies='',
            special_diet='素食主义',
            taste_likes='清淡,蔬菜,豆腐',
            taste_dislikes='肥肉,内脏',
            health_goal='保持身材，健康饮食',
            family_id=family2.id,
            is_family_admin=True
        )

        user6 = User(
            username='wangda',
            password=generate_password_hash('123456'),
            role='user',
            nickname='王大',
            avatar='https://randomuser.me/api/portraits/men/52.jpg',
            gender='男',
            age=35,
            height=180,
            weight=85,
            diseases='糖尿病',
            allergies='牛奶过敏',
            special_diet='低糖饮食',
            taste_likes='清蒸,炖煮,凉拌',
            taste_dislikes='甜食,牛奶,奶酪',
            health_goal='控制血糖',
            family_id=family2.id,
            is_family_admin=False
        )

        db.session.add_all([admin, test_user, user3, user4, user5, user6])
        db.session.flush()

        # 更新家庭创建者
        family1.created_by = test_user.id
        family2.created_by = user5.id
        db.session.flush()
        print("用户数据创建成功")

        # ========== 3. 创建食材 ==========
        ingredients_data = [
            {'name': '猪肉', 'category': '肉类', 'unit': 'g', 'protein': 20.3, 'fat': 6.2, 'carbs': 1.5, 'calories': 143, 'fiber': 0,
             'image': 'https://www.themealdb.com/images/ingredients/pork.png', 'description': '优质蛋白质来源'},
            {'name': '鸡肉', 'category': '肉类', 'unit': 'g', 'protein': 23.3, 'fat': 1.2, 'carbs': 0, 'calories': 104, 'fiber': 0,
             'image': 'https://www.themealdb.com/images/ingredients/chicken.png', 'description': '低脂高蛋白'},
            {'name': '牛肉', 'category': '肉类', 'unit': 'g', 'protein': 26.2, 'fat': 3.5, 'carbs': 0, 'calories': 125, 'fiber': 0,
             'image': 'https://www.themealdb.com/images/ingredients/beef.png', 'description': '富含铁和锌'},
            {'name': '鸡蛋', 'category': '蛋类', 'unit': '个', 'protein': 12.8, 'fat': 11.1, 'carbs': 1.5, 'calories': 144, 'fiber': 0,
             'image': 'https://www.themealdb.com/images/ingredients/eggs.png', 'description': '营养全面的食材'},
            {'name': '豆腐', 'category': '豆制品', 'unit': 'g', 'protein': 8.1, 'fat': 3.7, 'carbs': 4.2, 'calories': 81, 'fiber': 0.4,
             'image': 'https://www.themealdb.com/images/ingredients/tofu.png', 'description': '植物蛋白来源'},
            {'name': '西红柿', 'category': '蔬菜', 'unit': 'g', 'protein': 0.9, 'fat': 0.2, 'carbs': 3.9, 'calories': 19, 'fiber': 1.2,
             'image': 'https://www.themealdb.com/images/ingredients/tomatoes.png', 'description': '富含番茄红素'},
            {'name': '土豆', 'category': '蔬菜', 'unit': 'g', 'protein': 2.0, 'fat': 0.2, 'carbs': 17.0, 'calories': 77, 'fiber': 2.2,
             'image': 'https://www.themealdb.com/images/ingredients/potatoes.png', 'description': '淀粉类蔬菜'},
            {'name': '白菜', 'category': '蔬菜', 'unit': 'g', 'protein': 1.5, 'fat': 0.1, 'carbs': 3.2, 'calories': 18, 'fiber': 1.0,
             'image': 'https://www.themealdb.com/images/ingredients/Napa_Cabbage.png', 'description': '冬季常见蔬菜'},
            {'name': '青椒', 'category': '蔬菜', 'unit': 'g', 'protein': 1.0, 'fat': 0.2, 'carbs': 5.4, 'calories': 22, 'fiber': 1.4,
             'image': 'https://www.themealdb.com/images/ingredients/green_pepper.png', 'description': '维生素C丰富'},
            {'name': '胡萝卜', 'category': '蔬菜', 'unit': 'g', 'protein': 1.0, 'fat': 0.2, 'carbs': 8.8, 'calories': 37, 'fiber': 2.8,
             'image': 'https://www.themealdb.com/images/ingredients/carrots.png', 'description': '富含胡萝卜素'},
            {'name': '大米', 'category': '主食', 'unit': 'g', 'protein': 7.4, 'fat': 0.8, 'carbs': 77.9, 'calories': 346, 'fiber': 0.7,
             'image': 'https://www.themealdb.com/images/ingredients/rice.png', 'description': '主食基础'},
            {'name': '面粉', 'category': '主食', 'unit': 'g', 'protein': 11.2, 'fat': 1.5, 'carbs': 73.6, 'calories': 350, 'fiber': 2.7,
             'image': 'https://www.themealdb.com/images/ingredients/flour.png', 'description': '面食原料'},
            {'name': '虾', 'category': '海鲜', 'unit': 'g', 'protein': 18.6, 'fat': 0.8, 'carbs': 0, 'calories': 87, 'fiber': 0,
             'image': 'https://www.themealdb.com/images/ingredients/king_prawns.png', 'description': '高蛋白海鲜'},
            {'name': '鱼', 'category': '海鲜', 'unit': 'g', 'protein': 18.0, 'fat': 2.5, 'carbs': 0, 'calories': 96, 'fiber': 0,
             'image': 'https://www.themealdb.com/images/ingredients/salmon.png', 'description': '优质蛋白和不饱和脂肪酸'},
            {'name': '蘑菇', 'category': '菌类', 'unit': 'g', 'protein': 3.3, 'fat': 0.3, 'carbs': 4.0, 'calories': 26, 'fiber': 2.6,
             'image': 'https://www.themealdb.com/images/ingredients/mushrooms.png', 'description': '低热量高营养'},
            {'name': '黄瓜', 'category': '蔬菜', 'unit': 'g', 'protein': 0.7, 'fat': 0.1, 'carbs': 2.9, 'calories': 15, 'fiber': 0.5,
             'image': 'https://www.themealdb.com/images/ingredients/cucumber.png', 'description': '清爽低热量'},
            {'name': '花生', 'category': '坚果', 'unit': 'g', 'protein': 24.8, 'fat': 44.3, 'carbs': 21.7, 'calories': 563, 'fiber': 5.5,
             'image': 'https://www.themealdb.com/images/ingredients/peanuts.png', 'description': '高蛋白坚果'},
            {'name': '生姜', 'category': '调料', 'unit': 'g', 'protein': 1.3, 'fat': 0.6, 'carbs': 10.3, 'calories': 41, 'fiber': 2.0,
             'image': 'https://www.themealdb.com/images/ingredients/ginger.png', 'description': '调味驱寒'},
            {'name': '大蒜', 'category': '调料', 'unit': 'g', 'protein': 4.5, 'fat': 0.2, 'carbs': 27.6, 'calories': 126, 'fiber': 1.1,
             'image': 'https://www.themealdb.com/images/ingredients/garlic.png', 'description': '杀菌调味'},
            {'name': '葱', 'category': '调料', 'unit': 'g', 'protein': 1.7, 'fat': 0.3, 'carbs': 6.5, 'calories': 30, 'fiber': 2.6,
             'image': 'https://www.themealdb.com/images/ingredients/spring_onions.png', 'description': '提香增味'},
        ]

        ingredient_objs = []
        for data in ingredients_data:
            obj = Ingredient(**data)
            ingredient_objs.append(obj)
        db.session.add_all(ingredient_objs)
        db.session.flush()
        print("食材数据创建成功")

        # ========== 4. 创建菜谱 ==========
        recipes_data = [
            {
                'name': '西红柿炒鸡蛋',
                'image': 'https://www.themealdb.com/images/media/meals/rwvw8q1765660071.jpg',
                'category': '家常菜', 'cuisine': '家常', 'taste': '酸甜',
                'difficulty': '简单', 'cook_time': 15,
                'ingredients_json': json.dumps([
                    {'name': '西红柿', 'amount': '2个', 'unit': '个'},
                    {'name': '鸡蛋', 'amount': '3个', 'unit': '个'},
                    {'name': '葱', 'amount': '适量', 'unit': ''},
                    {'name': '盐', 'amount': '适量', 'unit': ''},
                    {'name': '糖', 'amount': '少许', 'unit': ''}
                ], ensure_ascii=False),
                'steps': '1. 西红柿切块，鸡蛋打散\n2. 热锅凉油，炒鸡蛋盛出\n3. 锅中加油，炒西红柿至出汁\n4. 加入鸡蛋翻炒\n5. 加盐、糖调味，撒葱花出锅',
                'calories': 180, 'protein': 12, 'fat': 10, 'carbs': 12, 'fiber': 2.5,
                'description': '经典家常菜，酸甜可口，营养丰富'
            },
            {
                'name': '红烧肉',
                'image': 'https://www.themealdb.com/images/media/meals/1529442316.jpg',
                'category': '荤菜', 'cuisine': '家常', 'taste': '咸甜',
                'difficulty': '中等', 'cook_time': 60,
                'ingredients_json': json.dumps([
                    {'name': '五花肉', 'amount': '500g', 'unit': 'g'},
                    {'name': '生姜', 'amount': '3片', 'unit': '片'},
                    {'name': '大蒜', 'amount': '3瓣', 'unit': '瓣'},
                    {'name': '酱油', 'amount': '2勺', 'unit': '勺'},
                    {'name': '冰糖', 'amount': '30g', 'unit': 'g'},
                    {'name': '料酒', 'amount': '1勺', 'unit': '勺'}
                ], ensure_ascii=False),
                'steps': '1. 五花肉切块焯水\n2. 锅中放少油，加冰糖炒糖色\n3. 放入肉块翻炒上色\n4. 加姜蒜、料酒、酱油\n5. 加水没过肉，大火烧开转小火炖40分钟\n6. 大火收汁即可',
                'calories': 520, 'protein': 25, 'fat': 42, 'carbs': 8, 'fiber': 0,
                'description': '色泽红亮，肥而不腻的经典菜肴'
            },
            {
                'name': '清炒西兰花',
                'image': 'https://www.themealdb.com/images/media/meals/m0p0j81765568742.jpg',
                'category': '素菜', 'cuisine': '家常', 'taste': '清淡',
                'difficulty': '简单', 'cook_time': 10,
                'ingredients_json': json.dumps([
                    {'name': '西兰花', 'amount': '1棵', 'unit': '棵'},
                    {'name': '大蒜', 'amount': '3瓣', 'unit': '瓣'},
                    {'name': '盐', 'amount': '适量', 'unit': ''},
                    {'name': '蚝油', 'amount': '1勺', 'unit': '勺'}
                ], ensure_ascii=False),
                'steps': '1. 西兰花掰小朵，焯水备用\n2. 热锅凉油，爆香蒜末\n3. 放入西兰花翻炒\n4. 加蚝油、盐调味\n5. 快速翻炒出锅',
                'calories': 65, 'protein': 4.5, 'fat': 2, 'carbs': 7, 'fiber': 3.5,
                'description': '低热量高纤维的健康蔬菜'
            },
            {
                'name': '麻婆豆腐',
                'image': 'https://www.themealdb.com/images/media/meals/1525874812.jpg',
                'category': '家常菜', 'cuisine': '川菜', 'taste': '麻辣',
                'difficulty': '中等', 'cook_time': 20,
                'ingredients_json': json.dumps([
                    {'name': '豆腐', 'amount': '1块', 'unit': '块'},
                    {'name': '猪肉', 'amount': '100g', 'unit': 'g'},
                    {'name': '豆瓣酱', 'amount': '1勺', 'unit': '勺'},
                    {'name': '花椒', 'amount': '适量', 'unit': ''},
                    {'name': '葱', 'amount': '适量', 'unit': ''}
                ], ensure_ascii=False),
                'steps': '1. 豆腐切块焯水\n2. 猪肉末炒散\n3. 加豆瓣酱炒出红油\n4. 加水和豆腐煮3分钟\n5. 勾芡撒花椒粉和葱花',
                'calories': 210, 'protein': 15, 'fat': 12, 'carbs': 10, 'fiber': 1.5,
                'description': '麻辣鲜香的川菜经典'
            },
            {
                'name': '蒸鱼',
                'image': 'https://www.themealdb.com/images/media/meals/tqd7s21763780609.jpg',
                'category': '荤菜', 'cuisine': '粤菜', 'taste': '清淡',
                'difficulty': '中等', 'cook_time': 25,
                'ingredients_json': json.dumps([
                    {'name': '鱼', 'amount': '1条', 'unit': '条'},
                    {'name': '生姜', 'amount': '5片', 'unit': '片'},
                    {'name': '葱', 'amount': '2根', 'unit': '根'},
                    {'name': '蒸鱼豉油', 'amount': '2勺', 'unit': '勺'}
                ], ensure_ascii=False),
                'steps': '1. 鱼洗净在两面划几刀\n2. 铺上姜片，大火蒸8分钟\n3. 倒掉蒸出的汤汁\n4. 铺上葱丝，淋热油\n5. 浇上蒸鱼豉油即可',
                'calories': 150, 'protein': 25, 'fat': 4, 'carbs': 2, 'fiber': 0,
                'description': '原汁原味的清蒸做法，保留鱼肉鲜美'
            },
            {
                'name': '宫保鸡丁',
                'image': 'https://www.themealdb.com/images/media/meals/1525872624.jpg',
                'category': '荤菜', 'cuisine': '川菜', 'taste': '辣',
                'difficulty': '中等', 'cook_time': 20,
                'ingredients_json': json.dumps([
                    {'name': '鸡肉', 'amount': '300g', 'unit': 'g'},
                    {'name': '花生', 'amount': '50g', 'unit': 'g'},
                    {'name': '青椒', 'amount': '2个', 'unit': '个'},
                    {'name': '干辣椒', 'amount': '6个', 'unit': '个'},
                    {'name': '大蒜', 'amount': '3瓣', 'unit': '瓣'}
                ], ensure_ascii=False),
                'steps': '1. 鸡胸肉切丁腌制\n2. 调好碗汁（酱油、醋、糖、淀粉）\n3. 热锅炒花生盛出\n4. 锅中爆香干辣椒和蒜\n5. 放入鸡丁炒熟\n6. 倒入碗汁和花生翻炒出锅',
                'calories': 280, 'protein': 28, 'fat': 14, 'carbs': 10, 'fiber': 2,
                'description': '酸甜微辣，花生酥脆的经典川菜'
            },
            {
                'name': '紫菜蛋花汤',
                'image': 'https://www.themealdb.com/images/media/meals/1529446137.jpg',
                'category': '汤类', 'cuisine': '家常', 'taste': '清淡',
                'difficulty': '简单', 'cook_time': 10,
                'ingredients_json': json.dumps([
                    {'name': '紫菜', 'amount': '10g', 'unit': 'g'},
                    {'name': '鸡蛋', 'amount': '2个', 'unit': '个'},
                    {'name': '葱', 'amount': '适量', 'unit': ''},
                    {'name': '香油', 'amount': '少许', 'unit': ''}
                ], ensure_ascii=False),
                'steps': '1. 紫菜撕碎泡水\n2. 鸡蛋打散备用\n3. 水烧开放入紫菜\n4. 缓慢倒入蛋液搅拌\n5. 加盐、香油、葱花调味',
                'calories': 80, 'protein': 7, 'fat': 5, 'carbs': 3, 'fiber': 0.5,
                'description': '简单营养的家常汤品'
            },
            {
                'name': '凉拌黄瓜',
                'image': 'https://www.themealdb.com/images/media/meals/93iok31766436070.jpg',
                'category': '凉菜', 'cuisine': '家常', 'taste': '酸辣',
                'difficulty': '简单', 'cook_time': 5,
                'ingredients_json': json.dumps([
                    {'name': '黄瓜', 'amount': '2根', 'unit': '根'},
                    {'name': '大蒜', 'amount': '3瓣', 'unit': '瓣'},
                    {'name': '辣椒油', 'amount': '1勺', 'unit': '勺'},
                    {'name': '醋', 'amount': '2勺', 'unit': '勺'}
                ], ensure_ascii=False),
                'steps': '1. 黄瓜拍碎切段\n2. 蒜切末\n3. 加醋、酱油、辣椒油、盐\n4. 拌匀腌制5分钟即可',
                'calories': 35, 'protein': 1.5, 'fat': 2, 'carbs': 4, 'fiber': 1,
                'description': '开胃爽口的凉菜'
            },
            {
                'name': '土豆炖牛肉',
                'image': 'https://www.themealdb.com/images/media/meals/1529443236.jpg',
                'category': '荤菜', 'cuisine': '家常', 'taste': '咸鲜',
                'difficulty': '中等', 'cook_time': 50,
                'ingredients_json': json.dumps([
                    {'name': '牛肉', 'amount': '400g', 'unit': 'g'},
                    {'name': '土豆', 'amount': '2个', 'unit': '个'},
                    {'name': '胡萝卜', 'amount': '1根', 'unit': '根'},
                    {'name': '生姜', 'amount': '3片', 'unit': '片'},
                    {'name': '大蒜', 'amount': '3瓣', 'unit': '瓣'}
                ], ensure_ascii=False),
                'steps': '1. 牛肉切块焯水\n2. 土豆胡萝卜切块\n3. 锅中翻炒牛肉至变色\n4. 加姜蒜、酱油、料酒\n5. 加水大火烧开转小火炖30分钟\n6. 加入土豆胡萝卜继续炖15分钟',
                'calories': 350, 'protein': 30, 'fat': 15, 'carbs': 22, 'fiber': 3,
                'description': '营养丰富的炖菜，冬日暖胃'
            },
            {
                'name': '蛋炒饭',
                'image': 'https://www.themealdb.com/images/media/meals/wuyd2h1765655837.jpg',
                'category': '主食', 'cuisine': '家常', 'taste': '咸鲜',
                'difficulty': '简单', 'cook_time': 10,
                'ingredients_json': json.dumps([
                    {'name': '大米', 'amount': '200g', 'unit': 'g'},
                    {'name': '鸡蛋', 'amount': '2个', 'unit': '个'},
                    {'name': '葱', 'amount': '2根', 'unit': '根'},
                    {'name': '盐', 'amount': '适量', 'unit': ''}
                ], ensure_ascii=False),
                'steps': '1. 米饭提前煮好放凉\n2. 鸡蛋打散\n3. 热锅多油，倒入蛋液炒散\n4. 加入米饭大火翻炒\n5. 加盐调味，撒葱花出锅',
                'calories': 380, 'protein': 12, 'fat': 10, 'carbs': 60, 'fiber': 1,
                'description': '简单快手的经典主食'
            },
            {
                'name': '酸辣白菜',
                'image': 'https://www.themealdb.com/images/media/meals/9nh4dl1766435484.jpg',
                'category': '素菜', 'cuisine': '家常', 'taste': '酸辣',
                'difficulty': '简单', 'cook_time': 10,
                'ingredients_json': json.dumps([
                    {'name': '白菜', 'amount': '300g', 'unit': 'g'},
                    {'name': '干辣椒', 'amount': '5个', 'unit': '个'},
                    {'name': '醋', 'amount': '2勺', 'unit': '勺'},
                    {'name': '大蒜', 'amount': '3瓣', 'unit': '瓣'}
                ], ensure_ascii=False),
                'steps': '1. 白菜斜切片\n2. 热锅爆香干辣椒和蒜\n3. 放入白菜大火翻炒\n4. 沿锅边倒醋\n5. 加盐调味出锅',
                'calories': 45, 'protein': 2, 'fat': 1.5, 'carbs': 6, 'fiber': 2,
                'description': '酸辣开胃的快手家常菜'
            },
            {
                'name': '香菇鸡汤',
                'image': 'https://www.themealdb.com/images/media/meals/1529445893.jpg',
                'category': '汤类', 'cuisine': '家常', 'taste': '清淡',
                'difficulty': '简单', 'cook_time': 45,
                'ingredients_json': json.dumps([
                    {'name': '鸡肉', 'amount': '500g', 'unit': 'g'},
                    {'name': '蘑菇', 'amount': '100g', 'unit': 'g'},
                    {'name': '生姜', 'amount': '5片', 'unit': '片'},
                    {'name': '枸杞', 'amount': '10g', 'unit': 'g'},
                    {'name': '盐', 'amount': '适量', 'unit': ''}
                ], ensure_ascii=False),
                'steps': '1. 鸡肉切块焯水\n2. 香菇泡发切片\n3. 砂锅放入鸡肉、姜片、水\n4. 大火烧开转小火炖30分钟\n5. 加入香菇继续炖10分钟\n6. 加盐和枸杞调味',
                'calories': 200, 'protein': 28, 'fat': 8, 'carbs': 5, 'fiber': 1.5,
                'description': '滋补养身的家庭汤品'
            },
        ]

        recipe_objs = []
        for data in recipes_data:
            obj = Recipe(**data)
            recipe_objs.append(obj)
        db.session.add_all(recipe_objs)
        db.session.flush()
        print("菜谱数据创建成功")

        # ========== 5. 创建点菜记录 ==========
        today = date.today()
        records_data = []
        for i in range(7):
            d = today - timedelta(days=i)
            meal_recipes = recipes_data[i % len(recipes_data): i % len(recipes_data) + 3]
            if len(meal_recipes) < 3:
                meal_recipes = recipes_data[:3]
            total_cal = sum(r['calories'] for r in meal_recipes)
            total_pro = sum(r['protein'] for r in meal_recipes)
            total_fat = sum(r['fat'] for r in meal_recipes)
            total_carb = sum(r['carbs'] for r in meal_recipes)
            rec = RecipeRecord(
                family_id=family1.id,
                user_id=test_user.id,
                date=d,
                meal_type=['breakfast', 'lunch', 'dinner'][i % 3],
                recipes_json=json.dumps([{
                    'name': r['name'], 'image': r['image'],
                    'category': r.get('category', ''),
                    'taste': r.get('taste', ''),
                    'difficulty': r.get('difficulty', '简单'),
                    'cook_time': r.get('cook_time', 30),
                    'ingredients': json.loads(r['ingredients_json']),
                    'steps': r.get('steps', ''),
                    'calories': r['calories'], 'protein': r['protein'],
                    'fat': r['fat'], 'carbs': r['carbs']
                } for r in meal_recipes], ensure_ascii=False),
                total_calories=total_cal,
                total_protein=total_pro,
                total_fat=total_fat,
                total_carbs=total_carb,
                status='active'
            )

            records_data.append(rec)

        db.session.add_all(records_data)
        db.session.flush()
        print("点菜记录创建成功")

        # ========== 6. 创建聊天记录 ==========
        chat_messages = [
            ChatMessage(family_id=family1.id, user_id=test_user.id,
                        message='今晚大家想吃什么呀？', msg_type='text',
                        created_at=datetime.now() - timedelta(hours=3)),
            ChatMessage(family_id=family1.id, user_id=user3.id,
                        message='我想吃红烧肉！', msg_type='text',
                        created_at=datetime.now() - timedelta(hours=2, minutes=50)),
            ChatMessage(family_id=family1.id, user_id=user4.id,
                        message='我要吃炸鸡！还有可乐！', msg_type='text',
                        created_at=datetime.now() - timedelta(hours=2, minutes=40)),
            ChatMessage(family_id=family1.id, user_id=test_user.id,
                        message='小明不能天天吃炸鸡，要注意营养均衡哦', msg_type='text',
                        created_at=datetime.now() - timedelta(hours=2, minutes=30)),
            ChatMessage(family_id=family1.id, user_id=user3.id,
                        message='弄个汤吧，再配个青菜', msg_type='text',
                        created_at=datetime.now() - timedelta(hours=2, minutes=20)),
            ChatMessage(family_id=family1.id, user_id=test_user.id,
                        message='好的，那今晚做红烧肉、清炒西兰花、紫菜蛋花汤', msg_type='text',
                        created_at=datetime.now() - timedelta(hours=2, minutes=10)),
        ]
        db.session.add_all(chat_messages)
        db.session.flush()
        print("聊天记录创建成功")

        # ========== 7. 创建采购清单 ==========
        shopping1 = ShoppingList(
            family_id=family1.id,
            record_id=records_data[0].id,
            date=today,
            items_json=json.dumps([
                {'name': '五花肉', 'amount': '500', 'unit': 'g', 'checked': False},
                {'name': '西兰花', 'amount': '1', 'unit': '棵', 'checked': False},
                {'name': '鸡蛋', 'amount': '5', 'unit': '个', 'checked': True},
                {'name': '紫菜', 'amount': '10', 'unit': 'g', 'checked': False},
                {'name': '生姜', 'amount': '1', 'unit': '块', 'checked': True},
                {'name': '大蒜', 'amount': '1', 'unit': '头', 'checked': False},
                {'name': '葱', 'amount': '2', 'unit': '根', 'checked': False},
                {'name': '酱油', 'amount': '1', 'unit': '瓶', 'checked': True},
                {'name': '蚝油', 'amount': '1', 'unit': '瓶', 'checked': False},
            ], ensure_ascii=False),
            status='pending'
        )
        db.session.add(shopping1)
        db.session.flush()
        print("采购清单创建成功")

        # ========== 8. 创建健康周报 ==========
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        report1 = WeeklyReport(
            family_id=family1.id,
            week_start=week_start,
            week_end=week_end,
            total_meals=7,
            avg_calories=285,
            avg_protein=18.5,
            avg_fat=12.3,
            avg_carbs=28.6,
            top_recipes=json.dumps([
                {'name': '西红柿炒鸡蛋', 'count': 3},
                {'name': '红烧肉', 'count': 2},
                {'name': '清炒西兰花', 'count': 2},
                {'name': '紫菜蛋花汤', 'count': 2},
                {'name': '麻婆豆腐', 'count': 1}
            ], ensure_ascii=False),
            nutrition_analysis='本周饮食结构整体较为均衡。蛋白质摄入主要来源于鸡蛋和猪肉，共占蛋白质总摄入的65%。蔬菜摄入量充足，西兰花和白菜提供了丰富的膳食纤维和维生素。碳水化合物摄入以米饭为主，占比适中。',
            suggestions='1. 建议增加鱼类的摄入频次，补充不饱和脂肪酸和DHA\n2. 适当减少红烧肉等高脂菜品的频次\n3. 可以增加豆制品（如豆腐）的摄入，补充植物蛋白\n4. 建议每天保证至少两种以上蔬菜的摄入\n5. 小明成长期需要注意钙质补充，建议增加牛奶或钙片',
            report_data=json.dumps({
                'daily_calories': [280, 310, 250, 320, 270, 290, 275],
                'daily_protein': [18, 22, 16, 20, 17, 19, 18],
                'daily_fat': [12, 15, 10, 14, 11, 13, 11],
                'daily_carbs': [30, 28, 25, 32, 27, 29, 28],
                'categories': {'荤菜': 4, '素菜': 3, '汤类': 2, '主食': 2, '凉菜': 1}
            }, ensure_ascii=False)
        )
        db.session.add(report1)
        db.session.flush()
        print("健康周报创建成功")

        db.session.commit()
        print("\n========== 数据库初始化完成 ==========")
        print(f"家庭: 2个")
        print(f"用户: 6个 (admin/123456, test/123456, zhangba/123456, xiaoming/123456, lili/123456, wangda/123456)")
        print(f"食材: {len(ingredients_data)}种")
        print(f"菜谱: {len(recipes_data)}道")
        print(f"点菜记录: {len(records_data)}条")
        print(f"聊天记录: {len(chat_messages)}条")
        print(f"采购清单: 1条")
        print(f"健康周报: 1条")


if __name__ == '__main__':
    init_database()
