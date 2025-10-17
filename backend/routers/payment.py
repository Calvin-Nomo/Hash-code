from fastapi import APIRouter,HTTPException,Depends
from pydantic import BaseModel
from dependencies import get_current_active_user,require_role
import pymysql

DB= pymysql.connect(
    host="localhost",
    user="root",
    password="Bineli26",
    database="Order_System", 
   cursorclass=pymysql.cursors.DictCursor  # so results come as dicts instead of tuples
)

cursor=DB.cursor()

router = APIRouter( prefix="/payment", tags=["payment"])

class Payment(BaseModel):
    Payment_Method:str


@router.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}
@router.get('/total_revenue')
def total_revenue():
    sql_command="Select sum(Total_Amount) as total from Payment"
    cursor.execute(sql_command)
    revenue=cursor.fetchone()
    return revenue

@router.get('/Payment')
def get_payment():
    sql_command="Select* from Payment" 
    cursor.execute(sql_command)
    payments=cursor.fetchall()
    return payments

# @router.post("/create_payment")
# def create_payment(pay:Payment,current_user: dict = Depends(require_role(["Admin"]))):
#     try:
#         payment_date=datetime.utcnow()
#         sql_command="""INSERT INTO Payment(Order_ID,Total_Amount,Payment_Date,Payment_Method,Payment_Status)
#         VALUES(%s,%s,%s,%s,%s)"""
#         cursor.execute(sql_command,(pay.Order_ID,pay.Total_Amount,payment_date,pay.Payment_Method,pay.Payment_Status))
#         DB.commit()
#     except Exception as e:
#         raise HTTPException(status_code=404,detail=(e))
#     return{
# 'Message':'You Have successfully added the Payment data to your database'
#     }

# @router.put('/updated_payment/{payment_id}')
# def update_order(payment_id:int,pay:Payment,current_user: dict = Depends(require_role(["Admin"]))):
#     try:
#         sql_command=""" UPDATE Payment SET
#         Order_ID=%s,Total_Amount=%s,Payment_Date=%s,Payment_Method=%s,Payment_Status=%s WHERE Payment_ID=%s)"""
#         cursor.execute(sql_command,(pay.Order_ID,pay.Total_Amount,pay.Payment_Date,pay.Payment_Method,pay.Payment_Status,payment_id))
#         DB.commit()
#     except Exception as e:
#         raise HTTPException(status_code=404,detail=(e))
#     return{
#         'Message':'You have updated successfully the Payments data from the database'
#     }

@router.delete('/delete_payment/{payment_id}')
def delete_payment(payment_id: int,current_user: dict = Depends(require_role(["admin"]))):
    try:
        sql_command = """
        DELETE FROM Payment
        WHERE Payment_ID = %s
        """
        cursor.execute(sql_command, (payment_id,))
        DB.commit()


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        'Message': f'Payment with ID {payment_id} has been successfully deleted.'
    }