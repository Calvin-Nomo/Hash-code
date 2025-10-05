from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
import pymysql

DB= pymysql.connect(
    host="localhost",
    user="root",
    password="Bineli26",
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



@router.put('/update_client/{client_id}')
def update_client(client_id:int,client:Client):
    try:
        sql_command="""
        UPDATE Clients
        SET 
        Client_Name=%s,No_Telephone=%s
        WHERE No_Client=%s
        """
        cursor.execute(sql_command,(client.Client_Name,client.No_Telephone,client_id))
        DB.commit()
    except Exception as e:
        raise HTTPException(status_code=404,detail=(e))
    return{
        'Message':'You have updated successfully the Clients data from the database'
    }

@router.delete('/delete_client/{client_id}')
def delete_client(client_id: int):
    try:
        sql_command = """
            DELETE FROM Clients
            WHERE No_Client = %s
        """
        cursor.execute(sql_command, (client_id,))
        DB.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        'Message': f'Client with ID {client_id} has been successfully deleted.'
    }