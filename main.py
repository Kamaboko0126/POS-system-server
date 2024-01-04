import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from admin import create_admin_db
import sqlite3

create_admin_db()

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
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()  # 關閉資料庫連接

    return JSONResponse({"message": "success"})

if __name__ == "__main__":
    uvicorn.run(app, port=10000)
