from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pymysql
from routers import client, order, order_items, reservation, payment, product, stock
from routers.client import Client
from routers.order import Order
from routers.payment import Payment
from routers.reservation import Reservation
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='Qrcode Order System')

class FullOrderRequest(BaseModel):
    client: Client
    reservation: Optional[Reservation] = None   # fixed typo
    order: Order
    payment: Payment

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB = pymysql.connect(
    host="localhost",
    user="root",
    database="Order_System",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

cursor = DB.cursor()

# Routers
app.include_router(client.router, prefix="/client", tags=["client"])
app.include_router(order.router, prefix="/order", tags=["order"])
app.include_router(order_items.router, prefix="/order_items", tags=["order_items"])
app.include_router(reservation.router, prefix="/reservation", tags=["reservation"])
app.include_router(product.router, prefix="/product", tags=["product"])
app.include_router(payment.router, prefix="/payment", tags=["payment"])
app.include_router(stock.router, prefix="/stock", tags=["stock"])

@app.get('/')
def greetings():
    return {"Message": "Hello World"}

@app.get('/database')
def get_databases():
    cursor.execute("SHOW DATABASES")
    return cursor.fetchall()

@app.post('/FullOrderRequest')
def create_order(data: FullOrderRequest):
    try:
        # 1. Check if client exists
        sql_command = """SELECT No_Client FROM Clients WHERE No_Telephone=%s"""
        cursor.execute(sql_command, (data.client.No_Telephone,))
        client_row = cursor.fetchone()

        if client_row:
            client_id = client_row['No_Client']
        else:
            sql_command = """INSERT INTO Clients(Client_Name, No_Telephone) VALUES(%s,%s)"""
            cursor.execute(sql_command, (data.client.Client_Name, data.client.No_Telephone))
            client_id = cursor.lastrowid

        # 2. Handle reservation / table
        reservation_id = None
        if data.order.Order_Type == 'Reservation':
            if not data.reservation:
                raise HTTPException(status_code=404, detail='Reservation Information is required')
            r = data.reservation
            sql_command = """INSERT INTO Reservation(No_Client,No_Table,Reservation_Date,Reservation_Time,No_Person)
                             VALUES(%s,%s,%s,%s,%s)"""
            cursor.execute(sql_command, (client_id, r.No_Table, r.Reservation_Date, r.Reservation_Time, r.No_Person))
            reservation_id = cursor.lastrowid
            table_id = r.No_Table
        elif data.order.Order_Type == 'Dine In':
            if not data.order.No_Table:
                raise HTTPException(status_code=404, detail='A Table Number is required for Dine In')
            table_id = data.order.No_Table
        else:
            table_id = None  # Takeaway

        # 3. Insert order
        order = data.order
        order_date = datetime.utcnow()
        sql_command = """INSERT INTO Orders(No_Client, No_Reservation, Order_Date, Order_Type, No_Table, Note)
                         VALUES(%s,%s,%s,%s,%s,%s)"""
        cursor.execute(sql_command, (client_id, reservation_id, order_date, order.Order_Type, table_id, order.Note))
        order_id = cursor.lastrowid

        # 4. Insert order items & update stock
        for item in data.order.items:
            cursor.execute("SELECT Quantity_Available FROM Stock WHERE No_Product=%s", (item.No_Product,))
            stock = cursor.fetchone()
            if not stock:
                raise HTTPException(status_code=404, detail=f'No stock found for product {item.No_Product}')
            if stock["Quantity_Available"] < item.Quantity:
                raise HTTPException(status_code=404, detail=f'Not enough stock for product {item.No_Product}')

            cursor.execute("INSERT INTO Order_Items(Order_ID, No_Product, Quantity) VALUES(%s,%s,%s)",
                           (order_id, item.No_Product, item.Quantity))
            cursor.execute("UPDATE Stock SET Quantity_Available = Quantity_Available - %s WHERE No_Product=%s",
                           (item.Quantity, item.No_Product))

        # 5. Calculate total and insert payment
        sql_total = """
            SELECT SUM(oi.Quantity * p.Unit_Price) AS total
            FROM Order_Items oi
            JOIN Product p ON oi.No_Product = p.No_Product
            WHERE oi.Order_ID = %s
        """
        cursor.execute(sql_total, (order_id,))
        total_amount = cursor.fetchone()['total']
        payment_date = datetime.utcnow()

        sql_payment = """INSERT INTO Payment (Order_ID, Total_Amount, Payment_Date, Payment_Method, Payment_Status)
                         VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql_payment, (order_id, total_amount, payment_date, data.payment.Payment_Method, "Paid"))

        DB.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"Message": "Order placed successfully", "Order_ID": order_id}
