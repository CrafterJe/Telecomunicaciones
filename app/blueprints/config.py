import os

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'mi_secreto_super_seguro') 
