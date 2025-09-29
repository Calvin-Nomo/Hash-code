# welcome to my api
# cd desktop
#cd Hash-code
# env\Scripts\activate
from fastapi import FastAPI,APIRouter
from pydantic import BaseModel
import pymysql
from routers import client,order,order_items,reservation,payment,product

DB= pymysql.connect(
    host="localhost",
    user="root",
    password="Bineli2006",
    database="Order_System", 
   cursorclass=pymysql.cursors.DictCursor  # so results come as dicts instead of tuples
)

cursor=DB.cursor()

app=FastAPI(title='Qrcode Order System') 

app.include_router(client.router, prefix="/client", tags=["client"])
app.include_router(order.router, prefix="/order", tags=["order"])
app.include_router(order_items.router, prefix="/order_items", tags=["order_items"])
app.include_router(reservation.router, prefix="/reservation", tags=["reservation"])
app.include_router(product.router, prefix="/product", tags=["product"])
app.include_router(payment.router, prefix="/payment", tags=["payment"])

##### Class############

######## Get Method#######
@app.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}

# @app.get('/Product')
# def get_product():
#     sql_command="Select* from Product"
#     cursor.execute(sql_command)
#     product=cursor.fetchall()
#     return product
# @app.get('/database')
# def get_databases():
#     sql_command="Show databases"
#     cursor.execute(sql_command)
#     data=cursor.fetchall()
#     return data
# @app.get('/Order')
# def get_order():
#     sql_command="Select* from Orders" 
#     cursor.execute(sql_command)
#     order =cursor.fetchall()
#     return order
# @app.get('/Order_Items')
# def get_orderitems():
#     sql_command="Select* from Order_Items " 
#     cursor.execute(sql_command)
#     Items=cursor.fetchall()
#     return Items

# @app.get('/Payment')
# def get_payment():
#     sql_command="Select* from Payment" 
#     cursor.execute(sql_command)
#     payments=cursor.fetchall()
#     return payments


# @app.get('/Reservation')
# def get_reservation():
#     sql_command="Select * from Reservation "
#     cursor.execute(sql_command)
#     reservations =cursor.fetchall()
#     return reservations

# @app.get('/Client')
# def get_client():
#     sql_command="Select * from Clients" 
#     cursor.execute(sql_command)
#     clients=cursor.fetchall()
#     return clients


###### Post Method #####




######Update Method #####



#### Delete Method #####