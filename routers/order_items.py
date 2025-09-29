from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
import pymysql

DB= pymysql.connect(
    host="localhost",
    user="root",
    password="Bineli2006",
    database="Order_System", 
   cursorclass=pymysql.cursors.DictCursor  # so results come as dicts instead of tuples
)

cursor=DB.cursor()

router = APIRouter(prefix="/order_items", tags=["order_items"])

class Items(BaseModel):
 Order_ID:int
 No_Product:int
 Quantity:int


@router.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}

@router.get('/Order_Items')
def get_orderitems():
    sql_command="Select* from Order_Items " 
    cursor.execute(sql_command)
    Items=cursor.fetchall()
    return Items
@router.post('/create_Order_items')
def create_items(item:Items):
    try:
        sql_command="""INSERT INTO Order_Items(Order_ID, No_Product,Quantity)
        VALUES(%s,%s,%s)"""
        cursor.execute(sql_command,(item.Order_ID,item.No_Product,item.Quantity))
        DB.commit()
    except Exception as e:
        raise HTTPException(status_code=404,detail=(e))
    return{
'Message':'You Have Successfully Added The  Order_Item Data To Your  Database'
    }