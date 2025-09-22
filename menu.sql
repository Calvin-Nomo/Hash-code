Create database Menu;
Create table Order(
Order_ID int AUTO_INCREMENT primary key, 
Order_date datetime, 
Order_type enum("Dine In", "Take Away"), 
No_Table int 
); 
Create table Note(
Note_ID int AUTO_INCREMENT primary key, 
Order_ID int, 
Note VARCHAR(255),
Foriegn key(Order_ID) References Order(Order_ID ) 
);
