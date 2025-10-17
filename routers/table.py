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

router = APIRouter(prefix="/table", tags=["table"])

class Table(BaseModel):
    Table_Number:int
    Seat_Number:int
    State:str
###################################Get Method############################# 
@router.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}
@router.get('/Table')
def get_tables():
    sql_command="Select * from Tab" 
    cursor.execute(sql_command)
    table=cursor.fetchall()
    return table

###################################Post Method############################# 
@router.post("/create_table")
async def create_table(table:Table, current_user: dict = Depends(require_role(["admin"]))):
    try:
        sql_command="""INSERT INTO Tab(No_Table,Seat_Number,State)
        VALUES(%s,%s,%s)"""
        cursor.execute(sql_command,(table.Table_Number,table.Seat_Number,table.State))
        table_id=cursor.lastrowid
        DB.commit()
    except Exception as e:
        raise HTTPException(status_code=404,detail=(e))
    return{
'Message':f'You Have successfully created a new table {table_id} data to your database'
    }
###################################Put Method#############################     
@router.put('/update_table/{table_id}')
async def update_table(table_id:int,table:Table,current_user: dict = Depends(require_role(["admin"]))):
    try:
        sql_command="""
        UPDATE Tab
        SET 
        No_Table=%s,Seat_Number=%s
        WHERE Table_ID=%s
        """
        cursor.execute(sql_command,(table.Table_Number,table.Seat_Number,table_id))
        DB.commit()
    except Exception as e:
        raise HTTPException(status_code=404,detail=(e))
    return{
        'Message':'You have updated successfully the Table data from the database'
    }
###################################Delete Method############################# 
@router.delete('/delete_table/{table_id}')
async def delete_table(table_id: int,current_user: dict = Depends(require_role(["admin"]))):
        try:
            sql_command = """
                DELETE FROM Tab
                WHERE Table_ID = %s
            """
            cursor.execute(sql_command, (table_id,))
            DB.commit()

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        return {
            'Message': f'Table with ID {table_id} has been successfully deleted.'
        }