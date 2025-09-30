from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
from routers.order_items import Items
from routers.product import get_product
import pymysql
from typing import List,Optional
from datetime import datetime

DB= pymysql.connect(
    host="localhost",
    user="root",
    password="Bineli2006",
    database="Order_System", 
   cursorclass=pymysql.cursors.DictCursor  # so results come as dicts instead of tuples
)
class Order(BaseModel):
    No_Reservation:Optional[int]=None
    Order_Type: str
    No_Table: int 
    Note:str
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

@router.post("/create_order")
def create_order(order:Order):
    try:
        order_date = datetime.utcnow() 
        sql_command="""INSERT INTO Orders(No_Reservation,Order_Date,Order_Type,No_Table,Note)
        VALUES(%s,%s,%s,%s,%s)"""
        cursor.execute(sql_command,(order.No_Reservation,order_date,order.Order_Type,order.No_Table,order.Note))
        order_id = cursor.lastrowid
            # Insert all order items in one go
        for item in order.items:
                cursor.execute(
                    """
                    INSERT INTO Order_Items (Order_ID, No_Product, Quantity)
                    VALUES (%s, %s, %s)
                    """,
                    (order_id, item.No_Product, item.Quantity)
                )

        DB.commit()
    except Exception as e:
        raise HTTPException(status_code=404,detail=(e))
    return{
        'Message':'You Have successfully added the Order data to your database',
        'Order_ID': order_id 
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
@router.delete('/delete order/{order_id}')
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