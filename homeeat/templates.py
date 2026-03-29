"""
HTML 模板模块
所有页面模板集中在这里，避免创建templates文件夹
"""

BASE_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - HomeEat</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ 
            background: white; 
            border-radius: 16px; 
            padding: 20px 30px; 
            margin-bottom: 20px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            display: flex; justify-content: space-between; align-items: center;
        }}
        .logo {{ font-size: 28px; font-weight: bold; color: #667eea; display: flex; align-items: center; gap: 10px; }}
        .nav {{ display: flex; gap: 20px; }}
        .nav a {{ 
            text-decoration: none; color: #666; padding: 8px 16px; 
            border-radius: 8px; transition: all 0.3s;
        }}
        .nav a:hover, .nav a.active {{ background: #667eea; color: white; }}
        .card {{ 
            background: white; border-radius: 16px; padding: 24px; 
            margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .btn {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; padding: 12px 24px;
            border-radius: 8px; cursor: pointer; font-size: 16px;
            text-decoration: none; display: inline-block; transition: transform 0.2s;
        }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102,126,234,0.4); }}
        .btn-secondary {{ background: #f0f0f0; color: #333; }}
        .btn-success {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
        .input-group {{ margin-bottom: 16px; }}
        .input-group input, .input-group textarea {{ 
            width: 100%; padding: 12px; border: 2px solid #e0e0e0;
            border-radius: 8px; font-size: 16px;
        }}
        .input-group input:focus {{ outline: none; border-color: #667eea; }}
        .alert {{ padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; }}
        .alert-info {{ background: #e3f2fd; color: #1976d2; border-left: 4px solid #1976d2; }}
        .alert-success {{ background: #e8f5e9; color: #388e3c; border-left: 4px solid #388e3c; }}
        .avatar {{ 
            width: 40px; height: 40px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            color: white; font-weight: bold; font-size: 18px;
        }}
        .chat-area {{ flex: 1; overflow-y: auto; margin-bottom: 16px; padding-right: 5px; max-height: 360px; }}
        .recipe-area {{ margin-top: 20px; }}
        {extra_css}
    </style>
</head>
<body>
    <div class="container">
        {header}
        {content}
    </div>
    {extra_js}
</body>
</html>
"""

def render_header(user, current='home'):
    if not user:
        return ""
    
    nav_items = [
        ('home', '💬 协同点菜', '/'),
        ('history', '📜 历史菜单', '/history'),
        ('report', '📊 健康周报', '/report'),
    ]
    
    nav_html = ''.join([
        f'<a href="{url}" class="{"active" if page == current else ""}">{label}</a>'
        for page, label, url in nav_items
    ])
    
    return f"""
    <div class="header">
        <div class="logo">🍽️ HomeEat</div>
        <nav class="nav">{nav_html}</nav>
        <div style="display: flex; align-items: center; gap: 10px;">
            <div class="avatar" style="background: {user.get('avatar_color', '#667eea')}">{user['name'][0]}</div>
            <span>{user['name']}</span>
            <a href="/logout" style="color: #999; text-decoration: none; margin-left: 10px;">退出</a>
        </div>
    </div>
    """

def login_page(error=None):
    error_html = f'<div class="alert alert-info">{error}</div>' if error else ''
    
    content = f"""
    <div style="max-width: 400px; margin: 80px auto;">
        <div class="card" style="text-align: center;">
            <div style="font-size: 48px; margin-bottom: 10px;">🍽️</div>
            <h1 style="color: #667eea; margin-bottom: 10px;">HomeEat</h1>
            <p style="color: #666; margin-bottom: 24px;">家庭饮食管理协同系统</p>
            {error_html}
            <form method="POST" action="/login">
                <div class="input-group">
                    <input type="text" name="username" placeholder="用户名" required>
                </div>
                <div class="input-group">
                    <input type="password" name="password" placeholder="密码（默认123456）" required>
                </div>
                <button type="submit" class="btn" style="width: 100%;">登录</button>
            </form>
            <div style="margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px; font-size: 14px; color: #666; text-align: left;">
                <strong>演示账号：</strong><br>
                • mama（奶奶，高血压）<br>
                • momo（妈妈，健康）<br>
                • meme（女儿，海鲜过敏）<br>
                <strong>密码：</strong>123456
            </div>
        </div>
    </div>
    """
    
    return BASE_HTML.format(title="登录", header="", content=content, extra_css="", extra_js="")

def chat_partial(chat_history, current_user):
    """仅聊天区域的HTML（用于轮询刷新）"""
    if not chat_history:
        return '<div style="text-align: center; color: #999; padding-top: 100px;"><div style="font-size: 48px; margin-bottom: 10px;">💬</div>暂无消息，开始讨论今晚吃什么吧！</div>'
    
    html = ""
    for msg in chat_history:
        is_me = msg.get('user_id') == current_user['id']
        align = "flex-end" if is_me else "flex-start"
        bg = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" if is_me else "#f5f5f5"
        color = "white" if is_me else "#333"
        
        html += f"""
        <div style="display: flex; justify-content: {align}; margin-bottom: 12px;">
            <div style="max-width: 75%;">
                <div style="font-size: 12px; color: #999; margin-bottom: 4px; text-align: {'right' if is_me else 'left'};">
                    {msg.get('user_name', '未知')} {msg['timestamp'][11:16]}
                </div>
                <div style="background: {bg}; color: {color}; padding: 10px 14px; border-radius: 12px; word-wrap: break-word; font-size: 14px; line-height: 1.5;">
                    {msg['message']}
                </div>
            </div>
        </div>
        """
    return html

def render_recipe_card(recipe):
    """生成菜谱卡片的HTML（用于轮询刷新）"""
    dishes_html = ""
    for dish in recipe.get('dishes', []):
        ingredients = "<br>".join([f"• {ing}" for ing in dish.get('ingredients', [])])
        dishes_html += f"""
        <div style="border: 2px solid #e8e8e8; border-radius: 12px; padding: 16px; margin-bottom: 12px; background: #fafafa;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h4 style="color: #667eea; margin: 0;">{dish['name']}</h4>
                <span style="background: #e3f2fd; color: #1976d2; padding: 4px 8px; border-radius: 4px; font-size: 12px;">⏱️ {dish.get('cooking_time', '未知')}</span>
            </div>
            <p style="font-size: 13px; color: #666; margin-bottom: 10px;">{dish.get('nutrition', '')}</p>
            <div style="background: white; padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 10px; border: 1px solid #eee;">
                <strong>食材：</strong><br>{ingredients}
            </div>
            <p style="font-size: 13px; color: #555; line-height: 1.6; white-space: pre-line;">
                <strong>做法：</strong><br>{dish.get('steps', '暂无')}
            </p>
        </div>
        """
    
    note = recipe.get('note', '')
    return f"""
    <div class="card" style="margin-top: 20px;">
        <h3 style="margin-bottom: 16px; color: #333;">📋 今日推荐菜谱</h3>
        {f'<div style="background: #fff3e0; color: #e65100; padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 15px;">{note}</div>' if note else ''}
        <div style="background: #e8f5e9; color: #2e7d32; padding: 12px; border-radius: 8px; margin-bottom: 15px; font-size: 14px;">
            <strong>💡 建议：</strong>{recipe.get('suggestions', '')}
        </div>
        {dishes_html}
        <div style="display: flex; gap: 10px; margin-top: 16px;">
            <a href="/generate_shopping_list" class="btn btn-success">🛒 生成采购清单</a>
            <a href="/save_menu" class="btn">💾 保存今日菜单</a>
        </div>
    </div>
    """

def home_page(user, members, chat_history, recipe=None, shopping_list=None):
    # 成员列表
    members_html = ""
    for m in members:
        health_info = ""
        if m.get('diseases'):
            health_info += f"<span style='background: #ffebee; color: #c62828; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin-right: 5px;'>⚕️{','.join(m['diseases'][:1])}</span>"
        if m.get('allergies'):
            health_info += f"<span style='background: #fff3e0; color: #ef6c00; padding: 2px 6px; border-radius: 4px; font-size: 11px;'>⚠️过敏</span>"
        
        members_html += f"""
        <div style="display: flex; align-items: center; padding: 12px; border-bottom: 1px solid #f0f0f0;">
            <div class="avatar" style="background: {m.get('avatar_color', '#667eea')}; width: 36px; height: 36px; font-size: 16px; margin-right: 12px;">
                {m['name'][0]}
            </div>
            <div style="flex: 1;">
                <div style="font-weight: 500; font-size: 14px;">{m['name']}</div>
                <div style="font-size: 12px; color: #999; margin-top: 2px;">{m.get('age', '?')}岁 {health_info}</div>
            </div>
        </div>
        """
    
    # 聊天区域初始内容
    chat_html = chat_partial(chat_history, user)
    
    # 菜谱展示
    recipe_html = render_recipe_card(recipe) if recipe else ""
    
    # 采购清单
    shopping_html = ""
    if shopping_list:
        items_html = "".join([
            f"<div style='padding: 8px; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center;'>"
            f"<input type='checkbox' style='margin-right: 10px; width: 18px; height: 18px; cursor: pointer;'>"
            f"<span>{item}</span></div>"
            for item in shopping_list.get('items', [])
        ])
        shopping_html = f"""
        <div class="card" style="margin-top: 20px;">
            <h3 style="margin-bottom: 16px; color: #333;">🛒 采购清单 ({shopping_list.get('date', '')})</h3>
            <div style="font-size: 15px; margin-bottom: 15px;">
                {items_html}
            </div>
            <button class="btn btn-secondary" onclick="window.print()" style="font-size: 14px;">🖨️ 打印清单</button>
        </div>
        """
    
    content = f"""
    <div style="display: grid; grid-template-columns: 260px 1fr; gap: 20px;">
        <!-- 左侧成员列表 -->
        <div class="card" style="padding: 0; overflow: hidden; height: fit-content;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 16px; font-weight: bold; font-size: 15px;">
                👨‍👩‍👧‍👦 家庭成员 ({len(members)}人)
            </div>
            <div style="max-height: 500px; overflow-y: auto;">
                {members_html}
            </div>
        </div>
        
        <!-- 右侧内容 -->
        <div>
            <!-- 聊天区域 -->
            <div class="card" style="height: 420px; display: flex; flex-direction: column;">
                <div id="chat-area" class="chat-area">
                    {chat_html}
                </div>
                <form id="message-form" method="POST" action="/send_message" style="display: flex; gap: 10px;">
                    <input type="text" name="message" placeholder="输入消息，例如：今晚想吃辣的、要有蔬菜..." 
                           style="flex: 1; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 15px;"
                           required autofocus autocomplete="off">
                    <button type="submit" class="btn">发送</button>
                    <a href="/generate_menu" class="btn btn-success" style="display: flex; align-items: center;">✨ 生成菜谱</a>
                </form>
            </div>
            
            <div id="recipe-area" class="recipe-area">
                {recipe_html}
            </div>
            {shopping_html}
        </div>
    </div>
    """
    
    # 加入轮询JS
    extra_js = """
    <script>
        function fetchLatest() {
            fetch('/get_latest_chat')
                .then(res => res.json())
                .then(data => {
                    if (data.chat_html) {
                        document.getElementById('chat-area').innerHTML = data.chat_html;
                    }
                    if (data.recipe_html) {
                        document.getElementById('recipe-area').innerHTML = data.recipe_html;
                    }
                })
                .catch(err => console.log('轮询出错:', err));
        }
        // 每3秒轮询一次
        setInterval(fetchLatest, 3000);
        
        // 发送消息后不清空输入框（可选），但为了体验保留
        const form = document.getElementById('message-form');
        if (form) {
            form.addEventListener('submit', function(e) {
                setTimeout(fetchLatest, 500);
            });
        }
    </script>
    """
    
    return BASE_HTML.format(
        title="协同点菜",
        header=render_header(user, 'home'),
        content=content,
        extra_css="",
        extra_js=extra_js
    )

def history_page(user, records):
    records_html = ""
    for rec in records:
        dishes = "、".join([d['name'] for d in rec['recipes'].get('dishes', [])])
        records_html += f"""
        <div style="border-bottom: 1px solid #f0f0f0; padding: 16px 0; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-weight: 500; margin-bottom: 4px; font-size: 16px;">{rec['date']}</div>
                <div style="color: #666; font-size: 14px;">{dishes}</div>
            </div>
            <a href="/reuse_menu/{rec['id']}" class="btn btn-secondary" style="padding: 8px 16px; font-size: 14px;">复用此菜单</a>
        </div>
        """
    
    content = f"""
    <div class="card">
        <h2 style="margin-bottom: 20px;">📜 历史菜单</h2>
        {records_html if records_html else '<div style="text-align: center; color: #999; padding: 40px;">暂无历史记录</div>'}
    </div>
    """
    
    return BASE_HTML.format(title="历史菜单", header=render_header(user, 'history'), content=content, extra_css="", extra_js="")

def report_page(user, report_data, members):
    ranking_html = ""
    for i, (dish, count) in enumerate(report_data.get('dish_ranking', []), 1):
        ranking_html += f"""
        <div style="display: flex; justify-content: space-between; padding: 12px; background: {'#f9f9f9' if i % 2 == 0 else 'white'}; border-radius: 8px; margin-bottom: 8px;">
            <span><span style="color: #667eea; font-weight: bold; margin-right: 8px;">#{i}</span>{dish}</span>
            <span style="color: #667eea; font-weight: bold;">{count} 次</span>
        </div>
        """
    
    nutrition = report_data.get('nutrition_analysis', {})
    suggestions_html = "".join([f"<li style='margin-bottom: 10px; padding: 10px; background: #f5f5f5; border-radius: 8px;'>{s}</li>" for s in report_data.get('suggestions', [])])
    
    content = f"""
    <div class="card">
        <h2 style="margin-bottom: 10px;">📊 饮食健康周报</h2>
        <p style="color: #666; margin-bottom: 24px; font-size: 14px;">
            统计周期：{report_data.get('start_date')} 至 {report_data.get('end_date')}
        </p>
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 24px; border-radius: 12px; text-align: center;">
                <div style="font-size: 40px; font-weight: bold;">{report_data.get('total_meals', 0)}</div>
                <div style="opacity: 0.9; margin-top: 5px;">本周餐数</div>
            </div>
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 24px; border-radius: 12px; text-align: center;">
                <div style="font-size: 40px; font-weight: bold;">{len(report_data.get('dish_ranking', []))}</div>
                <div style="opacity: 0.9; margin-top: 5px;">菜品种类</div>
            </div>
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 24px; border-radius: 12px; text-align: center;">
                <div style="font-size: 40px; font-weight: bold;">{nutrition.get('variety_score', 0)}</div>
                <div style="opacity: 0.9; margin-top: 5px;">多样性评分</div>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
            <div>
                <h3 style="margin-bottom: 16px; color: #333;">🔥 菜品热度排行</h3>
                {ranking_html if ranking_html else '<p style="color: #999;">暂无数据</p>'}
            </div>
            <div>
                <h3 style="margin-bottom: 16px; color: #333;">💡 健康建议</h3>
                <ul style="color: #555; line-height: 1.6; list-style: none; padding: 0;">
                    {suggestions_html if suggestions_html else '<li>继续记录饮食，获取个性化建议</li>'}
                </ul>
                
                <h3 style="margin: 24px 0 16px; color: #333;">📈 营养摄入分析</h3>
                <div style="background: #f9f9f9; padding: 16px; border-radius: 8px;">
                    <p style="margin-bottom: 10px;">🥩 蛋白质摄入：<strong>{nutrition.get('protein_intake', '未知')}</strong></p>
                    <p>🥬 蔬菜摄入：<strong>{nutrition.get('vegetable_intake', '未知')}</strong></p>
                </div>
            </div>
        </div>
    </div>
    """
    
    return BASE_HTML.format(title="健康周报", header=render_header(user, 'report'), content=content, extra_css="", extra_js="")