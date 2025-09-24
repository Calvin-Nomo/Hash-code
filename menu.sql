Create database Order_System;
Create table Order(
Order_ID int AUTO_INCREMENT primary key, 
Order_Date datetime Not Null, 
Order_Type enum("Dine In", "Take Away") NOT NULL , 
No_Table int Not Null, 
Note VARCHAR(255) Null 
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
Foriegn key (No_Product) References Product(No_Produit), 
Foriegn key (Order_ID ) References Order(Order_ID) 
); 
Create table Payment (
Payment_ID int AUTO_INCREMENT primary key, 
Order_ID int, 
Total_Amount float, 
Payment_Date datetime, 
Payment_Method enum("Cash", "MTN Money", "Orange Money" ) NOT NULL 
Payment_Status
 VARCHAR(255), 
Foriegn key (Order_ID ) References Order(Order_ID) 
);