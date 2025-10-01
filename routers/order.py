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
def total_Amount(order_id:int):
    sql_command=""" SELECT 
        o.Order_ID,
        SUM(oi.Quantity * pr.Unit_Price) AS Total_Amount
    FROM Orders o
    JOIN Order_Items oi ON o.Order_ID = oi.Order_ID
    JOIN Product pr ON oi.No_Product = pr.No_Product
    Where o.Order_ID=%s
    GROUP BY o.Order_ID"""
    cursor.execute(sql_command,(order_id,))
    result=cursor.fetchone()
    return result['Total_Amount']
class Order(BaseModel):
    No_Reservation:Optional[int]= None
    Order_Type: str
    No_Table: int 
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
        # 3. Calculate total amount using JOIN
        # sql_total = """
        #         SELECT SUM(oi.Quantity * p.Unit_Price) AS total_amount
        #         FROM Order_Items oi
        #         JOIN Product p ON oi.No_Product = p.No_Product
        #         WHERE oi.Order_ID = %s
        #     """
        # cursor.execute(sql_total, (order_id,))
        total_amount = total_amount(order_id)
        payment_date=datetime.utcnow()

            # 4. Insert Payment automatically
        sql_payment = """
                INSERT INTO Payment (Order_ID, Total_Amount,Payment_Date, Payment_Method, Payment_Status)
                VALUES (%s, %s, %s, %s, %s)
            """
        cursor.execute(sql_payment, (order_id, total_amount, payment_date,"Cash", "pending"))

        #         )
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