
from fastapi import FastAPI
import pymysql

from fastapi.middleware.cors import CORSMiddleware
from routers import client, order, order_items, reservation, payment, product, stock, table
app = FastAPI(title="Qrcode Order System")

# --- Allow frontend access ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MySQL Connection ---
DB = pymysql.connect(
    host="localhost",
    user="root",
    passwd="Bineli26",
    database="Order_System",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=False  # turn off auto-commit for transaction safety
)

app.include_router(client.router, prefix="/client", tags=["client"])
app.include_router(order.router, prefix="/order", tags=["order"])
app.include_router(order_items.router, prefix="/order_items", tags=["order_items"])
app.include_router(reservation.router, prefix="/reservation", tags=["reservation"])
app.include_router(product.router, prefix="/product", tags=["product"])
app.include_router(payment.router, prefix="/payment", tags=["payment"])
app.include_router(stock.router, prefix="/stock", tags=["stock"])
app.include_router(table.router, prefix="/table", tags=["table"])



