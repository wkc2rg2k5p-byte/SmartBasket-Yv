import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'homeeat-secret-key-2024')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'homeeat.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # AI API Configuration (可配置真实API)
    AI_API_KEY = os.environ.get('AI_API_KEY', 'ak_1Kh8jA3OR92y8ng5ii4hc4WF83D2d')
    AI_API_URL = os.environ.get('AI_API_URL', 'https://api.longcat.chat/openai/v1/chat/completions')
    AI_MODEL = os.environ.get('AI_MODEL', 'LongCat-Flash-Chat')
