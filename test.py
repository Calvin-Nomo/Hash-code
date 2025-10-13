# filename: main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Allow local frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.get('/greeting')
def welcome():
    return 'Hello Calvin'
# Dummy database
orders_db = [
    {
        "order_id": 10234,
        "client_id": 1,
        "date": "2025-10-12",
        "time": "15:45",
        "status": "pending",
        "total": 30.0,
        "items": [
            {"name": "Classic Burger", "qty": 2, "price": 19.98, "image": "/image/burger.jpg"},
            {"name": "Lemon Juice", "qty": 1, "price": 3.5, "image": "/image/drink.jpg"},
            {"name": "Chocolate Cake", "qty": 1, "price": 5.0, "image": "/image/dessert.jpg"}
        ]
    },
    {
        "order_id": 10233,
        "client_id": 1,
        "date": "2025-10-10",
        "time": "18:20",
        "status": "completed",
        "total": 24.5,
        "items": [
            {"name": "Margherita Pizza", "qty": 1, "price": 14.5, "image": "/image/pizza.jpg"},
            {"name": "Orange Juice", "qty": 2, "price": 10.0, "image": "/image/drink.jpg"}
        ]
    }
]

@app.get("/orders/{client_id}")
async def get_orders(client_id: int):
    client_orders = [o for o in orders_db if o["client_id"] == client_id]
    return client_orders

@app.put("/orders/cancel/{order_id}")
async def cancel_order(order_id: int):
    for order in orders_db:
        if order["order_id"] == order_id:
            if order["status"] == "pending":
                order["status"] = "canceled"
                return {"message": "Order canceled successfully"}
            else:
                raise HTTPException(status_code=400, detail="Cannot cancel completed or canceled orders")
    raise HTTPException(status_code=404, detail="Order not found")
