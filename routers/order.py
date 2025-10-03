from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
from routers.order_items import Items
from routers.reservation import Reservation
from routers.client import Client
from routers.product import get_product
import pymysql
from typing import List,Optional
from datetime import datetime

DB= pymysql.connect(
    host="localhost",
    user="root",
    password="Bineli26",
    database="Order_System", 
   cursorclass=pymysql.cursors.DictCursor  # so results come as dicts instead of tuples
)
class Order(BaseModel):
    Order_Type: str
    No_Table: Optional[int]=None
    Note: str | None = None
    items: List[Items]

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

# @router.put('/updated_order/{order_id}')
# def update_order(order_id:int,order:Order):
#     try:
#         sql_command=""" UPDATE Orders 
#         SET No_Reservation=%s,
#         Order_Date=%s,Order_Type=%s,
#         No_Table=%s,Note=%s
#         WHERE Order_ID=%s  
#         """
#         cursor.execute(sql_command,(order.No_Reservation,order.Order_Date,order.Order_Type,order.No_Table,order.Note,order_id))
#         DB.commit()
#     except Exception as e:
#         raise HTTPException(status_code=404,detail=(e))
#     return{
#         'Message':'You have updated successfully the Orders data from the database'
#     }
# @router.delete('/delete order/{order_id}')
# def delete_order(order_id: int):
#     try:
#         sql_command = """
#         DELETE FROM Orders
#         WHERE Order_ID = %s
#         """
#         cursor.execute(sql_command, (order_id,))
#         DB.commit()

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

#     return {
#         'Message': f'Order with ID {order_id} has been successfully deleted.'
#     }