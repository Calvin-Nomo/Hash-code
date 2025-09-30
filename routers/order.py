from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
import pymysql
from datetime import datetime

DB= pymysql.connect(
    host="localhost",
    user="root",
    password="Bineli2006",
    database="Order_System", 
   cursorclass=pymysql.cursors.DictCursor  # so results come as dicts instead of tuples
)
class Order(BaseModel):
    No_Reservation:int 
    Order_Date: datetime 
    Order_Type: str
    No_Table: int 
    Note:str
    

cursor=DB.cursor()

router = APIRouter(prefix="/order", tags=["order"])
@router.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}
@router.get('/Order')
def get_order():
    sql_command="Select* from Orders" 
    cursor.execute(sql_command)
    order =cursor.fetchall()
    return order

@router.post("/create order")
def create_order(order:Order):
    try:
        sql_command="""INSERT INTO Orders(No_Reservation,Order_Date,Order_Type,No_Table,Note)
        VALUES(%s,%s,%s,%s,%s)"""
        cursor.execute(sql_command,(order.No_Reservation,order.Order_Date,order.Order_Type,order.No_Table,order.Note))
        DB.commit()
    except Exception as e:
        raise HTTPException(status_code=404,detail=(e))
    return{
'Message':'You Have successfully added the Order data to your database'
    }

@router.put('/updated_order/{order_id}')
def update_order(order_id:int,order:Order):
    try:
        sql_command=""" UPDATE Orders 
        SET No_Reservation=%s,
        Order_Date=%s,Order_Type=%s,
        No_Table=%s,Note=%s
        WHERE Order_ID=%s  
        """
        cursor.execute(sql_command,(order.No_Reservation,order.Order_Date,order.Order_Type,order.No_Table,order.Note,order_id))
        DB.commit()
    except Exception as e:
        raise HTTPException(status_code=404,detail=(e))
    return{
        'Message':'You have updated successfully the Orders data from the database'
    }
@router.delete('/delete-order/{order_id}')
def delete_order(order_id: int):
    try:
        sql_command = """
        DELETE FROM Orders
        WHERE Order_ID = %s
        """
        cursor.execute(sql_command, (order_id,))
        DB.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        'Message': f'Order with ID {order_id} has been successfully deleted.'
    }