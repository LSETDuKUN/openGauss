import psycopg2
from config import DB_CONFIG


class Database:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            print("成功连接到数据库")
        except psycopg2.Error as e:
            print(f"数据库连接失败: {e}")

    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            else:
                self.connection.commit()
                return cursor.rowcount
        except psycopg2.Error as e:
            print(f"查询执行失败: {e}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()

    def close(self):
        if self.connection:
            self.connection.close()