"""
HomeEat 家庭饮食管理协同系统 - 主应用
"""
from flask import Flask, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from datetime import date
import json
import re
import os

from config import SECRET_KEY, HOST, PORT, DEBUG
from database import db
from ai_service import ai_service
from templates import login_page, home_page, history_page, report_page, chat_partial, recipe_partial

app = Flask(__name__)
app.secret_key = SECRET_KEY

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if 'username' in session:
        return db.get_user_by_username(session['username'])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = db.get_user_by_username(username)
        
        if user and password == user.get('password', '123456'):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['family_id'] = user['family_id']
            return redirect(url_for('home'))
        else:
            return login_page(error="用户名或密码错误")
    
    return login_page()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    user = get_current_user()
    family_id = session.get('family_id')
    
    members = db.get_family_members(family_id)
    chat_history = db.get_chat_history(family_id)
    
    today = str(date.today())
    current_recipe = None
    recipe_record = db.get_recipe_by_date(family_id, today)
    if recipe_record:
        current_recipe = recipe_record['recipes']
    elif 'temp_recipe' in session:
        current_recipe = json.loads(session['temp_recipe'])
    
    shopping_list = db.get_shopping_list(family_id, today)
    
    return home_page(user, members, chat_history, current_recipe, shopping_list)

# 新增：获取最新聊天和菜谱（用于轮询）
@app.route('/get_latest_chat')
@login_required
def get_latest_chat():
    family_id = session.get('family_id')
    chat_history = db.get_chat_history(family_id)
    today = str(date.today())
    
    # 生成聊天HTML
    user = get_current_user()
    chat_html = chat_partial(chat_history, user)
    
    # 检查菜谱是否有更新
    recipe_record = db.get_recipe_by_date(family_id, today)
    current_recipe = None
    if recipe_record:
        current_recipe = recipe_record['recipes']
    elif 'temp_recipe' in session:
        current_recipe = json.loads(session['temp_recipe'])
    
    recipe_html = ""
    if current_recipe:
        from templates import render_recipe_card
        recipe_html = render_recipe_card(current_recipe)
    
    return jsonify({'chat_html': chat_html, 'recipe_html': recipe_html})

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    user = get_current_user()
    message = request.form.get('message', '').strip()
    
    if message:
        db.add_chat_message(user['family_id'], user['id'], message)
    
    return redirect(url_for('home'))

@app.route('/generate_menu')
@login_required
def generate_menu():
    user = get_current_user()
    family_id = session.get('family_id')
    
    members = db.get_family_members(family_id)
    chat_history = db.get_chat_history(family_id)
    
    if not chat_history:
        flash("请先讨论一下想吃什么，再生成菜谱", "info")
        return redirect(url_for('home'))
    
    recipe = ai_service.generate_recipe(members, chat_history)
    session['temp_recipe'] = json.dumps(recipe)
    
    return redirect(url_for('home'))

@app.route('/save_menu')
@login_required
def save_menu():
    user = get_current_user()
    family_id = session.get('family_id')
    
    temp_recipe_json = session.get('temp_recipe')
    if not temp_recipe_json:
        flash("没有待保存的菜谱", "warning")
        return redirect(url_for('home'))
    
    recipe = json.loads(temp_recipe_json)
    today = str(date.today())
    
    db.save_recipe(family_id, today, recipe, user['id'])
    db.clear_chat_history(family_id)
    session.pop('temp_recipe', None)
    
    flash("菜单已保存！", "success")
    return redirect(url_for('home'))

@app.route('/generate_shopping_list')
@login_required
def generate_shopping_list():
    user = get_current_user()
    family_id = session.get('family_id')
    
    today = str(date.today())
    recipe_record = db.get_recipe_by_date(family_id, today)
    
    if not recipe_record:
        temp_recipe_json = session.get('temp_recipe')
        if temp_recipe_json:
            recipe = json.loads(temp_recipe_json)
        else:
            flash("请先生成菜谱", "warning")
            return redirect(url_for('home'))
    else:
        recipe = recipe_record['recipes']
    
    # 智能合并食材：提取食材名称（去掉数量单位）
    ingredients = []
    for dish in recipe.get('dishes', []):
        for ing in dish.get('ingredients', []):
            # 简单合并：去除末尾的数字和单位，保留食材名
            # 例如 "五花肉 300g" -> "五花肉"
            name = re.sub(r'\s*\d+[g克斤两]?$', '', ing).strip()
            ingredients.append(name)
    
    # 去重并排序
    unique_items = sorted(list(set(ingredients)))
    
    db.save_shopping_list(family_id, today, unique_items)
    
    return redirect(url_for('home'))

@app.route('/history')
@login_required
def history():
    user = get_current_user()
    family_id = session.get('family_id')
    
    records = db.get_recipe_history(family_id)
    return history_page(user, records)

@app.route('/reuse_menu/<int:record_id>')
@login_required
def reuse_menu(record_id):
    user = get_current_user()
    family_id = session.get('family_id')
    
    records = db.get_recipe_history(family_id, limit=100)
    for rec in records:
        if rec['id'] == record_id:
            today = str(date.today())
            db.save_recipe(family_id, today, rec['recipes'], user['id'])
            flash("历史菜单已应用到今天！", "success")
            break
    
    return redirect(url_for('home'))

@app.route('/report')
@login_required
def report():
    user = get_current_user()
    family_id = session.get('family_id')
    
    stats = db.get_weekly_stats(family_id)
    members = db.get_family_members(family_id)
    
    report_data = ai_service.generate_weekly_report(stats, members)
    
    return report_page(user, report_data, members)

if __name__ == '__main__':
    print("=" * 60)
    print("  HomeEat 家庭饮食管理协同系统")
    print("=" * 60)
    print(f"数据库: {db.db_path}")
    print(f"访问地址: http://{HOST}:{PORT}")
    print("演示账号: mama, momo, meme")
    print("密码: 123456")
    print("=" * 60)
    
    app.run(host=HOST, port=PORT, debug=DEBUG)