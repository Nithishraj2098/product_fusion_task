# product_fusion_task

#To database migration

In this case i use phpmysql database 

Before following the below commands , ensure in the folder backend/app/app/core/config.py  
set the "data_base" variable as your database name with the user credentials

1. cd backend/app  -> move the current directory to this place

2. alembic revision --autogenerate -m "your_comment" -> use this command to database migration

3. alembic upgrade heads -> to reflect on database use this 


#To run this Application

1. Move to backend/app/app  by cd backend/app/app 

2. uvicorn main:app --host 0.0.0.0 --port 8000 --reload -> use what port you want

3. open your browser and type localhost:8000/docs  -> To open swagger 

#Postman
Before  checking in post man
make authentication with Bearer Token (not for login and signup)


#ACTIVATE ENV

source env/bin/activate
