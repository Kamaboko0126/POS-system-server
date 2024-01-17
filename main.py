import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from admin import create_admin_db
from menu_class import create_menu_class_db
import sqlite3
import os

create_admin_db()
create_menu_class_db()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginData(BaseModel):
    Account: str
    Password: str

class MenuClass(BaseModel):
    MenuClass: str

@app.post("/login")
def login(data: LoginData):
    conn = None
    try:
        conn = sqlite3.connect('admin.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 從 'admin' 表中獲取帳號和密碼
        cursor.execute("SELECT Account, Password FROM admin WHERE Account = ?", (data.Account,))
        row = cursor.fetchone()

        if row is None or row[1] != data.Password:
            # 如果帳號不存在，或者密碼不正確，則返回錯誤訊息
            return JSONResponse({"message": "failed"})
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()  # 關閉資料庫連接

    return JSONResponse({"message": "success"})

@app.get("/getmenuclass")
def getmenuclass():
    conn = None
    try:
        conn = sqlite3.connect('menu_class.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 查詢 'menu-class' 表中的所有 MenuClass
        cursor.execute("SELECT MenuClass FROM 'menu_class'")
        menu_classes = cursor.fetchall()

        print(JSONResponse({"MenuClasses": [menu_class[0] for menu_class in menu_classes]}))
        # 將結果轉換為 JSON 格式
        return JSONResponse({"MenuClasses": [menu_class[0] for menu_class in menu_classes]})
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()  # 關閉資料庫連接

@app.post("/addmenuclass")
def addmenuclass(data: MenuClass):
    conn = None
    try:
        conn = sqlite3.connect('menu_class.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 檢查 'menu-class' 表中是否已經存在該 MenuClass
        cursor.execute("SELECT MenuClass FROM 'menu_class' WHERE MenuClass = ?", (data.MenuClass,))
        if cursor.fetchone() is None:
            # 如果不存在，則插入新的 MenuClass
            cursor.execute("INSERT INTO 'menu_class' (MenuClass) VALUES (?)", (data.MenuClass,))
            conn.commit()  # 提交事務

             # 在 'menus.db' 中創建一個新的表
            new_db_conn = sqlite3.connect('menus.db')
            new_db_cursor = new_db_conn.cursor()
            new_db_cursor.execute(f'''
                CREATE TABLE {data.MenuClass} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL
                )
            ''')
            new_db_conn.commit()
            new_db_conn.close()


            return JSONResponse({"message": "success"})
        else:
            return JSONResponse({"message": "already exists"})
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()  # 關閉資料庫連接


@app.post("/delmenuclass")
def delmenuclass(data: MenuClass):
    conn = None
    try:
        conn = sqlite3.connect('menu_class.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 檢查 'menu_class' 表中是否已經存在該 MenuClass
        cursor.execute("SELECT MenuClass FROM 'menu_class' WHERE MenuClass = ?", (data.MenuClass,))
        if cursor.fetchone() is not None:
            # 如果存在，則刪除該 MenuClass
            cursor.execute("DELETE FROM 'menu_class' WHERE MenuClass = ?", (data.MenuClass,))
            conn.commit()  # 提交事務

            # 在 'menus.db' 中刪除一個表
            new_db_conn = sqlite3.connect('menus.db')
            new_db_cursor = new_db_conn.cursor()
            new_db_cursor.execute(f"DROP TABLE IF EXISTS {data.MenuClass}")
            new_db_conn.commit()
            new_db_conn.close()

            return JSONResponse({"message": "success"})
        else:
            return JSONResponse({"message": "not exist"})
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()  # 關閉資料庫連接

if __name__ == "__main__":
    uvicorn.run(app, port=10000)
