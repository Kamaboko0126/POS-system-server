import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from admin import create_admin_db
from menu_class import create_menu_class_db
from remarks import create_remarks_db
import sqlite3
import json

create_admin_db()
create_menu_class_db()
create_remarks_db()

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
    order_id: int
    menu_class: str
    id: str


class EditMenu(BaseModel):
    id: str
    menu_class: str


class DelClass(BaseModel):
    id: str


class ChangeClassOrder(BaseModel):
    data: str


class Item(BaseModel):
    id: str
    name: str
    price: int


class AddItem(BaseModel):
    table_id: str
    id: str
    name: str
    price: int
    marker: str


class DelItem(BaseModel):
    table_id: str
    id: str


# class Remark(BaseModel):
#     id: str
#     name: str


# 登入
@app.post("/login")
def login(data: LoginData):
    conn = None
    try:
        conn = sqlite3.connect('admin.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 從 'admin' 表中獲取帳號和密碼
        cursor.execute(
            "SELECT Account, Password FROM admin WHERE Account = ?", (data.Account,))
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


# 取得菜單類別
@app.get("/getmenuclass")
def getmenuclass():
    conn = None
    try:
        conn = sqlite3.connect('menu_class.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 查詢 'menu-class' 表中的所有 MenuClass
        cursor.execute(
            "SELECT menu_class, id FROM 'menu_class' ORDER BY order_id ")
        menu_classes = cursor.fetchall()

        # 將結果轉換為 JSON 格式
        response = JSONResponse(
            {"MenuClasses": [{"menu_class": menu_class[0], "id": menu_class[1]} for menu_class in menu_classes]})
        return response

    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()  # 關閉資料庫連接


# 新增菜單類別
@app.post("/addmenuclass")
def addmenuclass(data: MenuClass):
    conn = None
    try:
        conn = sqlite3.connect('menu_class.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 檢查 'menu-class' 表中是否已經存在該 MenuClass
        cursor.execute(
            "SELECT id FROM 'menu_class' WHERE id = ?", (data.id,))
        if cursor.fetchone() is None:
            # 如果不存在，則插入新的 MenuClass
            cursor.execute(
                "INSERT INTO 'menu_class' (order_id, menu_class, id) VALUES (?, ?, ?)", (data.order_id, data.menu_class, data.id))
            conn.commit()  # 提交事務
            print(data.menu_class, data.id)

            # 在 'menus.db' 中創建一個新的表
            new_db_conn = sqlite3.connect('menus.db')
            new_db_cursor = new_db_conn.cursor()
            new_db_cursor.execute(f'''
                CREATE TABLE {data.id} (
                    id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    marker TEXT
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


# 刪除菜單類別
@app.post("/delmenuclass")
def delmenuclass(data: DelClass):
    conn = None
    try:
        conn = sqlite3.connect('menu_class.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 檢查 'menu_class' 表中是否存在該 id
        cursor.execute(
            "SELECT id FROM 'menu_class' WHERE id = ?", (data.id,))
        if cursor.fetchone() is not None:
            # 如果存在，則刪除該 MenuClass
            cursor.execute(
                "DELETE FROM 'menu_class' WHERE id = ?", (data.id,))
            conn.commit()  # 提交事務

            # 在 'menus.db' 中刪除一個表
            new_db_conn = sqlite3.connect('menus.db')
            new_db_cursor = new_db_conn.cursor()
            new_db_cursor.execute(f"DROP TABLE IF EXISTS {data.id}")
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


# 修改菜單類別
@app.post("/editmenuclass")
def editmenuclass(data: EditMenu):
    conn = None
    try:
        conn = sqlite3.connect('menu_class.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 更新 'menu_class' 表中的 menu_class
        cursor.execute(
            "UPDATE 'menu_class' SET menu_class = ? WHERE id = ?", (data.menu_class, data.id))
        conn.commit()  # 提交事務

        # 檢查是否有資料被更新
        if cursor.rowcount > 0:
            return JSONResponse({"message": "success"})
        else:
            return JSONResponse({"message": "failed"})
    except sqlite3.Error as e:
        print(e)
        return JSONResponse({"message": "failed"})
    finally:
        if conn:
            conn.close()  # 關閉資料庫連接


# 變更類別順序
@app.post("/changeclassorder")
def changeclassorder(data: ChangeClassOrder):
    data_list = json.loads(str(data.data))
    conn = sqlite3.connect('menu_class.db')
    cursor = conn.cursor()

    for item in data_list:
        cursor.execute(
            "UPDATE menu_class SET order_id = ? WHERE id = ?", (item['order_id'], item['id']))
        print(f"order_id: {item['order_id']}, ID: {item['id']}")

    conn.commit()
    conn.close()

    return JSONResponse({"message": "success"})


# 取得菜單項目
@app.get("/getitems/{id}")
def get_items(id: str):
    conn = None
    try:
        conn = sqlite3.connect('menus.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 查詢對應的表中的所有項目
        cursor.execute(f"SELECT id, name, price, marker FROM '{id}'")
        items = cursor.fetchall()

        # 將結果轉換為 JSON 格式
        return [Item(id=item[0], name=item[1], price=item[2], marker=item[3]) for item in items]
    except sqlite3.Error as e:
        print(e)
        raise HTTPException(status_code=400, detail="Error in fetching items")
    finally:
        if conn:
            conn.close()  # 關閉資料庫連接


# 新增菜單項目
@app.post("/additem")
def add_item(data: AddItem):
    conn = None
    try:
        conn = sqlite3.connect('menus.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 將新的項目插入到指定的表中
        cursor.execute(
            f"INSERT INTO '{data.table_id}' (id, name, price, marker) VALUES (?, ?, ?, ?)", (data.id, data.name, data.price, data.marker))
        conn.commit()  # 提交事務

        return JSONResponse({"message": "success"})
    except sqlite3.Error as e:
        print(e)
        return JSONResponse({"message": "failed"})
    finally:
        if conn:
            conn.close()  # 關閉資料庫連接


# 刪除菜單項目
@app.post("/delitem")
def del_item(data: DelItem):
    conn = None
    try:
        conn = sqlite3.connect('menus.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 將新的項目插入到指定的表中
        cursor.execute(
            f"DELETE FROM '{data.table_id}' WHERE id = ?", (data.id,))
        conn.commit()  # 提交事務

        return JSONResponse({"message": "success"})
    except sqlite3.Error as e:
        print(e)
        return JSONResponse({"message": "failed"})
    finally:
        if conn:
            conn.close()



# # 取得所有的備註
# @app.get("/getremarks")
# def get_remarks():
#     conn = None
#     try:
#         conn = sqlite3.connect('remarks.db')  # 建立資料庫連接
#         cursor = conn.cursor()  # 建立游標對象

#         # 從 SQLite 數據庫中讀取所有的 remarks
#         cursor.execute('SELECT * FROM remarks')
#         rows = cursor.fetchall()

#         # 將結果轉換為 JSON 格式
#         remarks = [{"id": row[0], "name": row[1]} for row in rows]
#         return JSONResponse({"remarks": remarks})

#     except sqlite3.Error as e:
#         print(e)
#     finally:
#         if conn:
#             conn.close()  # 關閉資料庫連接


# # 新增備註
# @app.post("/addremark")
# def addremark(data: Remark):
#     conn = None
#     try:
#         conn = sqlite3.connect('remarks.db')  # 建立資料庫連接
#         cursor = conn.cursor()  # 建立游標對象

#         # 檢查 'remarks' 表中是否已經存在該 remark
#         cursor.execute(
#             "SELECT id FROM 'remarks' WHERE id = ?", (data.id,))
#         if cursor.fetchone() is None:
#             # 如果不存在，則插入新的 MenuClass
#             cursor.execute(
#                 "INSERT INTO 'remarks' (id, data) VALUES (?, ?)", (data.id, data.data))
#             conn.commit()  # 提交事務

#             return JSONResponse({"message": "success"})
#         else:
#             return JSONResponse({"message": "already exists"})
#     except sqlite3.Error as e:
#         print(e)
#     finally:
#         if conn:
#             conn.close()  # 關閉資料庫連接


if __name__ == "__main__":
    uvicorn.run(app, port=10000)
