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
Seat_Number int,
Is_Occupied Boolean
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
