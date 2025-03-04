import os

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'mi_secreto_super_seguro') 
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY', '6LcU3egqAAAAAOr--Z-g4ppU0ggVKf1OqruGBXb_')