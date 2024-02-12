import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
# from systemdb.admin import create_admin_db
from systemdb.menu_class import create_menu_class_db
from orderdb.orders import create_orders_db
import sqlite3
import json
from datetime import datetime
import asyncio

# create_admin_db()
create_menu_class_db()
create_orders_db()

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


class ChangeClassOrder(BaseModel):
    data: str


class Item(BaseModel):
    id: str
    name: str
    price: int
    marker: str
    order_id: int


class AddItem(BaseModel):
    table_id: str
    id: str
    name: str
    price: int
    marker: str
    order_id: int

class EditItem(BaseModel):
    table_id: str
    id: str
    name: str
    price: int


class AddMarker(BaseModel):
    table_id: str
    item_id: str
    marker: str

class ChangeItemOrder(BaseModel):
    table_id: str
    data: str


# class OrderList(BaseModel):
#     id:str
#     markers:str
#     name:str
#     price:int
#     quantity:int

class AddOrder(BaseModel):
    is_discount:bool
    lists:str
    order_id:str
    ordering_method:str
    payment:str
    phone:str

class EventBus:
    def __init__(self):
        self._subscribers = set()

    async def publish(self, message):
        for subscriber in self._subscribers:
            await subscriber.put(message)

    def subscribe(self):
        queue = asyncio.Queue()
        self._subscribers.add(queue)
        return queue

event_bus = EventBus()

# 登入
# def execute_db_query(query, params):
#     conn = sqlite3.connect('system/admin.db')
#     cursor = conn.cursor()
#     cursor.execute(query, params)
#     result = cursor.fetchone()
#     conn.close()
#     return result

# @app.post("/admin/login")
# def login(data: LoginData):
#     row = execute_db_query(
#         "SELECT Account, Password FROM admin WHERE Account = ?",
#         (data.Account,)
#     )

#     if row is None or row[1] != data.Password:
#         raise HTTPException(status_code=400, detail="Invalid credentials")

#     return {"message": "success"}


# 取得菜單類別
@app.get("/class/get")
def getmenuclass():
    conn = None
    try:
        conn = sqlite3.connect('systemdb/menu_class.db')  # 建立資料庫連接
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
@app.post("/class/add")
def addmenuclass(data: MenuClass):
    conn = None
    try:
        conn = sqlite3.connect('systemdb/menu_class.db')  # 建立資料庫連接
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
                    marker TEXT NOT NULL,
                    order_id INTEGER NOT NULL
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
@app.delete("/class/del/{id}")
def delmenuclass(id: str):
    conn = None
    try:
        conn = sqlite3.connect('systemdb/menu_class.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 檢查 'menu_class' 表中是否存在該 id
        cursor.execute(
            "SELECT id FROM 'menu_class' WHERE id = ?", (id,))
        if cursor.fetchone() is not None:
            # 如果存在，則刪除該 MenuClass
            cursor.execute(
                "DELETE FROM 'menu_class' WHERE id = ?", (id,))
            conn.commit()  # 提交事務

            # 在 'menus.db' 中刪除一個表
            new_db_conn = sqlite3.connect('menus.db')
            new_db_cursor = new_db_conn.cursor()
            new_db_cursor.execute(f"DROP TABLE IF EXISTS {id}")
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
@app.put("/class/edit")
def editmenuclass(data: EditMenu):
    conn = None
    try:
        conn = sqlite3.connect('systemdb/menu_class.db')  # 建立資料庫連接
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
@app.put("/class/changeorder")
def changeclassorder(data: ChangeClassOrder):
    data_list = json.loads(str(data.data))
    conn = sqlite3.connect('systemdb/menu_class.db')
    cursor = conn.cursor()

    for item in data_list:
        cursor.execute(
            "UPDATE menu_class SET order_id = ? WHERE id = ?", (item['order_id'], item['id']))
        # print(f"order_id: {item['order_id']}, ID: {item['id']}")

    conn.commit()
    conn.close()

    return JSONResponse({"message": "success"})


# 取得菜單品項
@app.get("/item/get/{id}")
def get_items(id: str):
    conn = None
    try:
        conn = sqlite3.connect('systemdb/menus.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 查詢對應的表中的所有項目，並按照 order_id 進行排序
        cursor.execute(f"SELECT id, name, price, marker, order_id FROM '{id}' ORDER BY order_id")
        items = cursor.fetchall()

        # print([Item(id=item[0], name=item[1], price=item[2], marker=item[3], order_id=item[4]) for item in items])

        # 將結果轉換為 JSON 格式
        return [Item(id=item[0], name=item[1], price=item[2], marker=item[3], order_id=item[4]) for item in items]
    except sqlite3.Error as e:
        print(e)
        raise HTTPException(status_code=400, detail="Error in fetching items")
    finally:
        if conn:
            conn.close()  # 關閉資料庫連接


# 新增菜單品項
@app.post("/item/add")
def add_item(data: AddItem):
    print(data.dict())
    conn = None
    try:
        conn = sqlite3.connect('systemdb/menus.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 將新的項目插入到指定的表中
        cursor.execute(
            f"INSERT INTO '{data.table_id}' (id, name, price, marker, order_id) VALUES (?, ?, ?, ? ,?)", (data.id, data.name, data.price, data.marker, data.order_id))
        conn.commit()  # 提交事務

        return JSONResponse({"message": "success"})
    except sqlite3.Error as e:
        print(e)
        return JSONResponse({"message": "failed"})
    finally:
        if conn:
            conn.close()  # 關閉資料庫連接


# 刪除菜單品項
@app.delete("/item/del")
def del_item(table_id: str, id: str):
    conn = None
    try:
        conn = sqlite3.connect('systemdb/menus.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 將新的項目插入到指定的表中
        cursor.execute(
            f"DELETE FROM '{table_id}' WHERE id = ?", (id,))
        conn.commit()  # 提交事務

        return JSONResponse({"message": "success"})
    except sqlite3.Error as e:
        print(e)
        return JSONResponse({"message": "failed"})
    finally:
        if conn:
            conn.close()

#編輯菜單品項
@app.put("/item/edit")
def edit_item(data: EditItem):
    conn = None
    try:
        conn = sqlite3.connect('systemdb/menus.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象
        cursor.execute(f"""
            UPDATE {data.table_id}
            SET name = ?, price = ?
            WHERE id = ?
        """, (data.name, data.price, data.id))

        conn.commit()

        if cursor.rowcount > 0:
            return JSONResponse({"message": "success"})
        else:
            return JSONResponse({"message": "not exist"})
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()  # 關閉資料庫連接

# 修改品項順序
@app.put("/item/changeorder")
def changeitemorder(data: ChangeItemOrder):
    data_list = json.loads(str(data.data))
    conn = sqlite3.connect('systemdb/menus.db')
    cursor = conn.cursor()

    for item in data_list:
        cursor.execute(
            f'''UPDATE {data.table_id} SET order_id = ? WHERE id = ?''', (item['order_id'], item['id']))
        print(f"order_id: {item['order_id']}, ID: {item['id']}")


    conn.commit()
    conn.close()

    return JSONResponse({"message": "success"})

# 新增備註
@app.post("/marker/add")
def addmarker(data: AddMarker):
    conn=None
    try:
        conn = sqlite3.connect('systemdb/menus.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象
        cursor.execute(f"""
            UPDATE {data.table_id}
            SET marker = ?
            WHERE id = ?
        """, (data.marker, data.item_id))

        conn.commit()

        if cursor.rowcount > 0:
            return JSONResponse({"message": "success"})
        else:
            return JSONResponse({"message": "not exist"})
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()  # 關閉資料庫連接


@app.get("/orderlist/get/{id}")
def get_list_order(id:str):
    conn = None
    try:
        conn = sqlite3.connect('orderdb/orders.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 執行 SQL 查詢
        cursor.execute(f"SELECT * FROM '{id}'")

        # 獲取所有資料
        datas = cursor.fetchall()

        response = JSONResponse(
            [{"index_id": data[0], "is_discount": bool(data[1]), "lists": data[2], "order_id": data[3], "ordering_method": data[4], "payment": data[5], "phone": data[6], "is_finished": bool(data[7])} for data in datas])
        return response

    except sqlite3.Error as e:
        print(e)
        raise HTTPException(status_code=400, detail="Error in fetching items")
    finally:
        if conn:
            conn.close()

#新增訂單
@app.post("/order/add")
async def add_order(data: AddOrder):
    conn = None
    try:
        conn = sqlite3.connect('orderdb/orders.db')  # 建立資料庫連接
        cursor = conn.cursor()  # 建立游標對象

        # 獲取當前日期
        current_date = datetime.now().strftime('%Y%m%d')
        # 建立表名
        table_id = 'd' + current_date

        # 插入數據
        cursor.execute(
            f"INSERT INTO '{table_id}' (is_discount, lists, order_id, ordering_method, payment, phone) VALUES (?, ?, ?, ? ,?, ?)"
                , (data.is_discount, data.lists, data.order_id, data.ordering_method, data.payment, data.phone))

        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()  # 關閉資料庫連接

    # print(data.dict())
    asyncio.create_task(event_bus.publish("Order added"))
    return JSONResponse({"message": "success"})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    queue = event_bus.subscribe()
    try:
        while True:
            message = await queue.get()
            await websocket.send_text(message)
    finally:
        event_bus._subscribers.remove(queue)


if __name__ == "__main__":
    uvicorn.run(app, port=10000)
