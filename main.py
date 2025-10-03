from datetime import datetime
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import pymysql
from routers import client,order,order_items,reservation,payment,product,stock
from routers.client import Client
from routers.order import Order
from routers.payment import Payment
from routers.reservation import Reservation
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware


app=FastAPI(title='Qrcode Order System') 
class FullOrderRequest(BaseModel):
    client:Client
    reversation:Optional[Reservation]=None
    order:Order
    payment:Payment
# Allow CORS for frontend running on different port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in prod, restrict to your frontend domain
    allow_methods=["*"],
    allow_headers=["*"],
)

DB= pymysql.connect(
    host="localhost",
    user="root",
    passwd="Bineli26",
    database="Order_System", 
   cursorclass=pymysql.cursors.DictCursor,
   autocommit=True
   # so results come as dicts instead of tuples
)

cursor=DB.cursor()

app.include_router(client.router, prefix="/client", tags=["client"])
app.include_router(order.router, prefix="/order", tags=["order"])
app.include_router(order_items.router, prefix="/order_items", tags=["order_items"])
app.include_router(reservation.router, prefix="/reservation", tags=["reservation"])
app.include_router(product.router, prefix="/product", tags=["product"])
app.include_router(payment.router, prefix="/payment", tags=["payment"])
app.include_router(stock.router, prefix="/stock", tags=["stock"])

##### Class############
def client():
    sql_command="""SELECT Client_Name FROM Clients"""
    cursor.execute(sql_command)
    client=cursor.fetchone()
    return client
######## Get Method#######
@app.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}

@app.get('/database')
def get_databases():
    sql_command="Show databases"
    cursor.execute(sql_command)
    data=cursor.fetchall()
    return data


###### Post Method #####
@app.post('/FullOrderRequest')
def create_order(data:FullOrderRequest):
#checks if the clients exit if not  create
    try:
        sql_command="""SELECT No_Client FROM Clients 
                    WHERE No_Telephone=%s
                """
        cursor.execute(sql_command,(data.client.No_Telephone))
        client= cursor.fetchone()
        if  client:
            client_id=client['No_Client']
        else:
            sql_command="""INSERT INTO Clients(Client_Name,No_Telephone)
            Values(%s,%s)
            """
            cursor.execute(sql_command,(data.client.Client_Name,data.client.No_Telephone))
            client_id= cursor.lastrowid
            
            #Handling the Reservation if the Order_Type is Reversation
            reservation_id=None
            if data.order.Order_Type=='Reservation':
                if not data.reversation:
                    raise HTTPException(status_code=404,detail='The Reservation Information is needed')
                reverse=data.reversation
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
                if not data.order.No_Table:
                    raise HTTPException(status_code=404,detail='a Table Number is Required for the Dine In')
            else:
                #For the Take Away No Table(table_id) Need
                table_id=None
            order=data.order
            order_date = datetime.utcnow() 
            sql_command="""INSERT INTO Orders(No_Client,No_Reservation,Order_Date,Order_Type,No_Table,Note)
            VALUES(%s,%s,%s,%s,%s)"""
            cursor.execute(sql_command,(client_id,reservation_id,order_date,order.Order_Type,table_id,order.Note))
            order_id = cursor.lastrowid
            
            # filling the  client items in the Order_items Table
            for item in data.order.items:
                #checking if the is an Available Quantity  Product in stock
                cursor.execute(
                        "SELECT Quantity_Available FROM Product WHERE No_Product=%s",
                        (item.No_Product,)
                    )
                stock = cursor.fetchone()
                if not stock:
                        raise HTTPException(status_code=404,detail=f'No Quantity_Available Found For {item.No_Product}')
                        
                if stock["Quantity_Available"] < item.Quantity:
                        
                            raise HTTPException(status_code=404, detail=f"Not enough stock for product {item.No_Product}")

                sql_command="""INSERT INTO Order_Items(Order_ID,No_Product,Quantity) 
                VALUES(%s,%s,%s)
                """
                cursor.execute(sql_command,(order_id,item.No_Product,item.Quantity))
                
                cursor.execute(
                        "UPDATE Stock SET Quantity_Available = Quantity_Available - %s WHERE No_Product=%s",
                        (item.Quantity, item.No_Product)
                    )
                        # 3. Calculate total amount using JOIN
                sql_total = """
                    SELECT SUM(oi.Quantity * p.Unit_Price) AS total
                    FROM Order_Items oi
                    JOIN Product p ON oi.No_Product = p.No_Product
                    WHERE oi.Order_ID = %s
                """
                cursor.execute(sql_total, (order_id,))
                total_amount= cursor.fetchone()['total']
                payment_date=datetime.utcnow()

                # 4. Insert Payment automatically
            sql_payment = """
                    INSERT INTO Payment (Order_ID, Total_Amount,Payment_Date, Payment_Method, Payment_Status)
                    VALUES (%s, %s, %s, %s, %s)
                """
            status="Paid"
            cursor.execute(sql_payment, (order_id, total_amount, payment_date,data.payment.Payment_Method,status))

            # 
            DB.commit()
    except Exception as e:
        raise HTTPException(status_code=404,detail=(e))
    return{
        'Message':'You Have successfully Place an Order',
        'Order_ID': order_id 
    }
            
        
        
######Update Method #####



#### Delete Method #####