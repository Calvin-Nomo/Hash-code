from fastapi import APIRouter,HTTPException,Depends
from pydantic import BaseModel
from dependencies import require_role,get_current_active_user
import pymysql

from datetime import datetime
DB= pymysql.connect(
    host="localhost",
    user="root",
    password="Bineli26",
    database="Order_System", 
   cursorclass=pymysql.cursors.DictCursor  # so results come as dicts instead of tuples
)

cursor=DB.cursor()

router = APIRouter( prefix="/reservation", tags=["reservation"])

class Reservation(BaseModel):
    No_Table:int
    Reservation_Date:datetime
    No_Person:int

@router.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}

@router.get('/Reservation')
def get_reservations():
    sql_command="Select * from Reservation "
    cursor.execute(sql_command)
    reservations =cursor.fetchall()
    return reservations
@router.get('/total_reservations')
def total_reservations():
    sql_command="Select count(No_Reservation) as total from Reservation"
    cursor.execute(sql_command)
    total=cursor.fetchone()
    return total

# @router.post('/create_reservation')
# def create_reservation(reserve:Reservation):
#     try:
#         sql_command="""INSERT INTO Reservation(No_Client,Reservation_Date,Reservation_Time,No_Person)
#         VALUES(%s,%s,%s,%s)"""
#         cursor.execute(sql_command,(reserve.No_Client,reserve.Reservation_Date,reserve.Reservation_Time,reserve.No_Person))
#         DB.commit()
#     except Exception as e:
#         raise HTTPException(status_code=404,detail=(e))
#     return{
# 'Message':'You Have successfully added the Reservation data to your database'
#     }


@router.put('/update-reservation/{reservation_id}')
async def update_reservation(reservation_id: int, reserve: Reservation,current_user: dict = Depends(require_role(["admin"]))):
    try:
        sql_command = """
        UPDATE Reservation
        SET No_Client=%s, Reservation_Date=%s, No_Person=%s
        WHERE No_Reservation=%s
        """
        cursor.execute(sql_command, (
            reserve.Reservation_Date,
            reserve.No_Person,
            reservation_id
        ))
        DB.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        'Message': 'You have successfully updated the reservation data in your database.'
    }

@router.delete('/delete-reservation/{reservation_id}')
def delete_reservation(reservation_id: int,current_user: dict = Depends(require_role(["Admin"]))):
    try:
        sql_command = """
        DELETE FROM Reservation
        WHERE No_Reservation = %s
        """
        cursor.execute(sql_command, (reservation_id,))
        DB.commit()


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        'Message': f'Reservation with ID {reservation_id} has been successfully deleted.'
    }