import sqlite3
from sqlite3 import Error

def create_menu_class_db():
    conn = None
    try:
        conn = sqlite3.connect('systemdb/menu_class.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 檢查 'menu_class' 表是否已經存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='menu_class'")
        if cursor.fetchone() is None:
            # 如果 'menu_class' 表不存在，則創建它
            cursor.execute('''
                CREATE TABLE menu_class (
                    order_id INT NOT NULL,
                    id TEXT NOT NULL,
                    menu_class TEXT NOT NULL
                )
            ''')

    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()  # 關閉資料庫連接