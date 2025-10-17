from fastapi import APIRouter,HTTPException,Depends
from pydantic import BaseModel
from dependencies import require_role,get_current_active_user
import pymysql

DB= pymysql.connect(
    host="localhost",
    user="root",
    password="Bineli26",
    database="Order_System", 
   cursorclass=pymysql.cursors.DictCursor  # so results come as dicts instead of tuples
)

cursor=DB.cursor()

router = APIRouter(prefix="/stock", tags=["stock"])

class Stock(BaseModel):
    Quantity_Available:int
    
@router.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}

@router.get('/Stock')
def get_stock(current_user: dict = Depends(get_current_active_user)):
    sql_command="Select * from Stock" 
    cursor.execute(sql_command)
    stock=cursor.fetchall()
    return stock

@router.get('/Stock')
def get_stock():
    sql_command="""
    Select s.No_Stock,p.Product_Name,s.Quantity_Available
    From Stock s
    Join Product p
    ON
    s.No_Product=p.No_Product
    Limit 7
    """
    cursor.execute(sql_command)
    stock=cursor.fetchall()
    return stock
@router.post("/create_stock")
def create_stock(stock:Stock,current_user: dict = Depends(require_role(["Admin"]))):
    try:
        sql_command="""INSERT INTO Stock(Quantity_Available)
        VALUES(%s)"""
        cursor.execute(sql_command,(stock.Quantity_Available))
        DB.commit()
    except Exception as e:
        raise HTTPException(status_code=404,detail=(e))
    return{
'Message':'You Have successfully added the  Stock data to your database'
    }

@router.put("/update_stock/{stock_id}")
async def update_stock(stock_id,stock: Stock,current_user: dict = Depends(require_role(["admin"]))):
    try:
        sql_command = """
            UPDATE Stock
            SET Quantity_Available = %s
            WHERE No_Stock=%s
        """
        cursor.execute(sql_command, (stock.Quantity_Available,stock_id))
        DB.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "Message": "Stock data successfully updated in the database"
    }

@router.delete("/delete_stock/{stock_id}")
def delete_stock(stock_id: int,current_user: dict = Depends(require_role(["Admin"]))):
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