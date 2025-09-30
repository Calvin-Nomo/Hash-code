# welcome to my api
0# cd desktop
#cd Hash-code
# env\Scripts\activate
from fastapi import FastAPI,APIRouter
from pydantic import BaseModel
import pymysql
from routers import client,order,order_items,reservation,payment,product,stock
from typing import List
from fastapi.middleware.cors import CORSMiddleware


app=FastAPI(title='Qrcode Order System') 


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
    password="Bineli2006",
    database="Order_System", 
   cursorclass=pymysql.cursors.DictCursor  # so results come as dicts instead of tuples
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




######Update Method #####



#### Delete Method #####