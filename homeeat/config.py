"""
HomeEat 配置文件
"""
import os

# 数据库路径（自动在当前目录创建）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'homeeat.db')

# Flask 配置
SECRET_KEY = 'homeeat-secret-key-2026'
HOST = '0.0.0.0'  # 允许局域网访问，方便演示多用户
PORT = 5000
DEBUG = True

# 智谱AI 配置（已填写API Key）
OPENAI_API_KEY = '7888abfec6244444ae3eeb42e44332a9.zMRYQmetj5RGdRjP'
OPENAI_BASE_URL = 'https://open.bigmodel.cn/api/paas/v4/'
USE_MOCK_AI = False   # 使用真实AI

# 头像颜色
AVATAR_COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']