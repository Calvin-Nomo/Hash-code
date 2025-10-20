import os
from dotenv import find_dotenv,load_dotenv
doenv_path=find_dotenv()
get_env=load_dotenv(doenv_path)
ACCESS_SECRET_KEY=os.getenv('ACCESS_SECRET_KEY')
REFRESH_SECRET_KEY =os.getenv('REFRESH_SECRET_KEY')
Mysql_password=os.getenv('Mysql_password')
Database_Name = os.getenv('Database_Name')