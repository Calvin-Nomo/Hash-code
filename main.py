from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pymysql
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from routers import client, order, order_items, reservation, payment, product, stock, table
from routers.client import Client
from routers.order import Order
from routers.payment import Payment
from routers.reservation import Reservation

app = FastAPI(title="Qrcode Order System")

<<<<<<< HEAD
app=FastAPI(title='Qrcode Order System') 
class FullOrderRequest(BaseModel):
    client:Client
    reservation:Optional[Reservation]=None
    order:Order
    payment:Payment
# Allow CORS for frontend running on different port
=======
# --- Allow frontend access ---
>>>>>>> 96a09aaf701f509a91d2cde65e69e4a6d8e1e836
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


# ------------------- MODELS -------------------
class FullOrderRequest(BaseModel):
    client: Client
    reservation: Optional[Reservation] = None
    order: Order
    payment: Payment


# ------------------- POST /FullOrderRequest -------------------
@app.post("/FullOrderRequest")
def create_order(data: FullOrderRequest):
    try:
<<<<<<< HEAD

        sql_command="""SELECT No_Client FROM Clients 
                    WHERE No_Telephone=%s
                """
        cursor.execute(sql_command,(data.client.No_Telephone,))
        client= cursor.fetchone()
        if  client:
            client_id=client['No_Client']
=======
        cursor = DB.cursor()
        DB.begin()  #  start transaction

        # 1️ Check or create client
        cursor.execute("SELECT No_Client FROM Clients WHERE No_Telephone=%s", (data.client.No_Telephone,))
        client = cursor.fetchone()
        if client:
            client_id = client["No_Client"]
>>>>>>> 96a09aaf701f509a91d2cde65e69e4a6d8e1e836
        else:
            cursor.execute(
                "INSERT INTO Clients(Client_Name, No_Telephone) VALUES (%s, %s)",
                (data.client.Client_Name, data.client.No_Telephone),
            )
            client_id = cursor.lastrowid

<<<<<<< HEAD
            #Handling the Reservation if the Order_Type is Reversation
            reservation_id=None
            reverse=data.reservation
            # if data.order.Order_Type=='Reservation':
            #     if not data.reservation:
            #         raise HTTPException(status_code=404,detail='The Reservation Information is needed')
            if data.order.Order_Type == 'Reservation':
                if not data.reservation or data.reservation.No_Table is None:
                    raise HTTPException(status_code=400, detail='Reservation information is required for reservation-type orders.')

                    
                reverse=data.reservation
                sql_command=""" INSERT INTO 
                Reservation(No_Client,No_Table,Reservation_Date,Reservation_Time,No_Person)
                Values(%s,%s,%s,%s,%s)
                """ 
                cursor.execute(sql_command,(client_id,reverse.No_Table,reverse.Reservation_Date,reverse.Reservation_Time,reverse.No_Person))
                reservation_id=cursor.lastrowid
                table_id= reverse.No_Table
                # Handling the Dine In Order Type
            elif data.order.Order_Type == 'Dine In':
                table_id=data.order.No_Table
                #Checking if a table Exist
                sql_command="""SELECT No_Table From Tab WHERE Table_ID=%s """
                cursor.execute(sql_command,(table_id,))
                table=cursor.fetchone()
                if not table:
                  raise HTTPException(status_code=404,detail='The Table does not exist')
                if not data.order.No_Table:
                    raise HTTPException(status_code=404,detail='a Table Number is Required for the Dine In')
            else:
                #For the Take Away No Table(table_id) Need
                table_id=None
            order=data.order
            order_date = datetime.utcnow() 
            sql_order="""INSERT INTO Orders(No_Client,No_Reservation,Order_Date,Order_Type,No_Table,Note)
            VALUES(%s,%s,%s,%s,%s,%s)"""
            cursor.execute(sql_order,(client_id,reservation_id,order_date,order.Order_Type,table_id,order.Note))
            order_id = cursor.lastrowid
            
            # filling the  client items in the Order_items Table
            for item in data.order.items:
                #checking if the is an Available Quantity  Product in stock
                cursor.execute(
                        "SELECT Quantity_Available FROM Stock WHERE No_Product=%s",
                        (item.No_Product,)
                    )
                stock = cursor.fetchone()
                if not stock:
                        raise HTTPException(status_code=404,detail=f'No Quantity_Available Found For {item.No_Product}')
                        
                elif stock["Quantity_Available"] < item.Quantity:
                            
                    raise HTTPException(status_code=404, detail=f"Not enough stock for product {item.No_Product}")
=======
        # 2️ Handle Reservation / Dine In / Take Away
        reservation_id = None
        table_id = None
        if data.order.Order_Type == "Reservation":
            if not data.reservation:
                raise HTTPException(status_code=400, detail="Reservation details required for Reservation orders")
            cursor.execute(
                """INSERT INTO Reservation(No_Client, No_Table, Reservation_Date, Reservation_Time, No_Person)
                   VALUES (%s, %s, %s, %s, %s)""",
                (client_id, data.reservation.No_Table, data.reservation.Reservation_Date,
                 data.reservation.Reservation_Time, data.reservation.No_Person),
            )
            reservation_id = cursor.lastrowid
            table_id = data.reservation.No_Table
>>>>>>> 96a09aaf701f509a91d2cde65e69e4a6d8e1e836

        elif data.order.Order_Type == "Dine In":
            if not data.order.No_Table:
                raise HTTPException(status_code=400, detail="Table number required for Dine In order")
            cursor.execute("SELECT * FROM Tab WHERE Table_ID=%s", (data.order.No_Table,))
            table = cursor.fetchone()
            if not table:
                raise HTTPException(status_code=404, detail="Table not found")
            table_id = data.order.No_Table

        # 3️ Create Order
        order_date = datetime.utcnow()
        cursor.execute(
            """INSERT INTO Orders(No_Client, No_Reservation, Order_Date, Order_Type, No_Table, Note)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (client_id, reservation_id, order_date, data.order.Order_Type, table_id, data.order.Note),
        )
        order_id = cursor.lastrowid

<<<<<<< HEAD
            # 
            DB.commit()
    except Exception:
        raise HTTPException(status_code=404,detail='Error in the SQL Commands')
    return{
        'Message':'You Have successfully Place an Order',
     
    }
            
        
        
######Update Method #####
=======
        # 4️ Add items and update stock
        for item in data.order.items:
            cursor.execute("SELECT Quantity_Available FROM Stock WHERE No_Product=%s", (item.No_Product,))
            stock = cursor.fetchone()
            if not stock:
                raise HTTPException(status_code=404, detail=f"Product {item.No_Product} not found in stock")
            if stock["Quantity_Available"] < item.Quantity:
                raise HTTPException(status_code=400, detail=f"Not enough stock for product {item.No_Product}")

            cursor.execute(
                "INSERT INTO Order_Items(Order_ID, No_Product, Quantity) VALUES (%s, %s, %s)",
                (order_id, item.No_Product, item.Quantity),
            )
            cursor.execute(
                "UPDATE Stock SET Quantity_Available = Quantity_Available - %s WHERE No_Product=%s",
                (item.Quantity, item.No_Product),
            )

        # 5️ Calculate total and insert payment
        cursor.execute(
            """SELECT SUM(oi.Quantity * p.Unit_Price) AS total
               FROM Order_Items oi
               JOIN Product p ON oi.No_Product = p.No_Product
               WHERE oi.Order_ID = %s""",
            (order_id,),
        )
        total = cursor.fetchone()["total"]
        cursor.execute(
            """INSERT INTO Payment (Order_ID, Total_Amount, Payment_Date, Payment_Method, Payment_Status)
               VALUES (%s, %s, %s, %s, %s)""",
            (order_id, total, datetime.utcnow(), data.payment.Payment_Method, "Paid"),
        )

        DB.commit()  #  commit transaction
        return {"message": "Order placed successfully", "order_id": order_id}

    except HTTPException as e:
        DB.rollback()
        raise e
    except Exception as e:
        DB.rollback()
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
>>>>>>> 96a09aaf701f509a91d2cde65e69e4a6d8e1e836


@app.put("/order/{order_id}")
def update_order(order_id: int, data: FullOrderRequest):
    try:
        cursor = DB.cursor()
        DB.begin()

<<<<<<< HEAD
=======
        cursor.execute("SELECT * FROM Orders WHERE Order_ID=%s", (order_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Order not found")

        cursor.execute(
            "UPDATE Orders SET Order_Type=%s, Note=%s WHERE Order_ID=%s",
            (data.order.Order_Type, data.order.Note, order_id),
        )

        cursor.execute(
            "UPDATE Payment SET Payment_Method=%s, Payment_Status=%s WHERE Order_ID=%s",
            (data.payment.Payment_Method, data.payment.Payment_Status, order_id),
        )

        DB.commit()
        return {"message": "Order updated successfully"}
    except HTTPException as e:
        DB.rollback()
        raise e
    except Exception as e:
        DB.rollback()
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

@app.delete("/order/{order_id}")
def delete_order(order_id: int):
    try:
        cursor = DB.cursor()
        DB.begin()

        cursor.execute("SELECT * FROM Orders WHERE Order_ID=%s", (order_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Order not found")

        cursor.execute("DELETE FROM Order_Items WHERE Order_ID=%s", (order_id,))
        cursor.execute("DELETE FROM Payment WHERE Order_ID=%s", (order_id,))
        cursor.execute("DELETE FROM Orders WHERE Order_ID=%s", (order_id,))

        DB.commit()
        return {"message": "Order and related records deleted successfully"}
    except HTTPException as e:
        DB.rollback()
        raise e
    except Exception as e:
        DB.rollback()
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
>>>>>>> 96a09aaf701f509a91d2cde65e69e4a6d8e1e836
