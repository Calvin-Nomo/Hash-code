from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
import pymysql
from datetime import date,time
DB= pymysql.connect(
    host="localhost",
    user="root",
    password="Bineli2006",
    database="Order_System", 
   cursorclass=pymysql.cursors.DictCursor  # so results come as dicts instead of tuples
)

cursor=DB.cursor()

router = APIRouter( prefix="/reservation", tags=["reservation"])
class Reservation(BaseModel):
    No_Client:int
    Reservation_Date:date
    Reservation_Time:time
    No_Person:int

@router.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}
@router.get('/Reservation')
def get_reservation():
    sql_command="Select * from Reservation "
    cursor.execute(sql_command)
    reservations =cursor.fetchall()
    return reservations

@router.post('/create Reservation')
def create_reservation(reserve:Reservation):
    try:
        sql_command="""INSERT INTO Reservation(No_Client,Reservation_Date,Reservation_Time,No_Person)
        VALUES(%s,%s,%s,%s)"""
        cursor.execute(sql_command,(reserve.No_Client,reserve.Reservation_Date,reserve.Reservation_Time,reserve.No_Person))
        DB.commit()
    except Exception as e:
        raise HTTPException(status_code=404,detail=(e))
    return{
'Message':'You Have successfully added the Reservation data to your database'
    }
