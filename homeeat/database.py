"""
数据库模块 - SQLite
"""
import sqlite3
import json
from datetime import datetime, timedelta
from config import DATABASE_PATH

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 家庭表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS family (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT DEFAULT '123456',
                name TEXT NOT NULL,
                gender TEXT,
                age INTEGER,
                height REAL,
                weight REAL,
                diseases TEXT,
                allergies TEXT,
                likes TEXT,
                dislikes TEXT,
                goal TEXT,
                avatar_color TEXT DEFAULT '#667eea',
                family_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (family_id) REFERENCES family(id)
            )
        ''')
        
        # 聊天记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id INTEGER NOT NULL,
                user_id INTEGER,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (family_id) REFERENCES family(id),
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        ''')
        
        # 菜谱记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipe_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id INTEGER NOT NULL,
                date DATE NOT NULL,
                recipes_json TEXT NOT NULL,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (family_id) REFERENCES family(id)
            )
        ''')
        
        # 采购清单表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shopping_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id INTEGER NOT NULL,
                date DATE NOT NULL,
                items_json TEXT NOT NULL,
                is_completed BOOLEAN DEFAULT 0,
                FOREIGN KEY (family_id) REFERENCES family(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("数据库初始化完成")
    
    def get_family_by_name(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM family WHERE name = ?', (name,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def create_family(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO family (name) VALUES (?)', (name,))
        family_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return family_id
    
    def get_family(self, family_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM family WHERE id = ?', (family_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    
    def create_user(self, username, name, family_id, **kwargs):
        conn = self.get_connection()
        cursor = conn.cursor()
    
        # 处理JSON字段：将列表转换为JSON字符串（包括空列表）
        for field in ['diseases', 'allergies', 'likes', 'dislikes']:
            if field in kwargs:
                kwargs[field] = json.dumps(kwargs[field], ensure_ascii=False)
            else:
                kwargs[field] = '[]'  # 如果未提供，默认空列表
    
        fields = ['username', 'name', 'family_id'] + list(kwargs.keys())
        values = [username, name, family_id] + list(kwargs.values())
        placeholders = ', '.join(['?' for _ in fields])
    
        query = f'INSERT INTO user ({",".join(fields)}) VALUES ({placeholders})'
        cursor.execute(query, values)
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    def get_user_by_username(self, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            user = dict(result)
            for field in ['diseases', 'allergies', 'likes', 'dislikes']:
                if user.get(field):
                    try:
                        user[field] = json.loads(user[field])
                    except:
                        user[field] = []
            return user
        return None
    
    def get_family_members(self, family_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE family_id = ?', (family_id,))
        results = cursor.fetchall()
        conn.close()
        
        members = []
        for row in results:
            member = dict(row)
            for field in ['diseases', 'allergies', 'likes', 'dislikes']:
                if member.get(field):
                    try:
                        member[field] = json.loads(member[field])
                    except:
                        member[field] = []
            members.append(member)
        return members
    
    def add_chat_message(self, family_id, user_id, message):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO chat_history (family_id, user_id, message) VALUES (?, ?, ?)',
            (family_id, user_id, message)
        )
        conn.commit()
        conn.close()
    
    def get_chat_history(self, family_id, limit=50):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*, u.name as user_name, u.avatar_color 
            FROM chat_history c 
            LEFT JOIN user u ON c.user_id = u.id 
            WHERE c.family_id = ? 
            ORDER BY c.timestamp DESC 
            LIMIT ?
        ''', (family_id, limit))
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in reversed(results)]
    
    def clear_chat_history(self, family_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM chat_history WHERE family_id = ?', (family_id,))
        conn.commit()
        conn.close()
    
    def save_recipe(self, family_id, date, recipes, created_by):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO recipe_record (family_id, date, recipes_json, created_by) VALUES (?, ?, ?, ?)',
            (family_id, date, json.dumps(recipes, ensure_ascii=False), created_by)
        )
        conn.commit()
        conn.close()
    
    def get_recipe_by_date(self, family_id, date):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM recipe_record WHERE family_id = ? AND date = ?', (family_id, date))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            record = dict(result)
            record['recipes'] = json.loads(record['recipes_json'])
            return record
        return None
    
    def get_recipe_history(self, family_id, limit=30):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM recipe_record WHERE family_id = ? ORDER BY date DESC LIMIT ?',
            (family_id, limit)
        )
        results = cursor.fetchall()
        conn.close()
        
        records = []
        for row in results:
            record = dict(row)
            record['recipes'] = json.loads(record['recipes_json'])
            records.append(record)
        return records
    
    def save_shopping_list(self, family_id, date, items):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM shopping_list WHERE family_id = ? AND date = ?', (family_id, date))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('UPDATE shopping_list SET items_json = ? WHERE id = ?',
                         (json.dumps(items, ensure_ascii=False), existing['id']))
        else:
            cursor.execute('INSERT INTO shopping_list (family_id, date, items_json) VALUES (?, ?, ?)',
                         (family_id, date, json.dumps(items, ensure_ascii=False)))
        
        conn.commit()
        conn.close()
    
    def get_shopping_list(self, family_id, date):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM shopping_list WHERE family_id = ? AND date = ?', (family_id, date))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            record = dict(result)
            record['items'] = json.loads(record['items_json'])
            return record
        return None
    
    def get_weekly_stats(self, family_id, end_date=None):
        if end_date is None:
            end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM recipe_record 
            WHERE family_id = ? AND date >= ? AND date <= ?
            ORDER BY date DESC
        ''', (family_id, start_date, end_date))
        
        results = cursor.fetchall()
        conn.close()
        
        records = []
        all_dishes = []
        for row in results:
            record = dict(row)
            record['recipes'] = json.loads(record['recipes_json'])
            records.append(record)
            for dish in record['recipes'].get('dishes', []):
                all_dishes.append(dish['name'])
        
        dish_count = {}
        for dish in all_dishes:
            dish_count[dish] = dish_count.get(dish, 0) + 1
        
        return {
            'start_date': str(start_date),
            'end_date': str(end_date),
            'total_meals': len(records),
            'dish_ranking': sorted(dish_count.items(), key=lambda x: x[1], reverse=True)[:10],
            'records': records
        }

db = Database()