"""
HomeEat - 家庭饮食管理协同系统
主应用文件
"""
import os
import json
import uuid
import random
from datetime import datetime, date, timedelta
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   flash, jsonify, session, send_from_directory)
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config
from models import db, User, Family, Recipe, Ingredient, RecipeRecord, ChatMessage, ShoppingList, WeeklyReport

# ========== 应用初始化 ==========
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

socketio = SocketIO(app, cors_allowed_origins="*")

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('需要管理员权限', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ========== 文件上传 ==========
@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'code': 1, 'msg': '没有选择文件'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 1, 'msg': '没有选择文件'})
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'code': 0, 'msg': '上传成功', 'data': {'url': f'/uploads/{filename}'}})
    return jsonify({'code': 1, 'msg': '不支持的文件格式'})


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ========== 认证路由 ==========
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_home'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_home'))
        flash('用户名或密码错误', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        nickname = request.form.get('nickname', '')
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return render_template('login.html', show_register=True)
        user = User(
            username=username,
            password=generate_password_hash(password),
            nickname=nickname or username,
            role='user'
        )
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('login'))
    return render_template('login.html', show_register=True)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ========== 用户前台路由 ==========
@app.route('/user/home')
@login_required
def user_home():
    # 获取用户家庭信息
    family = None
    members = []
    recent_records = []
    recipes = Recipe.query.limit(8).all()
    if current_user.family_id:
        family = Family.query.get(current_user.family_id)
        members = User.query.filter_by(family_id=current_user.family_id).all()
        recent_records = RecipeRecord.query.filter_by(
            family_id=current_user.family_id
        ).order_by(RecipeRecord.date.desc()).limit(5).all()
    return render_template('user/home.html', family=family, members=members,
                           recent_records=recent_records, recipes=recipes)


@app.route('/user/family')
@login_required
def user_family():
    family = None
    members = []
    if current_user.family_id:
        family = Family.query.get(current_user.family_id)
        members = User.query.filter_by(family_id=current_user.family_id).all()
    return render_template('user/family.html', family=family, members=members)


@app.route('/user/family/create', methods=['POST'])
@login_required
def create_family():
    name = request.form.get('name', '')
    description = request.form.get('description', '')
    invite_code = uuid.uuid4().hex[:8].upper()
    avatar = request.form.get('avatar', '')
    family = Family(name=name, description=description,
                    invite_code=invite_code, avatar=avatar,
                    created_by=current_user.id)
    db.session.add(family)
    db.session.flush()
    current_user.family_id = family.id
    current_user.is_family_admin = True
    db.session.commit()
    flash('家庭创建成功！', 'success')
    return redirect(url_for('user_family'))


@app.route('/user/family/join', methods=['POST'])
@login_required
def join_family():
    invite_code = request.form.get('invite_code', '')
    family = Family.query.filter_by(invite_code=invite_code).first()
    if not family:
        flash('邀请码无效', 'error')
        return redirect(url_for('user_family'))
    current_user.family_id = family.id
    current_user.is_family_admin = False
    db.session.commit()
    flash(f'成功加入家庭：{family.name}', 'success')
    return redirect(url_for('user_family'))


@app.route('/user/family/leave')
@login_required
def leave_family():
    current_user.family_id = None
    current_user.is_family_admin = False
    db.session.commit()
    flash('已离开家庭', 'success')
    return redirect(url_for('user_family'))


@app.route('/user/family/remove/<int:user_id>')
@login_required
def remove_member(user_id):
    if not current_user.is_family_admin:
        flash('只有家庭管理员可以移除成员', 'error')
        return redirect(url_for('user_family'))
    user = User.query.get(user_id)
    if user and user.family_id == current_user.family_id:
        user.family_id = None
        user.is_family_admin = False
        db.session.commit()
        flash('已移除成员', 'success')
    return redirect(url_for('user_family'))


@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    if request.method == 'POST':
        current_user.nickname = request.form.get('nickname', current_user.nickname)
        current_user.gender = request.form.get('gender', '')
        current_user.age = int(request.form.get('age', 0) or 0)
        current_user.height = float(request.form.get('height', 0) or 0)
        current_user.weight = float(request.form.get('weight', 0) or 0)
        current_user.diseases = request.form.get('diseases', '')
        current_user.allergies = request.form.get('allergies', '')
        current_user.special_diet = request.form.get('special_diet', '')
        current_user.taste_likes = request.form.get('taste_likes', '')
        current_user.taste_dislikes = request.form.get('taste_dislikes', '')
        current_user.health_goal = request.form.get('health_goal', '')
        avatar = request.form.get('avatar', '')
        if avatar:
            current_user.avatar = avatar
        db.session.commit()
        flash('个人档案更新成功', 'success')
        return redirect(url_for('user_profile'))
    return render_template('user/profile.html')


@app.route('/user/ordering')
@login_required
def user_ordering():
    if not current_user.family_id:
        flash('请先加入或创建一个家庭', 'warning')
        return redirect(url_for('user_family'))
    family = Family.query.get(current_user.family_id)
    members = User.query.filter_by(family_id=current_user.family_id).all()
    messages = ChatMessage.query.filter_by(
        family_id=current_user.family_id
    ).order_by(ChatMessage.created_at.asc()).limit(100).all()
    recipes = Recipe.query.all()
    return render_template('user/ordering.html', family=family,
                           members=members, messages=messages, recipes=recipes)


@app.route('/user/shopping')
@login_required
def user_shopping():
    shopping_lists = []
    if current_user.family_id:
        shopping_lists = ShoppingList.query.filter_by(
            family_id=current_user.family_id
        ).order_by(ShoppingList.date.desc()).limit(20).all()
    return render_template('user/shopping.html', shopping_lists=shopping_lists)


@app.route('/user/history')
@login_required
def user_history():
    records = []
    if current_user.family_id:
        records = RecipeRecord.query.filter_by(
            family_id=current_user.family_id
        ).order_by(RecipeRecord.date.desc()).limit(30).all()
    return render_template('user/history.html', records=records)


@app.route('/user/report')
@login_required
def user_report():
    reports = []
    if current_user.family_id:
        reports = WeeklyReport.query.filter_by(
            family_id=current_user.family_id
        ).order_by(WeeklyReport.week_end.desc()).limit(10).all()
    return render_template('user/report.html', reports=reports)


# ========== 用户 API ==========
@app.route('/api/generate_recipe', methods=['POST'])
@login_required
def generate_recipe():
    """AI智能生成菜谱"""
    if not current_user.family_id:
        return jsonify({'code': 1, 'msg': '请先加入家庭'})

    # 获取家庭成员信息和聊天记录
    members = User.query.filter_by(family_id=current_user.family_id).all()
    messages = ChatMessage.query.filter_by(
        family_id=current_user.family_id
    ).order_by(ChatMessage.created_at.desc()).limit(20).all()

    # 收集成员偏好和忌口
    all_likes = []
    all_dislikes = []
    all_allergies = []
    all_diseases = []
    for m in members:
        if m.taste_likes:
            all_likes.extend(m.taste_likes.split(','))
        if m.taste_dislikes:
            all_dislikes.extend(m.taste_dislikes.split(','))
        if m.allergies:
            all_allergies.extend(m.allergies.split(','))
        if m.diseases:
            all_diseases.extend(m.diseases.split(','))

    # 收集聊天中的饮食需求关键词
    chat_keywords = []
    for msg in messages:
        chat_keywords.append(msg.message)

    # 基于成员偏好从数据库匹配菜谱（模拟AI推荐）
    all_recipes = Recipe.query.all()
    scored_recipes = []
    for recipe in all_recipes:
        score = 50  # 基础分
        # 口味匹配加分
        for like in all_likes:
            like = like.strip()
            if like and (like in recipe.taste or like in recipe.name or like in recipe.cuisine):
                score += 15
        # 忌口食材减分
        for dislike in all_dislikes:
            dislike = dislike.strip()
            if dislike and dislike in recipe.ingredients_json:
                score -= 30
        # 过敏食材严重减分
        for allergy in all_allergies:
            allergy = allergy.strip()
            if allergy and allergy in recipe.ingredients_json:
                score -= 100
        # 聊天关键词匹配
        for keyword in chat_keywords:
            if recipe.name in keyword or recipe.taste in keyword:
                score += 20
            if recipe.cuisine in keyword:
                score += 10
        # 健康状况考虑
        if '高血压' in str(all_diseases) and recipe.taste in ['咸', '麻辣']:
            score -= 20
        if '糖尿病' in str(all_diseases) and recipe.taste in ['甜', '咸甜']:
            score -= 20
        scored_recipes.append((recipe, score))

    # 按分数排序，选取前3-5道菜
    scored_recipes.sort(key=lambda x: x[1], reverse=True)
    # 确保菜品多样性（荤素搭配）
    selected = []
    categories_count = {}
    for recipe, score in scored_recipes:
        cat = recipe.category
        if categories_count.get(cat, 0) < 2:
            selected.append(recipe)
            categories_count[cat] = categories_count.get(cat, 0) + 1
        if len(selected) >= 4:
            break

    # 如果选不够，补充
    if len(selected) < 3:
        for recipe, score in scored_recipes:
            if recipe not in selected:
                selected.append(recipe)
            if len(selected) >= 4:
                break

    # 检测忌口冲突
    conflicts = []
    for recipe in selected:
        ingredients_str = recipe.ingredients_json
        for dislike in all_dislikes:
            dislike = dislike.strip()
            if dislike and dislike in ingredients_str:
                conflicts.append(f'菜品"{recipe.name}"含有忌口食材"{dislike}"')
        for allergy in all_allergies:
            allergy = allergy.strip()
            if allergy and allergy in ingredients_str:
                conflicts.append(f'⚠️ 菜品"{recipe.name}"含有过敏原"{allergy}"，已自动排除')
                selected.remove(recipe)
                break

    # 构建返回数据
    result_recipes = []
    for recipe in selected:
        result_recipes.append({
            'id': recipe.id,
            'name': recipe.name,
            'image': recipe.image,
            'category': recipe.category,
            'taste': recipe.taste,
            'difficulty': recipe.difficulty,
            'cook_time': recipe.cook_time,
            'ingredients': json.loads(recipe.ingredients_json),
            'steps': recipe.steps,
            'calories': recipe.calories,
            'protein': recipe.protein,
            'fat': recipe.fat,
            'carbs': recipe.carbs
        })

    # 保存点菜记录
    today_date = date.today()
    record = RecipeRecord(
        family_id=current_user.family_id,
        user_id=current_user.id,
        date=today_date,
        meal_type=request.json.get('meal_type', 'dinner') if request.is_json else 'dinner',
        recipes_json=json.dumps(result_recipes, ensure_ascii=False),
        total_calories=sum(r['calories'] for r in result_recipes),
        total_protein=sum(r['protein'] for r in result_recipes),
        total_fat=sum(r['fat'] for r in result_recipes),
        total_carbs=sum(r['carbs'] for r in result_recipes),
        status='active'
    )
    db.session.add(record)
    db.session.commit()

    # 自动生成采购清单
    all_ingredients = {}
    for recipe_data in result_recipes:
        for ing in recipe_data['ingredients']:
            name = ing['name']
            if name in all_ingredients:
                all_ingredients[name]['amount'] += f" + {ing['amount']}"
            else:
                all_ingredients[name] = {
                    'name': name,
                    'amount': ing['amount'],
                    'unit': ing.get('unit', ''),
                    'checked': False
                }

    shopping = ShoppingList(
        family_id=current_user.family_id,
        record_id=record.id,
        date=today_date,
        items_json=json.dumps(list(all_ingredients.values()), ensure_ascii=False),
        status='pending'
    )
    db.session.add(shopping)
    db.session.commit()

    # 发送系统消息到聊天
    recipe_names = '、'.join([r['name'] for r in result_recipes])
    sys_msg = ChatMessage(
        family_id=current_user.family_id,
        user_id=current_user.id,
        message=f'🍽️ 已生成今日菜谱推荐：{recipe_names}',
        msg_type='recipe'
    )
    db.session.add(sys_msg)
    db.session.commit()

    return jsonify({
        'code': 0,
        'msg': '菜谱生成成功',
        'data': {
            'recipes': result_recipes,
            'conflicts': conflicts,
            'shopping_list': list(all_ingredients.values()),
            'record_id': record.id
        }
    })


@app.route('/api/shopping/toggle', methods=['POST'])
@login_required
def toggle_shopping_item():
    """切换采购清单项目状态"""
    data = request.get_json()
    shopping_id = data.get('shopping_id')
    item_index = data.get('item_index')
    shopping = ShoppingList.query.get(shopping_id)
    if not shopping:
        return jsonify({'code': 1, 'msg': '清单不存在'})
    items = json.loads(shopping.items_json)
    if 0 <= item_index < len(items):
        items[item_index]['checked'] = not items[item_index]['checked']
        shopping.items_json = json.dumps(items, ensure_ascii=False)
        # 检查是否全部完成
        if all(item['checked'] for item in items):
            shopping.status = 'completed'
        else:
            shopping.status = 'pending'
        db.session.commit()
    return jsonify({'code': 0, 'msg': '更新成功'})


@app.route('/api/history/reuse/<int:record_id>', methods=['POST'])
@login_required
def reuse_history(record_id):
    """复用历史菜单"""
    old_record = RecipeRecord.query.get(record_id)
    if not old_record or old_record.family_id != current_user.family_id:
        return jsonify({'code': 1, 'msg': '记录不存在'})
    today_date = date.today()
    new_record = RecipeRecord(
        family_id=current_user.family_id,
        user_id=current_user.id,
        date=today_date,
        meal_type=old_record.meal_type,
        recipes_json=old_record.recipes_json,
        total_calories=old_record.total_calories,
        total_protein=old_record.total_protein,
        total_fat=old_record.total_fat,
        total_carbs=old_record.total_carbs,
        status='reused'
    )
    db.session.add(new_record)

    # 同时生成采购清单
    recipes = json.loads(old_record.recipes_json)
    all_ingredients = {}
    for recipe_data in recipes:
        ings = recipe_data.get('ingredients', '[]')
        if isinstance(ings, str):
            ings = json.loads(ings)
        for ing in ings:
            name = ing['name']
            if name in all_ingredients:
                all_ingredients[name]['amount'] += f" + {ing['amount']}"
            else:
                all_ingredients[name] = {
                    'name': name,
                    'amount': ing['amount'],
                    'unit': ing.get('unit', ''),
                    'checked': False
                }

    shopping = ShoppingList(
        family_id=current_user.family_id,
        record_id=new_record.id,
        date=today_date,
        items_json=json.dumps(list(all_ingredients.values()), ensure_ascii=False),
        status='pending'
    )
    db.session.add(shopping)
    db.session.commit()
    return jsonify({'code': 0, 'msg': '菜单复用成功'})


@app.route('/api/report/generate', methods=['POST'])
@login_required
def generate_report():
    """生成健康周报"""
    if not current_user.family_id:
        return jsonify({'code': 1, 'msg': '请先加入家庭'})

    today_date = date.today()
    week_start = today_date - timedelta(days=today_date.weekday())
    week_end = week_start + timedelta(days=6)

    # 获取本周记录
    records = RecipeRecord.query.filter(
        RecipeRecord.family_id == current_user.family_id,
        RecipeRecord.date >= week_start,
        RecipeRecord.date <= week_end
    ).all()

    if not records:
        return jsonify({'code': 1, 'msg': '本周暂无点菜记录'})

    # 统计数据
    total_meals = len(records)
    total_calories = sum(r.total_calories for r in records)
    total_protein = sum(r.total_protein for r in records)
    total_fat = sum(r.total_fat for r in records)
    total_carbs = sum(r.total_carbs for r in records)

    # 统计菜品热度
    recipe_count = {}
    category_count = {}
    daily_data = {i: {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0} for i in range(7)}

    for record in records:
        day_index = (record.date - week_start).days
        if 0 <= day_index < 7:
            daily_data[day_index]['calories'] += record.total_calories
            daily_data[day_index]['protein'] += record.total_protein
            daily_data[day_index]['fat'] += record.total_fat
            daily_data[day_index]['carbs'] += record.total_carbs

        recipes = json.loads(record.recipes_json)
        for r in recipes:
            name = r.get('name', '')
            recipe_count[name] = recipe_count.get(name, 0) + 1
            cat = r.get('category', '其他')
            category_count[cat] = category_count.get(cat, 0) + 1

    top_recipes = sorted(recipe_count.items(), key=lambda x: x[1], reverse=True)[:5]
    top_recipes_list = [{'name': name, 'count': count} for name, count in top_recipes]

    # 生成营养分析和建议
    avg_calories = total_calories / max(total_meals, 1)
    avg_protein = total_protein / max(total_meals, 1)
    avg_fat = total_fat / max(total_meals, 1)
    avg_carbs = total_carbs / max(total_meals, 1)

    analysis_parts = []
    suggestions_parts = []

    if avg_protein < 15:
        analysis_parts.append('蛋白质摄入偏低')
        suggestions_parts.append('建议增加鸡蛋、鸡肉、鱼类等高蛋白食物的摄入')
    elif avg_protein > 30:
        analysis_parts.append('蛋白质摄入充足')
    else:
        analysis_parts.append('蛋白质摄入适中')

    if avg_fat > 25:
        analysis_parts.append('脂肪摄入偏高')
        suggestions_parts.append('建议减少红烧、油炸类菜品，增加蒸煮类菜品')
    else:
        analysis_parts.append('脂肪摄入合理')

    if avg_carbs > 50:
        analysis_parts.append('碳水化合物摄入偏高')
        suggestions_parts.append('建议适当减少主食摄入，增加蔬菜比例')
    else:
        analysis_parts.append('碳水化合物摄入正常')

    if category_count.get('素菜', 0) < category_count.get('荤菜', 0):
        suggestions_parts.append('建议增加蔬菜摄入量，保证每餐有绿叶蔬菜')

    if category_count.get('汤类', 0) == 0:
        suggestions_parts.append('建议每天至少一餐配汤，帮助消化')

    suggestions_parts.append('建议饮食多样化，每周尝试不同的菜品')

    nutrition_analysis = '本周共进餐{}次。'.format(total_meals) + '。'.join(analysis_parts) + '。'
    suggestions = '\n'.join([f'{i+1}. {s}' for i, s in enumerate(suggestions_parts)])

    report = WeeklyReport(
        family_id=current_user.family_id,
        week_start=week_start,
        week_end=week_end,
        total_meals=total_meals,
        avg_calories=round(avg_calories, 1),
        avg_protein=round(avg_protein, 1),
        avg_fat=round(avg_fat, 1),
        avg_carbs=round(avg_carbs, 1),
        top_recipes=json.dumps(top_recipes_list, ensure_ascii=False),
        nutrition_analysis=nutrition_analysis,
        suggestions=suggestions,
        report_data=json.dumps({
            'daily_calories': [daily_data[i]['calories'] for i in range(7)],
            'daily_protein': [daily_data[i]['protein'] for i in range(7)],
            'daily_fat': [daily_data[i]['fat'] for i in range(7)],
            'daily_carbs': [daily_data[i]['carbs'] for i in range(7)],
            'categories': category_count
        }, ensure_ascii=False)
    )
    db.session.add(report)
    db.session.commit()

    return jsonify({'code': 0, 'msg': '周报生成成功', 'data': {'report_id': report.id}})


# ========== WebSocket 事件 ==========
@socketio.on('join')
def on_join(data):
    room = f"family_{data.get('family_id')}"
    join_room(room)
    emit('status', {'msg': f'{current_user.nickname} 进入了点菜房间'}, room=room)


@socketio.on('leave')
def on_leave(data):
    room = f"family_{data.get('family_id')}"
    leave_room(room)
    emit('status', {'msg': f'{current_user.nickname} 离开了点菜房间'}, room=room)


@socketio.on('send_message')
def on_message(data):
    family_id = data.get('family_id')
    message = data.get('message', '')
    if not family_id or not message:
        return

    msg = ChatMessage(
        family_id=family_id,
        user_id=current_user.id,
        message=message,
        msg_type='text'
    )
    db.session.add(msg)
    db.session.commit()

    room = f"family_{family_id}"
    emit('new_message', {
        'id': msg.id,
        'user_id': current_user.id,
        'nickname': current_user.nickname,
        'avatar': current_user.avatar,
        'message': message,
        'msg_type': 'text',
        'time': msg.created_at.strftime('%H:%M')
    }, room=room)


# ========== 管理后台路由 ==========
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        'user_count': User.query.filter_by(role='user').count(),
        'family_count': Family.query.count(),
        'recipe_count': Recipe.query.count(),
        'ingredient_count': Ingredient.query.count(),
        'record_count': RecipeRecord.query.count(),
        'report_count': WeeklyReport.query.count(),
        'chat_count': ChatMessage.query.count(),
        'shopping_count': ShoppingList.query.count()
    }
    recent_records = RecipeRecord.query.order_by(RecipeRecord.created_at.desc()).limit(5).all()
    recent_users = User.query.filter_by(role='user').order_by(User.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats,
                           recent_records=recent_records, recent_users=recent_users)


@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    query = User.query.filter_by(role='user')
    if keyword:
        query = query.filter(User.nickname.like(f'%{keyword}%') | User.username.like(f'%{keyword}%'))
    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    families = Family.query.all()
    family_map = {f.id: f.name for f in families}
    return render_template('admin/users.html', pagination=pagination, keyword=keyword, family_map=family_map)


@app.route('/admin/users/add', methods=['POST'])
@login_required
@admin_required
def admin_add_user():
    username = request.form.get('username', '')
    password = request.form.get('password', '123456')
    nickname = request.form.get('nickname', '')
    gender = request.form.get('gender', '')
    age = int(request.form.get('age', 0) or 0)
    if User.query.filter_by(username=username).first():
        flash('用户名已存在', 'error')
        return redirect(url_for('admin_users'))
    user = User(username=username, password=generate_password_hash(password),
                nickname=nickname or username, gender=gender, age=age, role='user')
    db.session.add(user)
    db.session.commit()
    flash('用户添加成功', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/edit/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    user.nickname = request.form.get('nickname', user.nickname)
    user.gender = request.form.get('gender', user.gender)
    user.age = int(request.form.get('age', 0) or 0)
    user.height = float(request.form.get('height', 0) or 0)
    user.weight = float(request.form.get('weight', 0) or 0)
    user.diseases = request.form.get('diseases', '')
    user.allergies = request.form.get('allergies', '')
    user.taste_likes = request.form.get('taste_likes', '')
    user.taste_dislikes = request.form.get('taste_dislikes', '')
    user.health_goal = request.form.get('health_goal', '')
    password = request.form.get('password', '')
    if password:
        user.password = generate_password_hash(password)
    db.session.commit()
    flash('用户信息更新成功', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/delete/<int:user_id>')
@login_required
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('用户已删除', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/families')
@login_required
@admin_required
def admin_families():
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    query = Family.query
    if keyword:
        query = query.filter(Family.name.like(f'%{keyword}%'))
    pagination = query.order_by(Family.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/families.html', pagination=pagination, keyword=keyword)


@app.route('/admin/families/add', methods=['POST'])
@login_required
@admin_required
def admin_add_family():
    name = request.form.get('name', '')
    description = request.form.get('description', '')
    invite_code = uuid.uuid4().hex[:8].upper()
    family = Family(name=name, description=description, invite_code=invite_code)
    db.session.add(family)
    db.session.commit()
    flash('家庭创建成功', 'success')
    return redirect(url_for('admin_families'))


@app.route('/admin/families/edit/<int:family_id>', methods=['POST'])
@login_required
@admin_required
def admin_edit_family(family_id):
    family = Family.query.get_or_404(family_id)
    family.name = request.form.get('name', family.name)
    family.description = request.form.get('description', family.description)
    db.session.commit()
    flash('家庭信息更新成功', 'success')
    return redirect(url_for('admin_families'))


@app.route('/admin/families/delete/<int:family_id>')
@login_required
@admin_required
def admin_delete_family(family_id):
    family = Family.query.get_or_404(family_id)
    # 移除所有成员的family_id
    User.query.filter_by(family_id=family_id).update({'family_id': None, 'is_family_admin': False})
    db.session.delete(family)
    db.session.commit()
    flash('家庭已删除', 'success')
    return redirect(url_for('admin_families'))


@app.route('/admin/recipes')
@login_required
@admin_required
def admin_recipes():
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    query = Recipe.query
    if keyword:
        query = query.filter(Recipe.name.like(f'%{keyword}%'))
    pagination = query.order_by(Recipe.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/recipes.html', pagination=pagination, keyword=keyword)


@app.route('/admin/recipes/add', methods=['POST'])
@login_required
@admin_required
def admin_add_recipe():
    recipe = Recipe(
        name=request.form.get('name', ''),
        image=request.form.get('image', ''),
        category=request.form.get('category', ''),
        cuisine=request.form.get('cuisine', ''),
        taste=request.form.get('taste', ''),
        difficulty=request.form.get('difficulty', '简单'),
        cook_time=int(request.form.get('cook_time', 30) or 30),
        ingredients_json=request.form.get('ingredients_json', '[]'),
        steps=request.form.get('steps', ''),
        calories=float(request.form.get('calories', 0) or 0),
        protein=float(request.form.get('protein', 0) or 0),
        fat=float(request.form.get('fat', 0) or 0),
        carbs=float(request.form.get('carbs', 0) or 0),
        fiber=float(request.form.get('fiber', 0) or 0),
        description=request.form.get('description', '')
    )
    db.session.add(recipe)
    db.session.commit()
    flash('菜谱添加成功', 'success')
    return redirect(url_for('admin_recipes'))


@app.route('/admin/recipes/edit/<int:recipe_id>', methods=['POST'])
@login_required
@admin_required
def admin_edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    recipe.name = request.form.get('name', recipe.name)
    recipe.image = request.form.get('image', recipe.image)
    recipe.category = request.form.get('category', recipe.category)
    recipe.cuisine = request.form.get('cuisine', recipe.cuisine)
    recipe.taste = request.form.get('taste', recipe.taste)
    recipe.difficulty = request.form.get('difficulty', recipe.difficulty)
    recipe.cook_time = int(request.form.get('cook_time', 30) or 30)
    recipe.ingredients_json = request.form.get('ingredients_json', recipe.ingredients_json)
    recipe.steps = request.form.get('steps', recipe.steps)
    recipe.calories = float(request.form.get('calories', 0) or 0)
    recipe.protein = float(request.form.get('protein', 0) or 0)
    recipe.fat = float(request.form.get('fat', 0) or 0)
    recipe.carbs = float(request.form.get('carbs', 0) or 0)
    recipe.fiber = float(request.form.get('fiber', 0) or 0)
    recipe.description = request.form.get('description', recipe.description)
    db.session.commit()
    flash('菜谱更新成功', 'success')
    return redirect(url_for('admin_recipes'))


@app.route('/admin/recipes/delete/<int:recipe_id>')
@login_required
@admin_required
def admin_delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    db.session.delete(recipe)
    db.session.commit()
    flash('菜谱已删除', 'success')
    return redirect(url_for('admin_recipes'))


@app.route('/admin/ingredients')
@login_required
@admin_required
def admin_ingredients():
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    query = Ingredient.query
    if keyword:
        query = query.filter(Ingredient.name.like(f'%{keyword}%'))
    pagination = query.order_by(Ingredient.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/ingredients.html', pagination=pagination, keyword=keyword)


@app.route('/admin/ingredients/add', methods=['POST'])
@login_required
@admin_required
def admin_add_ingredient():
    ingredient = Ingredient(
        name=request.form.get('name', ''),
        category=request.form.get('category', ''),
        unit=request.form.get('unit', 'g'),
        image=request.form.get('image', ''),
        protein=float(request.form.get('protein', 0) or 0),
        fat=float(request.form.get('fat', 0) or 0),
        carbs=float(request.form.get('carbs', 0) or 0),
        calories=float(request.form.get('calories', 0) or 0),
        fiber=float(request.form.get('fiber', 0) or 0),
        description=request.form.get('description', '')
    )
    db.session.add(ingredient)
    db.session.commit()
    flash('食材添加成功', 'success')
    return redirect(url_for('admin_ingredients'))


@app.route('/admin/ingredients/edit/<int:ingredient_id>', methods=['POST'])
@login_required
@admin_required
def admin_edit_ingredient(ingredient_id):
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    ingredient.name = request.form.get('name', ingredient.name)
    ingredient.category = request.form.get('category', ingredient.category)
    ingredient.unit = request.form.get('unit', ingredient.unit)
    ingredient.image = request.form.get('image', ingredient.image)
    ingredient.protein = float(request.form.get('protein', 0) or 0)
    ingredient.fat = float(request.form.get('fat', 0) or 0)
    ingredient.carbs = float(request.form.get('carbs', 0) or 0)
    ingredient.calories = float(request.form.get('calories', 0) or 0)
    ingredient.fiber = float(request.form.get('fiber', 0) or 0)
    ingredient.description = request.form.get('description', ingredient.description)
    db.session.commit()
    flash('食材更新成功', 'success')
    return redirect(url_for('admin_ingredients'))


@app.route('/admin/ingredients/delete/<int:ingredient_id>')
@login_required
@admin_required
def admin_delete_ingredient(ingredient_id):
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    db.session.delete(ingredient)
    db.session.commit()
    flash('食材已删除', 'success')
    return redirect(url_for('admin_ingredients'))


@app.route('/admin/records')
@login_required
@admin_required
def admin_records():
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    query = RecipeRecord.query
    if keyword:
        query = query.filter(RecipeRecord.recipes_json.like(f'%{keyword}%'))
    pagination = query.order_by(RecipeRecord.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/records.html', pagination=pagination, keyword=keyword)


@app.route('/admin/records/delete/<int:record_id>')
@login_required
@admin_required
def admin_delete_record(record_id):
    record = RecipeRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    flash('记录已删除', 'success')
    return redirect(url_for('admin_records'))


@app.route('/admin/reports')
@login_required
@admin_required
def admin_reports():
    page = request.args.get('page', 1, type=int)
    pagination = WeeklyReport.query.order_by(
        WeeklyReport.created_at.desc()
    ).paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/reports.html', pagination=pagination)


@app.route('/admin/reports/delete/<int:report_id>')
@login_required
@admin_required
def admin_delete_report(report_id):
    report = WeeklyReport.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    flash('周报已删除', 'success')
    return redirect(url_for('admin_reports'))


@app.route('/admin/chats')
@login_required
@admin_required
def admin_chats():
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    query = ChatMessage.query
    if keyword:
        query = query.filter(ChatMessage.message.like(f'%{keyword}%'))
    pagination = query.order_by(ChatMessage.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('admin/chats.html', pagination=pagination, keyword=keyword)


@app.route('/admin/chats/delete/<int:msg_id>')
@login_required
@admin_required
def admin_delete_chat(msg_id):
    msg = ChatMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    flash('消息已删除', 'success')
    return redirect(url_for('admin_chats'))


# ========== Jinja2 过滤器 ==========
@app.template_filter('fromjson')
def fromjson_filter(s):
    try:
        return json.loads(s) if s else []
    except (json.JSONDecodeError, TypeError):
        return []


@app.template_filter('meal_type_cn')
def meal_type_cn(val):
    mapping = {'breakfast': '早餐', 'lunch': '午餐', 'dinner': '晚餐'}
    return mapping.get(val, val)


# ========== 启动 ==========
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
