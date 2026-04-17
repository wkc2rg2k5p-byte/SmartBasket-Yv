from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """用户表 - 包含健康档案信息"""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # admin / user
    nickname = db.Column(db.String(50), default='')
    avatar = db.Column(db.String(200), default='')
    gender = db.Column(db.String(10), default='')
    age = db.Column(db.Integer, default=0)
    height = db.Column(db.Float, default=0)
    weight = db.Column(db.Float, default=0)
    diseases = db.Column(db.Text, default='')  # 慢性疾病
    allergies = db.Column(db.Text, default='')  # 过敏史
    special_diet = db.Column(db.Text, default='')  # 特殊饮食需求
    taste_likes = db.Column(db.Text, default='')  # 喜欢的口味
    taste_dislikes = db.Column(db.Text, default='')  # 忌口食材
    health_goal = db.Column(db.Text, default='')  # 健康目标
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=True)
    is_family_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    family = db.relationship('Family', foreign_keys=[family_id], backref=db.backref('members', lazy=True))


class Family(db.Model):
    """家庭信息表"""
    __tablename__ = 'family'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    invite_code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, default='')
    avatar = db.Column(db.String(200), default='')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)

    creator = db.relationship('User', foreign_keys=[created_by])


class Recipe(db.Model):
    """菜谱表"""
    __tablename__ = 'recipe'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), default='')
    category = db.Column(db.String(50), default='')  # 分类: 荤菜/素菜/汤类/主食/甜点
    cuisine = db.Column(db.String(50), default='')  # 菜系: 川菜/粤菜/鲁菜等
    taste = db.Column(db.String(50), default='')  # 口味: 辣/甜/酸/咸
    difficulty = db.Column(db.String(20), default='简单')  # 难度
    cook_time = db.Column(db.Integer, default=30)  # 烹饪时间(分钟)
    ingredients_json = db.Column(db.Text, default='[]')  # 食材清单JSON
    steps = db.Column(db.Text, default='')  # 做法步骤
    calories = db.Column(db.Float, default=0)  # 热量(千卡)
    protein = db.Column(db.Float, default=0)  # 蛋白质(g)
    fat = db.Column(db.Float, default=0)  # 脂肪(g)
    carbs = db.Column(db.Float, default=0)  # 碳水化合物(g)
    fiber = db.Column(db.Float, default=0)  # 膳食纤维(g)
    description = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.now)


class Ingredient(db.Model):
    """食材营养表"""
    __tablename__ = 'ingredient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), default='')  # 分类: 肉类/蔬菜/调料等
    unit = db.Column(db.String(20), default='g')
    image = db.Column(db.String(200), default='')
    protein = db.Column(db.Float, default=0)  # 每100g蛋白质
    fat = db.Column(db.Float, default=0)  # 每100g脂肪
    carbs = db.Column(db.Float, default=0)  # 每100g碳水
    calories = db.Column(db.Float, default=0)  # 每100g热量
    fiber = db.Column(db.Float, default=0)  # 每100g膳食纤维
    description = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.now)


class RecipeRecord(db.Model):
    """点菜记录表"""
    __tablename__ = 'recipe_record'
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), default='dinner')  # breakfast/lunch/dinner
    recipes_json = db.Column(db.Text, default='[]')  # 完整菜谱JSON
    total_calories = db.Column(db.Float, default=0)
    total_protein = db.Column(db.Float, default=0)
    total_fat = db.Column(db.Float, default=0)
    total_carbs = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='active')  # active / reused
    created_at = db.Column(db.DateTime, default=datetime.now)

    family = db.relationship('Family', backref=db.backref('records', lazy=True))
    user = db.relationship('User', backref=db.backref('records', lazy=True))


class ChatMessage(db.Model):
    """聊天消息表"""
    __tablename__ = 'chat_message'
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    msg_type = db.Column(db.String(20), default='text')  # text / system / recipe
    created_at = db.Column(db.DateTime, default=datetime.now)

    family = db.relationship('Family', backref=db.backref('messages', lazy=True))
    user = db.relationship('User', backref=db.backref('messages', lazy=True))


class ShoppingList(db.Model):
    """采购清单表"""
    __tablename__ = 'shopping_list'
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('recipe_record.id'), nullable=True)
    date = db.Column(db.Date, nullable=False)
    items_json = db.Column(db.Text, default='[]')  # 购物清单JSON
    status = db.Column(db.String(20), default='pending')  # pending/completed
    created_at = db.Column(db.DateTime, default=datetime.now)

    family = db.relationship('Family', backref=db.backref('shopping_lists', lazy=True))
    record = db.relationship('RecipeRecord', backref=db.backref('shopping_list', uselist=False))


class WeeklyReport(db.Model):
    """健康周报表"""
    __tablename__ = 'weekly_report'
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    week_start = db.Column(db.Date, nullable=False)
    week_end = db.Column(db.Date, nullable=False)
    total_meals = db.Column(db.Integer, default=0)
    avg_calories = db.Column(db.Float, default=0)
    avg_protein = db.Column(db.Float, default=0)
    avg_fat = db.Column(db.Float, default=0)
    avg_carbs = db.Column(db.Float, default=0)
    top_recipes = db.Column(db.Text, default='[]')  # 热门菜品JSON
    nutrition_analysis = db.Column(db.Text, default='')  # 营养分析
    suggestions = db.Column(db.Text, default='')  # 饮食建议
    report_data = db.Column(db.Text, default='{}')  # 完整报告数据JSON
    created_at = db.Column(db.DateTime, default=datetime.now)

    family = db.relationship('Family', backref=db.backref('reports', lazy=True))
