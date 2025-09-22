Create database Menu;
Create table Order(
Order_ID int AUTO_INCREMENT primary key, 
Order_date datetime, 
Order_type enum("Dine In", "Take Away"), 
No_Table int 
); 
