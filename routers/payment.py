from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
from datetime import datetime
import pymysql

DB= pymysql.connect(
    host="localhost",
    user="root",
    password="Bineli2006",
    database="Order_System", 
   cursorclass=pymysql.cursors.DictCursor  # so results come as dicts instead of tuples
)

cursor=DB.cursor()

router = APIRouter( prefix="/payment", tags=["payment"])

class Payment(BaseModel):
    Order_ID:int 
    Total_Amount:float 
    Payment_Date:datetime 
    Payment_Method:str
    Payment_Status:str


@router.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}

@router.get('/Payment')
def get_payment():
    sql_command="Select* from Payment" 
    cursor.execute(sql_command)
    payments=cursor.fetchall()
    return payments
@router.post("/create_payment")
def create_payment(pay:Payment):
    try:
        sql_command="""INSERT INTO Payment(Order_ID,Total_Amount,Payment_Date,Payment_Method,Payment_Status)
        VALUES(%s,%s,%s,%s,%s)"""
        cursor.execute(sql_command,(pay.Order_ID,pay.Total_Amount,pay.Payment_Date,pay.Payment_Method,pay.Payment_Status))
        DB.commit()
    except Exception as e:
        raise HTTPException(status_code=404,detail=(e))
    return{
'Message':'You Have successfully added the Payment data to your database'
    }
