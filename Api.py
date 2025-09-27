# welcome to my api
from fastapi import FASTAPI
from pydantic import Base model 
import pymysql

connection = pymysql.connect(
    host="localhost",
    user="root",
    password="Bineli26",
   database="Order_System", cursorclass=pymysql.cursors.DictCursor  # so results come as dicts instead of tuples
)

app=FASTAPI() 

@app.get(/)
def greetings():
    return {
     "Message ":"Hello World" 
}