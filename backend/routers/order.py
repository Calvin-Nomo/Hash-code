from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import pymysql

from dependencies import require_role
from backend.data.credentials import Mysql_password, Database_Name
from backend.routers.order_items import Items
from backend.routers.client import Client
from backend.routers.payment import Payment
from backend.routers.reservation import Reservation

# ------------------- DATABASE -------------------
DB = pymysql.connect(
    host="localhost",
    user="root",
    password=Mysql_password,
    database=Database_Name,
    cursorclass=pymysql.cursors.DictCursor
)

cursor = DB.cursor()

# ------------------- MODELS -------------------
class Order(BaseModel):
    Order_Type: str
    No_Table: Optional[int] = None
    Note: Optional[str] = None
    items: List[Items]

class FullOrderRequest(BaseModel):
    client: Client
    reservation: Optional[Reservation] = None
    order: Order
    payment: Payment

# ------------------- ROUTER -------------------
router = APIRouter(prefix="/order", tags=["order"])

# ------------------- GET ROUTES -------------------
@router.get("/")
def greetings():
    return {"Message": "Hello World"}

@router.get("/Order")
def get_orders(current_user: dict = Depends(require_role(["waiter", "admin"]))):
    cursor.execute("SELECT * FROM Orders")
    return cursor.fetchall()

@router.get("/total_order")
def total_orders(current_user: dict = Depends(require_role(["waiter", "admin"]))):
    cursor.execute("SELECT COUNT(Order_ID) AS total FROM Orders")
    return cursor.fetchone()

# ------------------- HELPER FUNCTIONS -------------------
def check_table_availability(table_id: int, date: datetime):
    cursor.execute(
        "SELECT * FROM Reservation WHERE No_Table=%s AND Reservation_Date=%s",
        (table_id, date)
    )
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Table already reserved for this time")

def check_dine_in_availability(table_id: int):
    cursor.execute(
        "SELECT * FROM Orders WHERE No_Table=%s AND Order_Type='Dine In' AND Order_Status='Active'",
        (table_id,)
    )
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Table currently occupied")

# ------------------- POST: CREATE FULL ORDER -------------------
@router.post("/FullOrderRequest")
def create_order(data: FullOrderRequest, current_user: dict = Depends(require_role(["admin"]))):
    try:
        cursor = DB.cursor()
        DB.begin()  # start transaction

        # 1️⃣ Check or create client
        cursor.execute("SELECT No_Client FROM Clients WHERE No_Telephone=%s", (data.client.No_Telephone,))
        client = cursor.fetchone()
        if client:
            client_id = client["No_Client"]
        else:
            cursor.execute(
                "INSERT INTO Clients(Client_Name, No_Telephone) VALUES (%s, %s)",
                (data.client.Client_Name, data.client.No_Telephone)
            )
            client_id = cursor.lastrowid

        # 2️⃣ Handle Table / Reservation / Dine In
        reservation_id = None
        table_id = None

        if data.order.Order_Type == "Reservation":
            if not data.reservation:
                raise HTTPException(status_code=400, detail="Reservation details required")
            check_table_availability(data.reservation.No_Table, data.reservation.Reservation_Date)
            cursor.execute(
                """INSERT INTO Reservation(No_Client, No_Table, Reservation_Date, No_Person)
                   VALUES (%s, %s, %s, %s)""",
                (client_id, data.reservation.No_Table, data.reservation.Reservation_Date, data.reservation.No_Person)
            )
            reservation_id = cursor.lastrowid
            table_id = data.reservation.No_Table

        elif data.order.Order_Type == "Dine In":
            if not data.order.No_Table:
                raise HTTPException(status_code=400, detail="Table number required")
            cursor.execute("SELECT * FROM Tab WHERE Table_ID=%s", (data.order.No_Table,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Table not found")
            check_dine_in_availability(data.order.No_Table)
            table_id = data.order.No_Table

        # 3️⃣ Create Order
        order_date = datetime.utcnow()
        cursor.execute(
            """INSERT INTO Orders(No_Client, No_Reservation, Order_Date, Order_Type, No_Table, Note)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (client_id, reservation_id, order_date, data.order.Order_Type, table_id, data.order.Note)
        )
        order_id = cursor.lastrowid

        # 4️⃣ Insert Items and Update Stock
        for item in data.order.items:
            cursor.execute("SELECT Quantity_Available FROM Stock WHERE No_Product=%s", (item.No_Product,))
            stock = cursor.fetchone()
            if not stock:
                raise HTTPException(status_code=404, detail=f"Product {item.No_Product} not found")
            if stock["Quantity_Available"] < item.Quantity:
                raise HTTPException(status_code=400, detail=f"Not enough stock for product {item.No_Product}")

            cursor.execute(
                "INSERT INTO Order_Items(Order_ID, No_Product, Quantity) VALUES (%s, %s, %s)",
                (order_id, item.No_Product, item.Quantity)
            )
            cursor.execute(
                "UPDATE Stock SET Quantity_Available = Quantity_Available - %s WHERE No_Product=%s",
                (item.Quantity, item.No_Product)
            )

        # 5️⃣ Insert Payment
        cursor.execute(
            """SELECT SUM(oi.Quantity * p.Unit_Price) AS total
               FROM Order_Items oi
               JOIN Product p ON oi.No_Product = p.No_Product
               WHERE oi.Order_ID = %s""",
            (order_id,)
        )
        total = cursor.fetchone()["total"]
        cursor.execute(
            """INSERT INTO Payment(Order_ID, Total_Amount, Payment_Date, Payment_Method, Payment_Status)
               VALUES (%s, %s, %s, %s, %s)""",
            (order_id, total, datetime.utcnow(), data.payment.Payment_Method, "Paid")
        )

        DB.commit()
        return {"message": "Order placed successfully", "order_id": order_id}

    except HTTPException as e:
        DB.rollback()
        raise e
    except Exception as e:
        DB.rollback()
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

# ------------------- PUT: UPDATE ORDER -------------------
@router.put("/FullOrderRequest_Update/{order_id}")
def update_order(order_id: int, data: FullOrderRequest, current_user: dict = Depends(require_role(["admin"]))):
    try:
        cursor = DB.cursor()
        DB.begin()

        # 1️⃣ Check if order exists
        cursor.execute("SELECT * FROM Orders WHERE Order_ID=%s", (order_id,))
        existing_order = cursor.fetchone()
        if not existing_order:
            raise HTTPException(status_code=404, detail="Order not found")

        # 2️⃣ Check or create client
        cursor.execute("SELECT No_Client FROM Clients WHERE No_Telephone=%s", (data.client.No_Telephone,))
        client = cursor.fetchone()
        if client:
            client_id = client["No_Client"]
        else:
            cursor.execute(
                "INSERT INTO Clients(Client_Name, No_Telephone) VALUES (%s, %s)",
                (data.client.Client_Name, data.client.No_Telephone)
            )
            client_id = cursor.lastrowid

        # 3️⃣ Handle Table / Reservation / Dine In
        reservation_id = None
        table_id = None

        if data.order.Order_Type == "Reservation":
            if not data.reservation:
                raise HTTPException(status_code=400, detail="Reservation details required")

            if existing_order["No_Reservation"]:
                cursor.execute(
                    """UPDATE Reservation
                       SET No_Table=%s, Reservation_Date=%s, No_Person=%s
                       WHERE Reservation_ID=%s""",
                    (data.reservation.No_Table, data.reservation.Reservation_Date,
                     data.reservation.No_Person, existing_order["No_Reservation"])
                )
                reservation_id = existing_order["No_Reservation"]
            else:
                check_table_availability(data.reservation.No_Table, data.reservation.Reservation_Date)
                cursor.execute(
                    "INSERT INTO Reservation(No_Client, No_Table, Reservation_Date, No_Person) VALUES (%s,%s,%s,%s)",
                    (client_id, data.reservation.No_Table, data.reservation.Reservation_Date, data.reservation.No_Person)
                )
                reservation_id = cursor.lastrowid
            table_id = data.reservation.No_Table

        elif data.order.Order_Type == "Dine In":
            if not data.order.No_Table:
                raise HTTPException(status_code=400, detail="Table number required")
            cursor.execute("SELECT * FROM Tab WHERE Table_ID=%s", (data.order.No_Table,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Table not found")
            check_dine_in_availability(data.order.No_Table)
            table_id = data.order.No_Table

        # 4️⃣ Update Order
        cursor.execute(
            """UPDATE Orders
               SET No_Client=%s, No_Reservation=%s, Order_Type=%s, No_Table=%s, Note=%s
               WHERE Order_ID=%s""",
            (client_id, reservation_id, data.order.Order_Type, table_id, data.order.Note, order_id)
        )

        # 5️⃣ Remove old items and restore stock
        cursor.execute("SELECT No_Product, Quantity FROM Order_Items WHERE Order_ID=%s", (order_id,))
        for item in cursor.fetchall():
            cursor.execute(
                "UPDATE Stock SET Quantity_Available = Quantity_Available + %s WHERE No_Product=%s",
                (item["Quantity"], item["No_Product"])
            )
        cursor.execute("DELETE FROM Order_Items WHERE Order_ID=%s", (order_id,))

        # 6️⃣ Insert new items and update stock
        for item in data.order.items:
            cursor.execute("SELECT Quantity_Available FROM Stock WHERE No_Product=%s", (item.No_Product,))
            stock = cursor.fetchone()
            if not stock:
                raise HTTPException(status_code=404, detail=f"Product {item.No_Product} not found")
            if stock["Quantity_Available"] < item.Quantity:
                raise HTTPException(status_code=400, detail=f"Not enough stock for product {item.No_Product}")

            cursor.execute(
                "INSERT INTO Order_Items(Order_ID, No_Product, Quantity) VALUES (%s,%s,%s)",
                (order_id, item.No_Product, item.Quantity)
            )
            cursor.execute(
                "UPDATE Stock SET Quantity_Available = Quantity_Available - %s WHERE No_Product=%s",
                (item.Quantity, item.No_Product)
            )

        # 7️⃣ Update Payment
        cursor.execute(
            """SELECT SUM(oi.Quantity * p.Unit_Price) AS total
               FROM Order_Items oi
               JOIN Product p ON oi.No_Product = p.No_Product
               WHERE oi.Order_ID = %s""",
            (order_id,)
        )
        total = cursor.fetchone()["total"]
        cursor.execute(
            """UPDATE Payment
               SET Total_Amount=%s, Payment_Date=%s, Payment_Method=%s, Payment_Status=%s
               WHERE Order_ID=%s""",
            (total, datetime.utcnow(), data.payment.Payment_Method, "Paid", order_id)
        )

        DB.commit()
        return {"message": "Order updated successfully", "order_id": order_id}

    except HTTPException as e:
        DB.rollback()
        raise e
    except Exception as e:
        DB.rollback()
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

# ------------------- DELETE ORDER -------------------
@router.delete("/order/{order_id}")
def delete_order(order_id: int, current_user: dict = Depends(require_role(["admin"]))):
    try:
        cursor = DB.cursor()
        DB.begin()

        cursor.execute("SELECT * FROM Orders WHERE Order_ID=%s", (order_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Order not found")

        cursor.execute("DELETE FROM Order_Items WHERE Order_ID=%s", (order_id,))
        cursor.execute("DELETE FROM Payment WHERE Order_ID=%s", (order_id,))
        cursor.execute("DELETE FROM Orders WHERE Order_ID=%s", (order_id,))

        DB.commit()
        return {"message": "Order and related records deleted successfully"}

    except HTTPException as e:
        DB.rollback()
        raise e
    except Exception as e:
        DB.rollback()
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
