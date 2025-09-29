Create database Order_System;
Create table Clients(
No_Client int AUTO_INCREMENT primary key, 
Client_Name VARCHAR (255),
No_Telephone VARCHAR (255) Unique 
);
Create table Orders(
Order_ID int AUTO_INCREMENT primary key, 
No_Reservation int NULL ,
Order_Date datetime Not Null, 
Order_Type enum("Dine In", "Take Away", "Reserve" ) NOT NULL , 
No_Table int Not Null, 
Note VARCHAR(255) Null, 
Foreign key (No_Reservation ) References Reservation (No_Reservation ) 
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
No_Client int,
Reservation_Date Date, 
Reservation_Time Time, 
No_Person int, 
Foreign key (No_Client ) References Clients(No_Client)
);

create table Stock(
No_Stock int auto_increment primary key,
No_Product int,
Quantity_available int,
Foreign key (No_Product) References Product(No_Product) 
);

