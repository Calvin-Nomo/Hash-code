# welcome to my api
from fastapi import FASTAPI
from pydantic import Base model 
import pymysql

DB= pymysql.connect(
    host="localhost",
    user="root",
    password="Bineli26",
   database="Order_System", cursorclass=pymysql.cursors.DictCursor  # so results come as dicts instead of tuples
)

cursor=DB.connection()

app=FASTAPI() 
######## Get Method#######
@app.get(/)
def greetings():
    return {
     "Message ":"Hello World" 
}

@app.get(/Product)
def get_product():
 sql_command="Select* from Product" cursor.execute(sql_command)
 product=cursor.fetchall
    return product

@app.get(/Order)
def get_order():
 sql_command="Select* from Order " cursor.execute(sql_command)
 order =cursor.fetchall
    return order
@app.get(/Order_Items)
def get_orderitems():
 sql_command="Select* from Order_Items " cursor.execute(sql_command)
 Items=cursor.fetchall
    return items

@app.get(/Payment )
def get_payment():
 sql_command="Select* from Payment" cursor.execute(sql_command)
 payments=cursor.fetchall
    return payments


@app.get(/Reservation )
def get_reservation():
 sql_command="Select * from Reservation " cursor.execute(sql_command)
 reservations =cursor.fetchall
    return reservations

@app.get(/Client)
def get_client():
 sql_command="Select * from Client" cursor.execute(sql_command)
 clients=cursor.fetchall
    return clients