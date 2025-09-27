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
########Here is all the Get Method#######
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
