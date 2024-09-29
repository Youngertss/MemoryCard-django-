How to start:
1. activate your virtual envirement and install the requirements (pip install -r requirements.txt)
2. cd memorycard
3. python manage.py runserver
*Note: on directory memorycard/memorycard you should create a file "config.py" with two variable - POSTGRES_USER and POSTGRES_PASS


If connection with DATABASE isn't works, try next:
delete migrations from directory memorycard/game/migrations
Than write down this: 
- python manage.py makemigrations
- python manage.py migrate
  
