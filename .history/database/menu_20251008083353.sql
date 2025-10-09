Create database Order_System;
Create table Clients(
No_Client int AUTO_INCREMENT primary key, 
Client_Name VARCHAR (255),
No_Telephone VARCHAR (255) Unique 
);
Create table Orders(
Order_ID int AUTO_INCREMENT primary key,
No_Client int,
No_Reservation int NULL  Unique,
Order_Date datetime Not Null, 
Order_Type Enum("Dine In", "Take Away", "Reservation" ) NOT NULL , 
No_Table int  Null, 
Note VARCHAR(255) Null,
Foreign key(No_Client) References Clients(No_Client),
Foreign key (No_Reservation ) References Reservation (No_Reservation ), 
Foreign key (No_Table ) References Tab(Table_ID) 
); 
Create table Product(
No_Product int AUTO_INCREMENT primary key, 
Product_Name VARCHAR(255),
Product_Description VARCHAR(255) Null, 
Category VARCHAR(255),
Unit_Price float, 
Image_link VARCHAR(255) 
);
Create table Order_Items(
Item_ID int AUTO_INCREMENT primary key, 
Order_ID int,
No_Product int, 
Quantity int, 
Foreign key (No_Product) References Product(No_Product), 
Foreign key (Order_ID ) References Orders(Order_ID) 
);
Create Table Tab(
Table_ID int AUTO_INCREMENT primary key,
No_Table int Unique,
Seat_Number int
);
Create table Payment (
Payment_ID int AUTO_INCREMENT primary key, 
Order_ID int, 
Total_Amount float, 
Payment_Date datetime, 
Payment_Method enum("Cash", "MTN Money", "Orange Money" ) NOT NULL ,
Payment_Status VARCHAR(255), 
Foreign key (Order_ID ) References Orders(Order_ID) 
);

Create table Reservation (
No_Reservation int AUTO_INCREMENT primary key, 
No_Client int Unique,
No_Table int,
Reservation_Date Date, 
Reservation_Time Time, 
No_Person int, 
Foreign key (No_Client ) References Clients(No_Client),
Foreign key(No_Table) References Tab(Table_ID)
);

create table Stock(
No_Stock int auto_increment primary key,
No_Product int,
Quantity_available int,
Foreign key (No_Product) References Product(No_Product) 
);
SELECT 
    o.Order_ID,
    o.Order_Type,
    SUM(oi.Quantity * p.Unit_Price) AS Total_Amount
FROM Orders o
INNER JOIN Order_Items oi ON o.Order_ID = oi.Order_ID
INNER JOIN Product p ON oi.No_Product = p.No_Product
GROUP BY o.Order_ID,o.Order_Type;
select*  from Payment;
select*  from Order_items;
select* from Orders;
select * from product;
select * from tab;
select* from Stock;
UPDATE Payment p
JOIN (
    SELECT 
        o.Order_ID,
        SUM(oi.Quantity * pr.Unit_Price) AS Correct_Total
    FROM Orders o
    JOIN Order_Items oi ON o.Order_ID = oi.Order_ID
    JOIN Product pr ON oi.No_Product = pr.No_Product
    GROUP BY o.Order_ID
) AS calculated ON p.Order_ID = calculated.Order_ID
SET p.Total_Amount = calculated.Correct_Total;

UPDATE Payment p
JOIN (
    SELECT 
        o.Order_ID,
        SUM(oi.Quantity * pr.Unit_Price) AS Correct_Total
    FROM Orders o
    JOIN Order_Items oi ON o.Order_ID = oi.Order_ID
    JOIN Product pr ON oi.No_Product = pr.No_Product
    GROUP BY o.Order_ID
) AS calculated ON p.Order_ID = calculated.Order_ID
SET p.Total_Amount = calculated.Correct_Total
WHERE p.Order_ID = calculated.Order_ID;

UPDATE Payment p
JOIN (
    SELECT 
        o.Order_ID,
        SUM(oi.Quantity * pr.Unit_Price) AS Correct_Total
    FROM Orders o
    JOIN Order_Items oi ON o.Order_ID = oi.Order_ID
    JOIN Product pr ON oi.No_Product = pr.No_Product
    WHERE o.Order_ID = 16
    GROUP BY o.Order_ID
) AS calculated ON p.Order_ID = calculated.Order_ID
SET 
    p.Total_Amount = calculated.Correct_Total,
    p.Payment_Date = CURDATE(),               -- or your specific date
    p.Payment_Method = 'MTN Money',
    p.Payment_Status = 'Completed'
WHERE p.Order_ID = calculated.Order_ID;

SET SQL_SAFE_UPDATES =1;
INSERT INTO Product (Product_Name, Unit_Price, Category, Product_Description, Image_Link) VALUES
('Margherita Pizza', 8.99, 'Pizza', 'Classic pizza with tomato sauce and cheese', 'images/margherita.jpg'),
('Pepperoni Pizza', 10.99, 'Pizza', 'Pizza topped with pepperoni slices', 'images/pepperoni.jpg'),
('Cheeseburger', 7.50, 'Burger', 'Juicy beef burger with cheese', 'images/cheeseburger.jpg'),
('Chicken Burger', 7.00, 'Burger', 'Grilled chicken burger with lettuce and mayo', 'images/chicken_burger.jpg'),
('Veggie Burger', 6.50, 'Burger', 'Vegetarian burger with grilled veggies', 'images/veggie_burger.jpg'),
('French Fries', 3.00, 'Sides', 'Crispy golden fries', 'images/fries.jpg'),
('Onion Rings', 3.50, 'Sides', 'Crispy fried onion rings', 'images/onion_rings.jpg'),
('Caesar Salad', 5.50, 'Salad', 'Fresh romaine lettuce with Caesar dressing', 'images/caesar_salad.jpg'),
('Greek Salad', 5.99, 'Salad', 'Salad with feta, olives, and tomatoes', 'images/greek_salad.jpg'),
('Spaghetti Bolognese', 9.50, 'Pasta', 'Spaghetti with rich meat sauce', 'images/spaghetti.jpg'),
('Fettuccine Alfredo', 9.99, 'Pasta', 'Creamy Alfredo sauce with fettuccine', 'images/fettuccine.jpg'),
('Chicken Wings', 6.99, 'Sides', 'Spicy grilled chicken wings', 'images/wings.jpg'),
('Mozzarella Sticks', 4.99, 'Sides', 'Fried mozzarella cheese sticks', 'images/mozzarella.jpg'),
('Taco', 3.99, 'Mexican', 'Soft taco with beef and veggies', 'images/taco.jpg'),
('Burrito', 7.50, 'Mexican', 'Flour tortilla with rice, beans, and meat', 'images/burrito.jpg');
INSERT INTO Stock (No_Product, Quantity_Available) VALUES
(1, 50),
(2, 40),
(3, 60),
(4, 50),
(5, 30),
(6, 100),
(7, 80),
(8, 40),
(9, 35),
(10, 45),
(11, 40),
(12, 60),
(13, 50),
(14, 70),
(15, 50);
INSERT INTO Tab (No_Table, Seat_Number) VALUES
(1,4),
(2, 5),
(3,5);
CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    Role ENUM('admin', 'waiter') NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

