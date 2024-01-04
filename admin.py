import sqlite3
from sqlite3 import Error

def create_admin_db():
    conn = None
    try:
        conn = sqlite3.connect('admin.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 檢查 'admin' 表是否已經存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin'")
        if cursor.fetchone() is None:
            # 如果 'admin' 表不存在，則創建它
            cursor.execute('''
                CREATE TABLE admin (
                    Account TEXT NOT NULL,
                    Password TEXT NOT NULL
                )
            ''')

            # 插入一組帳號和密碼
            cursor.execute("INSERT INTO admin (Account, Password) VALUES (?, ?)", ('admin', 'admin'))
            conn.commit()  # 提交事務
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()  # 關閉資料庫連接