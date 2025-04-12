import psycopg2
from psycopg2 import sql
from config import DB_CONFIG


class Database:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            # 设置连接参数（关键修复）
            self.connection.set_session(autocommit=False)  # 关闭自动提交
            print("成功连接到数据库")
        except psycopg2.Error as e:
            print(f"数据库连接失败: {e}")
            raise  # 抛出异常让调用方处理

    def execute_query(self, query, params=None):
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())

            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            else:
                self.connection.commit()  # 显式提交
                return cursor.rowcount

        except psycopg2.Error as e:
            print(f"查询执行失败: {e}")
            if self.connection:
                self.connection.rollback()  # 关键修复：必须回滚
            return None
        finally:
            if cursor:
                cursor.close()

    def close(self):
        if self.connection and not self.connection.closed:
            self.connection.close()
            print("数据库连接已关闭")

    # 新增安全执行方法（推荐使用）
    def safe_execute(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:  # 自动管理游标
                cursor.execute(query, params or ())
                if query.strip().upper().startswith("SELECT"):
                    return cursor.fetchall()
                self.connection.commit()
                return cursor.rowcount
        except psycopg2.Error as e:
            print(f"安全执行失败: {e}")
            self.connection.rollback()
            return None