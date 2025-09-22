# welcome to my api
from fastapi import FASTAPI
from pydantic import Base model 

app=FASTAPI() 

@app.get(/)
def greetings():
    return {
     "Message ":"Hello World" 
}
