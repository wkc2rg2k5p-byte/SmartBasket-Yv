"""
初始化数据库和测试数据
"""
from database import db
from config import AVATAR_COLORS

def init_test_data():
    print("开始初始化测试数据...")
    
    # 检查是否已存在家庭
    existing_family = db.get_family_by_name("相亲相爱一家人")
    if existing_family:
        print("数据已存在，跳过初始化")
        return
    
    # 创建家庭
    family_id = db.create_family("相亲相爱一家人")
    print(f"✓ 创建家庭：相亲相爱一家人 (ID: {family_id})")
    
    # 创建成员（显式指定密码）
    members = [
        {
            'username': 'mama',
            'name': '奶奶',
            'password': '123456',
            'gender': '女',
            'age': 68,
            'height': 158.0,
            'weight': 60.0,
            'diseases': ['高血压'],
            'allergies': [],
            'likes': ['清淡', '鱼', '软烂'],
            'dislikes': ['咸', '辣', '硬'],
            'goal': '控制血压',
            'avatar_color': AVATAR_COLORS[0]
        },
        {
            'username': 'momo',
            'name': '妈妈',
            'password': '123456',
            'gender': '女',
            'age': 38,
            'height': 163.0,
            'weight': 55.0,
            'diseases': [],
            'allergies': [],
            'likes': ['甜', '蔬菜', '水果'],
            'dislikes': ['香菜', '肥肉'],
            'goal': '保持身材',
            'avatar_color': AVATAR_COLORS[1]
        },
        {
            'username': 'meme',
            'name': '女儿',
            'password': '123456',
            'gender': '女',
            'age': 10,
            'height': 138.0,
            'weight': 30.0,
            'diseases': [],
            'allergies': ['海鲜'],
            'likes': ['肉', '甜', '鸡蛋'],
            'dislikes': ['苦瓜', '芹菜', '香菇'],
            'goal': '长身体',
            'avatar_color': AVATAR_COLORS[2]
        }
    ]
    
    for m in members:
        user_id = db.create_user(
            username=m['username'],
            name=m['name'],
            family_id=family_id,
            password=m['password'],
            gender=m['gender'],
            age=m['age'],
            height=m['height'],
            weight=m['weight'],
            diseases=m['diseases'],
            allergies=m['allergies'],
            likes=m['likes'],
            dislikes=m['dislikes'],
            goal=m['goal'],
            avatar_color=m['avatar_color']
        )
        print(f"✓ 创建用户：{m['name']} (登录名: {m['username']})")
    
    # 添加示例聊天记录
    messages = [
        ("奶奶", "今晚想吃点清淡的，奶奶血压高不能吃太咸"),
        ("妈妈", "做个鱼怎么样？孩子需要补充营养"),
        ("女儿", "我想吃肉！但不要海鲜，我过敏"),
        ("奶奶", "那清蒸鲈鱼吧，清淡又有营养"),
        ("妈妈", "再炒个青菜搭配一下"),
        ("女儿", "好的！我还想吃西红柿炒蛋")
    ]
    
    # 获取用户ID映射
    users = db.get_family_members(family_id)
    name_to_id = {u['name']: u['id'] for u in users}
    
    for name, msg in messages:
        user_id = name_to_id.get(name, users[0]['id'])
        db.add_chat_message(family_id, user_id, msg)
    
    print("✓ 添加示例聊天记录")
    print("\n" + "=" * 60)
    print("初始化完成！请运行 python app.py 启动系统")
    print("登录账号: mama / momo / meme")
    print("密码: 123456")
    print("=" * 60)

if __name__ == '__main__':
    init_test_data()