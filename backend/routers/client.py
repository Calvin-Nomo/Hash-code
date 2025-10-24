from fastapi import APIRouter,HTTPException,Depends
from pydantic import BaseModel
from slowapi import Limiter
import logging
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from backend.data.credentials import Mysql_password,Database_Name
from dependencies import require_role,get_current_active_user
import pymysql

DB= pymysql.connect(
    host="localhost",
    user="root",
    password=Mysql_password,
    database=Database_Name, 
   cursorclass=pymysql.cursors.DictCursor  # so results come as dicts instead of tuples
)

cursor=DB.cursor()

router = APIRouter(
    prefix="/client", tags=["client"]
)
# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,  # can be DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log",  # all logs saved here
    filemode="a",  # append mode
)
logger = logging.getLogger(__name__)
# ---------------- Rate Limiter ----------------
limiter = Limiter(key_func=get_remote_address)
router.state.limiter = limiter

@router.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please wait a moment."},
    )

class Client(BaseModel):
    Client_Name:str
    No_Telephone:str
    Email :str = None


@router.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}

@router.get('/Client')
def get_client(current_user: dict = Depends(require_role(["admin"]))):
    sql_command="Select * from Clients" 
    cursor.execute(sql_command)
    clients=cursor.fetchall()
    return clients

@router.post("/create_client")
def create_stock(client:Client,current_user: dict = Depends(require_role(["admin"]))):
    try:
        sql_command="""INSERT INTO Clients(Client_Name,No_Telephone,Email)
        VALUES(%s,%s)"""
        cursor.execute(sql_command,(client.Client_Name,client.No_Telephone,))
        DB.commit()
    except Exception as e:
        raise HTTPException(status_code=404,detail=(e))
    return{
'Message':'You Have successfully created  the  client data in your database'
    }

@router.put('/update_client/{client_id}')
async def update_client(client_id:int,client:Client,current_user: dict = Depends(require_role(["admin"]))):
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
def delete_client(client_id: int,current_user: dict = Depends(require_role(["admin"]))):
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