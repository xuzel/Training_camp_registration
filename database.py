"""
数据库模型和连接配置
"""

import sqlite3
from datetime import datetime
from typing import Optional, List
import json

class DatabaseManager:
    """数据库管理类"""

    def __init__(self, db_path: str = "training_camp.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建报名表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                wechat TEXT NOT NULL,
                email TEXT NOT NULL,
                occupation TEXT NOT NULL,
                attendance_days TEXT NOT NULL,
                backup_plan TEXT NOT NULL,
                experience TEXT NOT NULL,
                goal TEXT NOT NULL,
                competition_experience TEXT NOT NULL,
                comp_category TEXT,
                injury_history TEXT NOT NULL,
                questions TEXT,
                channel TEXT NOT NULL,
                products TEXT,
                future_services TEXT,
                agree_terms BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 检查是否需要更新feedback表结构
        cursor.execute("PRAGMA table_info(feedback)")
        columns = [column[1] for column in cursor.fetchall()]

        # 如果表不存在或字段不匹配，重新创建
        expected_columns = [
            'id', 'knowledge_improvement', 'technique_understanding', 'planning_ability',
            'confidence_boost', 'instructor_satisfaction', 'materials_satisfaction',
            'venue_satisfaction', 'suggestions', 'desired_products', 'desired_services', 'created_at'
        ]

        if not all(col in columns for col in expected_columns):
            # 备份旧数据（如果存在）
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'")
            if cursor.fetchone():
                cursor.execute("ALTER TABLE feedback RENAME TO feedback_old")

            # 创建新的满意度反馈表
            cursor.execute('''
                CREATE TABLE feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    knowledge_improvement INTEGER NOT NULL,
                    technique_understanding INTEGER NOT NULL,
                    planning_ability INTEGER NOT NULL,
                    confidence_boost INTEGER NOT NULL,
                    instructor_satisfaction INTEGER NOT NULL,
                    materials_satisfaction INTEGER NOT NULL,
                    venue_satisfaction INTEGER NOT NULL,
                    suggestions TEXT,
                    desired_products TEXT,
                    desired_services TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        conn.commit()
        conn.close()

    def insert_feedback(self, feedback_data: dict) -> bool:
        """插入反馈数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO feedback (
                    knowledge_improvement, technique_understanding, planning_ability,
                    confidence_boost, instructor_satisfaction, materials_satisfaction,
                    venue_satisfaction, suggestions, desired_products, desired_services
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                feedback_data['knowledge_improvement'],
                feedback_data['technique_understanding'],
                feedback_data['planning_ability'],
                feedback_data['confidence_boost'],
                feedback_data['instructor_satisfaction'],
                feedback_data['materials_satisfaction'],
                feedback_data['venue_satisfaction'],
                feedback_data.get('suggestions', ''),
                feedback_data.get('desired_products', ''),
                feedback_data.get('desired_services', '')
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"反馈数据插入错误: {e}")
            return False

    def get_all_feedback(self) -> List[dict]:
        """获取所有反馈数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM feedback ORDER BY created_at DESC')
            rows = cursor.fetchall()

            feedback_list = []
            for row in rows:
                feedback_list.append(dict(row))

            conn.close()
            return feedback_list

        except Exception as e:
            print(f"反馈数据查询错误: {e}")
            return []

    def get_feedback_by_id(self, feedback_id: int) -> Optional[dict]:
        """根据ID获取反馈数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM feedback WHERE id = ?', (feedback_id,))
            row = cursor.fetchone()

            if row:
                conn.close()
                return dict(row)

            conn.close()
            return None

        except Exception as e:
            print(f"反馈数据查询错误: {e}")
            return None

    def delete_feedback_by_ids(self, feedback_ids: List[int]) -> bool:
        """根据ID列表删除反馈数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 构建SQL语句
            placeholders = ','.join(['?' for _ in feedback_ids])
            cursor.execute(f'DELETE FROM feedback WHERE id IN ({placeholders})', feedback_ids)

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"反馈数据删除错误: {e}")
            return False

    def insert_registration(self, registration_data: dict) -> bool:
        """插入报名数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO registrations (
                    full_name, phone, wechat, email, occupation,
                    attendance_days, backup_plan, experience, goal,
                    competition_experience, comp_category, injury_history,
                    questions, channel, products, future_services, agree_terms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                registration_data['full_name'],
                registration_data['phone'],
                registration_data['wechat'],
                registration_data['email'],
                registration_data['occupation'],
                json.dumps(registration_data.get('attendance_days', [])),
                registration_data['backup_plan'],
                registration_data['experience'],
                registration_data['goal'],
                registration_data['competition_experience'],
                registration_data.get('comp_category', ''),
                registration_data['injury_history'],
                registration_data.get('questions', ''),
                registration_data['channel'],
                registration_data.get('products', ''),
                registration_data.get('future_services', ''),
                registration_data.get('agree_terms', False)
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"数据库插入错误: {e}")
            return False

    def get_all_registrations(self) -> List[dict]:
        """获取所有报名数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM registrations ORDER BY created_at DESC')
            rows = cursor.fetchall()

            registrations = []
            for row in rows:
                reg = dict(row)
                # 解析attendance_days JSON
                try:
                    reg['attendance_days'] = json.loads(reg['attendance_days'])
                except:
                    reg['attendance_days'] = []
                registrations.append(reg)

            conn.close()
            return registrations

        except Exception as e:
            print(f"数据库查询错误: {e}")
            return []

    def get_registration_by_id(self, registration_id: int) -> Optional[dict]:
        """根据ID获取报名数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM registrations WHERE id = ?', (registration_id,))
            row = cursor.fetchone()

            if row:
                reg = dict(row)
                reg['attendance_days'] = json.loads(reg['attendance_days'])
                conn.close()
                return reg

            conn.close()
            return None

        except Exception as e:
            print(f"数据库查询错误: {e}")
            return None

    def delete_registrations_by_ids(self, registration_ids: List[int]) -> bool:
        """根据ID列表删除报名数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 构建SQL语句
            placeholders = ','.join(['?' for _ in registration_ids])
            cursor.execute(f'DELETE FROM registrations WHERE id IN ({placeholders})', registration_ids)

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"报名数据删除错误: {e}")
            return False

# 创建全局数据库实例
db_manager = DatabaseManager()