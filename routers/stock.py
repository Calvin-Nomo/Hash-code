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

router = APIRouter(prefix="/stock", tags=["stock"])

class Stock(BaseModel):
    No_Product:int
    Quantity_Available:int
    
@router.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}

@router.get('/Stock')
def get_client():
    sql_command="Select * from Stock" 
    cursor.execute(sql_command)
    stock=cursor.fetchall()
    return stock

@router.post("/create_stock")
def create_stock(stock:Stock):
    try:
        sql_command="""INSERT INTO Stock(No_Product,Quantity_Available)
        VALUES(%s,%s)"""
        cursor.execute(sql_command,(stock.No_Product,stock.Quantity_Available))
        DB.commit()
    except Exception as e:
        raise HTTPException(status_code=404,detail=(e))
    return{
'Message':'You Have successfully added the  Stock data to your database'
    }

@router.put("/update_stock/{stock_id}")
def update_stock(stock_id,stock: Stock):
    try:
        sql_command = """
            UPDATE Stock
            SET Quantity_Available = %s,No_Product = %s
            WHERE No_Stock=%s
        """
        cursor.execute(sql_command, (stock.Quantity_Available, stock.No_Product,stock_id))
        DB.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "Message": "Stock data successfully updated in the database"
    }

@router.delete("/delete_stock/{stock_id}")
def delete_stock(stock_id: int):
    try:
        sql_command = """
            DELETE FROM Stock
            WHERE No_Stock = %s
        """
        cursor.execute(sql_command, (stock_id,))
        DB.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "Message": f"Stock with No_Product {stock_id} has been successfully deleted."
    }