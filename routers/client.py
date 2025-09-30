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

router = APIRouter(
    prefix="/client", tags=["client"]
)

class Client(BaseModel):
    Client_Name:str
    No_Telephone:str


@router.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}

@router.get('/Client')
def get_client():
    sql_command="Select * from Clients" 
    cursor.execute(sql_command)
    clients=cursor.fetchall()
    return clients
@router.post("/create_client")
def create_client(client:Client):
    try:
        sql_command="""INSERT INTO Clients(Client_Name,No_Telephone)
        VALUES(%s,%s)"""
        cursor.execute(sql_command,(client.Client_Name,client.No_Telephone))
        DB.commit()
    except Exception as e:
        raise HTTPException(status_code=404,detail=(e))
    return{
'Message':'You Have successfully added the  Client data to your database'
    }