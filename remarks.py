import sqlite3
from sqlite3 import Error


def create_remarks_db():
    conn = None
    try:
        conn = sqlite3.connect('reamrks.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 檢查 'remarks' 表是否已經存在
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='remarks'")
        if cursor.fetchone() is None:
            # 如果 'remarks' 表不存在，則創建它
            cursor.execute('''
                CREATE TABLE remarks (
                    id TEXT NOT NULL,
                    data TEXT NOT NULL
                )
            ''')

    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()  # 關閉資料庫連接
