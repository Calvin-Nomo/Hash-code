from fastapi import APIRouter, HTTPException, Depends
from fastapi import Response
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.routers.notification import send_notification
import math
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
class OrderStatusUpdate(BaseModel):
    order_status: str
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
@router.get("/order_list")
def orders_list():
    cursor.execute("""SELECT 
    o.Order_ID,
    c.Client_Name,
    c.No_Telephone,
    o.Order_Date,
    o.Order_Type,
    COUNT(DISTINCT oi.No_Product) AS Total_Items,  -- count distinct products
    p.Total_Amount AS Total_Amount
FROM Orders o
JOIN Clients c 
    ON o.No_Client = c.No_Client
JOIN Order_Items oi 
    ON o.Order_ID = oi.Order_ID
JOIN Payment p 
    ON o.Order_ID = p.Order_ID
GROUP BY 
    o.Order_ID, 
    c.Client_Name, 
    c.No_Telephone, 
    o.Order_Date, 
    o.Order_Type,
    p.Total_Amount
ORDER BY o.Order_Date DESC;


""")
    return cursor.fetchall()


@router.get("/recent_orders")
def recent_order():
    cursor.execute("""SELECT 
    o.Order_ID,
    c.Client_Name,
    c.No_Telephone,
    o.Order_Type,
    p.Total_Amount,
    p.Payment_Status,
    p.Payment_Method,
    o.Order_Date,
    o.Order_Status
FROM Orders o
JOIN Payment p
    ON o.Order_ID = p.Order_ID
JOIN Clients c
    ON o.No_Client = c.No_Client
ORDER BY o.Order_Date DESC
LIMIT 8
;
""")
    return cursor.fetchall()

    
    
    
@router.get("/total_order")
def total_orders():
    cursor.execute("SELECT COUNT(*) AS total FROM Orders")
    return cursor.fetchone()
# Order Detail
# ---------------- GET Endpoint ----------------
@router.get("/order/{order_id}")
def get_order_detail(order_id: int):
    # -------- First query: Order + Client + Payment + Table + Reservation --------
    cursor.execute("""
SELECT  
  o.Order_ID,
  o.Order_Type,
  o.Order_Date,
o.Note,
o.Order_Status,
  p.Total_Amount,
  t.No_Table,
  p.Transaction_Fees,
  p.Payment_Status,
  p.Payment_Method,
  c.Client_Name,
  c.No_Telephone,
  c.Email,
  o.No_Reservation,
  r.Reservation_Date,
  r.No_Person
FROM Orders o
LEFT JOIN Payment p ON p.Order_ID = o.Order_ID
JOIN Clients c ON c.No_Client = o.No_Client
LEFT JOIN Tab t ON t.Table_ID = o.No_Table
LEFT JOIN Reservation r ON o.No_Reservation = r.No_Reservation
WHERE o.Order_ID = %s;
    """, (order_id,))
    
    order = cursor.fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # -------- Second query: Ordered items --------
    cursor.execute("""
        SELECT 
            oi.Order_ID,
            p.Image_link AS Image,
            p.Product_Name,
            SUM(oi.Quantity) AS Quantity,
            p.Price,
            SUM(oi.Quantity * p.Price) AS Total
        FROM Order_Items oi
        JOIN Product p ON oi.No_Product = p.No_Product
        WHERE oi.Order_ID = %s
        GROUP BY oi.Order_ID, p.Image_link, p.Product_Name, p.Price;
    """, (order_id,))
    items = cursor.fetchall()

    # -------- Build response --------
    return {
        "Order_ID": order["Order_ID"],
        "Order_Type": order["Order_Type"],
        "Order_Date": str(order["Order_Date"]),
        "Note": str(order["Note"]),
        "Order_Status": str(order["Order_Status"]),
        "No_Reservation": str(order["No_Reservation"]),
        "Total_Amount": float(order["Total_Amount"]),
        "No_Table": order["No_Table"],
        "Transaction_Fees": float(order["Transaction_Fees"]) if order["Transaction_Fees"] else 0,
        "Payment_Status": order["Payment_Status"],
        "Payment_Method": order["Payment_Method"],
        "Client_Name": order["Client_Name"],
        "No_Telephone": order["No_Telephone"],
        "Email": order["Email"],
        "Reservation_Date": str(order["Reservation_Date"]) if order["Reservation_Date"] else None,
        "No_Person": order["No_Person"],
        "Items": [dict(item) for item in items]
    }
@router.get("/order_history")
def get_order_history():
    # -------- Query: Orders + Payment + Table + Client + Reservation --------
    cursor.execute("""
    SELECT  
        o.Order_ID,
        o.Order_Type,
        o.Order_Date,
        o.Note,
        o.Order_Status,
        p.Total_Amount,
        t.No_Table,
        p.Transaction_Fees,
        p.Payment_Status,
        p.Payment_Method,
        c.Client_Name,
        c.No_Telephone,
        c.Email,
        o.No_Reservation,
        r.Reservation_Date,
        r.No_Person
    FROM Orders o
    LEFT JOIN Payment p ON p.Order_ID = o.Order_ID
    JOIN Clients c ON c.No_Client = o.No_Client
    LEFT JOIN Tab t ON t.Table_ID = o.No_Table
    LEFT JOIN Reservation r ON o.No_Reservation = r.No_Reservation
    ORDER BY o.Order_Date DESC;
    """)
    
    orders = cursor.fetchall()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this session")

    # -------- Query: Ordered items per order --------
    order_list = []
    for order in orders:
        cursor.execute("""
            SELECT 
                oi.Order_ID,
                p.Product_Name,
                SUM(oi.Quantity) AS Quantity,
                p.Price
            FROM Order_Items oi
            JOIN Product p ON oi.No_Product = p.No_Product
            WHERE oi.Order_ID = %s
            GROUP BY oi.Order_ID, p.Product_Name, p.Price;
        """, (order["Order_ID"],))
        items = cursor.fetchall()

        order_list.append({
            "Order_ID": order["Order_ID"],
            "Order_Type": order["Order_Type"],
            "Order_Date": str(order["Order_Date"]),
            "Note": str(order["Note"]) if order["Note"] else None,
            "Order_Status": str(order["Order_Status"]),
            "No_Reservation": str(order["No_Reservation"]) if order["No_Reservation"] else None,
            "Total_Amount": float(order["Total_Amount"]),
            "No_Table": order["No_Table"],
            "Transaction_Fees": float(order["Transaction_Fees"]) if order["Transaction_Fees"] else 0,
            "Payment_Status": order["Payment_Status"],
            "Payment_Method": order["Payment_Method"],
            "Client_Name": order["Client_Name"],
            "No_Telephone": order["No_Telephone"],
            "Email": order["Email"],
            "Reservation_Date": str(order["Reservation_Date"]) if order["Reservation_Date"] else None,
            "No_Person": order["No_Person"],
            "Items": [dict(item) for item in items]
        })
    
    return order_list

############
@router.get("/orderinfo")
def orderinfo():
    cursor.execute("""SELECT 
    p.Image_link AS Image,
    p.Product_Name AS Product_Name,
    SUM(oi.Quantity) AS Quantity,
    SUM(oi.Quantity * p.Price) AS Total
FROM Order_Items oi
JOIN Product p ON oi.No_Product = p.No_Product
GROUP BY p.Image_link, p.Product_Name;

""")
    return cursor.fetchall()

# ------------------- HELPER FUNCTIONS -----s--------------
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
async def create_order(data: FullOrderRequest):
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
                "INSERT INTO Clients(Client_Name, No_Telephone,Email) VALUES (%s, %s,%s)",
                (data.client.Client_Name, data.client.No_Telephone,data.client.Email)
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
        status = "Pending"
        cursor.execute(
            """INSERT INTO Orders(No_Client, No_Reservation, Order_Date, Order_Type, No_Table,Order_Status, Note)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (client_id, reservation_id, order_date, data.order.Order_Type, table_id,status, data.order.Note)
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
            """SELECT SUM(oi.Quantity * p.Price) AS total
               FROM Order_Items oi
               JOIN Product p ON oi.No_Product = p.No_Product
               WHERE oi.Order_ID = %s""",
            (order_id,)
        )
        total = cursor.fetchone()["total"] or 0
        def total_and_fees(total: float, method: str, tax=100):
            """
            Calculates the total amount including transaction fees based on payment method.
            Returns both total amount and fee.
            """
            if method in ['MTN Money', 'Orange Money']:
                blocks = math.ceil(total / 5000)  # count partial 5000 blocks
                fee = blocks * tax
                total_amount = total + fee
                return total_amount, fee
            else:
                return total, 0

        cursor.execute(
            """INSERT INTO Payment(Order_ID, Total_Amount, Payment_Date, Payment_Method, Payment_Status,Transaction_Fees)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (order_id, total_and_fees(total=total,method=data.payment.Payment_Method), datetime.utcnow(), data.payment.Payment_Method, "Payed",total_and_fees(total=total,method=data.payment.Payment_Method))
        )

        DB.commit()
        await send_notification(f'New  Order Created No #{order_id} Order Type-{data.order.Order_Type}')
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
                "INSERT INTO Clients(Client_Name, No_Telephone,Email) VALUES (%s, %s,, %s)",
                (data.client.Client_Name, data.client.No_Telephone,data.client.Email)
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
            """SELECT SUM(oi.Quantity * p.Price) AS total
               FROM Order_Items oi
               JOIN Product p ON oi.No_Product = p.No_Product
               WHERE oi.Order_ID = %s""",
            (order_id,)
        )
        total = cursor.fetchone()["total"]
        def total_and_fees(total:float,method:str,tax=100):
            if method=='MTN Money'or method=='Orange Money':
                amount=total//5000
                fee= amount * tax
                total_amount=total+fee
                return total_amount
            #here is in the case if the payment method is by cash
            else:
             return total
        def transaction_fees(total:float,method:str,tax=100):
            #initialising the fees variable to fee=0
            fee=0
            if method=='MTN Money'or method=='Orange Money':
                #if the method is mtn or orange it calculate the fees and returns it
                amount= total//5000
                fee = amount * tax
                return fee
            #here if the fees forthe cash is returns 0
            else:
                
             return fee
        cursor.execute(
            """UPDATE Payment
               SET Total_Amount=%s, Payment_Date=%s, Payment_Method=%s, Payment_Status=%s,Transaction_Fees=%s
               WHERE Order_ID=%s""",
            (total_and_fees(total=total,method=data.payment.Payment_Method), datetime.utcnow(), data.payment.Payment_Method, "Payed",transaction_fees(total=total,method=data.payment.Payment_Method),order_id)
            )

        DB.commit()
        return {"message": "Order updated successfully", "order_id": order_id}

    except HTTPException as e:
        DB.rollback()
        raise e
    except Exception as e:
        DB.rollback()
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
# ----- PUT Endpoint -----
@router.put("/order_status/{order_id}")
def update_order_status(order_id: int, data: OrderStatusUpdate):
    cursor.execute("SELECT Order_ID FROM orders WHERE Order_ID = %s", (order_id,))
    record = cursor.fetchone()

    if not record:
        raise HTTPException(status_code=404, detail="Order not found")

    cursor.execute("""
        UPDATE orders
        SET Order_Status = %s
        WHERE Order_ID = %s
    """, (data.order_status, order_id))

    DB.commit()

    return {
        "message": "Order status updated successfully",
        "order_id": order_id,
        "new_status": data.order_status
    }


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
