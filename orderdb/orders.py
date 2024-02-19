import sqlite3
from sqlite3 import Error
from datetime import datetime

def create_orders_db():
    conn = None
    try:
        conn = sqlite3.connect('orderdb/orders.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 獲取當前日期
        current_date = datetime.now().strftime('%Y%m%d')

        # 建立表名
        table_id = 'd' + current_date

        # 創建表
        cursor.execute(f'''
                       CREATE TABLE IF NOT EXISTS {table_id}(
                        index_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        is_discount BOOLEAN,
                        lists TEXT,
                        order_id TEXT,
                        order_time TEXT,
                        pick_up_time TEXT,
                        ordering_method TEXT,
                        payment TEXT,
                        phone TEXT,
                        is_finished BOOLEAN DEFAULT FALSE
                        )
                    ''')

        # 提交更改
        conn.commit()

    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()  # 關閉資料庫連接