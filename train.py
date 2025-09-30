# # db.py
# import pymysql

# def get_connection():
#     return pymysql.connect(
#         host="localhost",
#         user="your_user",
#         password="your_password",
#         database="orders_db",
#         cursorclass=pymysql.cursors.DictCursor,
#         autocommit=True
#     )

# # routers/order_items.py
# from typing import List
# from pydantic import BaseModel
# from db import get_connection

# # Local Pydantic model
# class OrderItem(BaseModel):
#     product_id: int
#     quantity: int
#     price: float

# def save_order_items(order_id: int, items: List[OrderItem]):
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             for item in items:
#                 cursor.execute(
#                     """
#                     INSERT INTO order_items (order_id, product_id, quantity, price)
#                     VALUES (%s, %s, %s, %s)
#                     """,
#                     (order_id, item.product_id, item.quantity, item.price)
#                 )
#     finally:
#         conn.close()


# order_id = cursor.lastrowid

# routers/orders.py
# from fastapi import APIRouter
# from typing import List
# from pydantic import BaseModel
# from db import get_connection
# from routers.order_items import OrderItem, save_order_items

# router = APIRouter(prefix="/orders", tags=["Orders"])

# # Local Pydantic model for Order
# class Order(BaseModel):
#     items: List[OrderItem]

# @router.post("/")
# def create_order(order: Order):
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             # Insert into orders table
#             cursor.execute("INSERT INTO orders () VALUES ()")
#             order_id = cursor.lastrowid

#         # Save order items using function from order_items.py
#         save_order_items(order_id, order.items)

#         return {
#             "message": "Order saved",
#             "order_id": order_id,
#             "items_count": len(order.items)
#         }

#     except Exception as e:
#         return {"error": str(e)}
#     finally:
#         conn.close()
import pandas as pd

# Restaurant menu data with higher prices
data = {
    "Product_Name": [
        "Grilled Lobster", "Wagyu Beef Steak", "Truffle Pasta", "Seafood Platter", "Butter Chicken",
        "Jollof Rice & Chicken", "Lamb Chops", "Prawn Fried Rice", "Shawarma Deluxe", "Chicken Alfredo",
        "Tandoori Platter", "Vegetarian Curry", "Beef Suya", "Sushi Combo", "Chicken Katsu",
        "Spicy Ramen", "Biryani Special", "Caesar Salad", "Mixed Grill", "Chocolate Lava Cake",
        "Fruit Parfait", "Fresh Pineapple Juice", "Chilled Champagne", "Virgin Mojito", "Red Velvet Cake"
    ],
    "Product_Description": [
        "Grilled whole lobster with garlic butter and lemon.",
        "Premium Wagyu steak grilled to perfection with sides.",
        "Creamy pasta topped with black truffles and cheese.",
        "Assortment of crab, prawns, mussels, and calamari.",
        "Traditional Indian dish with creamy tomato sauce.",
        "Nigerian-style rice with grilled spicy chicken.",
        "Tender lamb chops served with mashed potatoes.",
        "Fried rice with jumbo prawns and vegetables.",
        "Large shawarma wrap with beef, chicken, and extras.",
        "Fettuccine pasta in creamy Alfredo sauce with chicken.",
        "Mixed tandoori meats served with naan and chutneys.",
        "Mixed vegetables in spicy Indian curry sauce.",
        "Spicy skewered beef grilled with onions and pepper.",
        "Assorted sushi rolls with soy sauce and wasabi.",
        "Crispy fried chicken with rice and katsu sauce.",
        "Hot noodle soup with spicy broth, pork, and egg.",
        "Fragrant rice with spiced chicken or mutton.",
        "Romaine lettuce, croutons, and creamy dressing.",
        "Grilled beef, chicken, sausage, and vegetables.",
        "Chocolate cake with molten lava center and ice cream.",
        "Yogurt parfait with granola and fresh fruits.",
        "Freshly blended pineapple juice served cold.",
        "Premium bottle of French champagne.",
        "Minty lime drink served over crushed ice.",
        "Moist red velvet cake slice with cream cheese frosting."
    ],
    "Category": [
        "Main Course", "Main Course", "Main Course", "Main Course", "Main Course",
        "Main Course", "Main Course", "Main Course", "Main Course", "Main Course",
        "Main Course", "Main Course", "Appetizer", "Main Course", "Main Course",
        "Main Course", "Main Course", "Appetizer", "Main Course", "Dessert",
        "Dessert", "Beverage", "Beverage", "Beverage", "Dessert"
    ],
    "Unit_Price": [
        25000, 40000, 18000, 30000, 15000,
        12000, 22000, 14000, 10000, 13000,
        20000, 11000, 8000, 17000, 12500,
        9500, 14000, 7000, 23000, 6500,
        5500, 3000, 75000, 3500, 6000
    ],
    "Image_link": [
        "https://example.com/images/grilled_lobster.jpg",
        "https://example.com/images/wagyu_steak.jpg",
        "https://example.com/images/truffle_pasta.jpg",
        "https://example.com/images/seafood_platter.jpg",
        "https://example.com/images/butter_chicken.jpg",
        "https://example.com/images/jollof_rice_chicken.jpg",
        "https://example.com/images/lamb_chops.jpg",
        "https://example.com/images/prawn_fried_rice.jpg",
        "https://example.com/images/shawarma_deluxe.jpg",
        "https://example.com/images/chicken_alfredo.jpg",
        "https://example.com/images/tandoori_platter.jpg",
        "https://example.com/images/vegetarian_curry.jpg",
        "https://example.com/images/beef_suya.jpg",
        "https://example.com/images/sushi_combo.jpg",
        "https://example.com/images/chicken_katsu.jpg",
        "https://example.com/images/spicy_ramen.jpg",
        "https://example.com/images/biryani_special.jpg",
        "https://example.com/images/caesar_salad.jpg",
        "https://example.com/images/mixed_grill.jpg",
        "https://example.com/images/chocolate_lava_cake.jpg",
        "https://example.com/images/fruit_parfait.jpg",
        "https://example.com/images/pineapple_juice.jpg",
        "https://example.com/images/champagne.jpg",
        "https://example.com/images/virgin_mojito.jpg",
        "https://example.com/images/red_velvet_cake.jpg"
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("restaurant_menu.csv", index=False)

print("CSV file 'restaurant_menu_high_pricing.csv' created successfully.")
