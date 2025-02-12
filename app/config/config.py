import os
from cryptography.fernet import Fernet

# Función para desencriptar el archivo .env.encrypted y cargar las variables de entorno
def load_env_from_encrypted():
    # Leer la clave de cifrado (asegúrate de que esta clave esté protegida)
    with open('encryption_key.key', 'rb') as key_file:
        key = key_file.read()

    cipher_suite = Fernet(key)

    # Leer el archivo cifrado
    with open('.env.encrypted', 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()

    # Desencriptar los datos
    decrypted_data = cipher_suite.decrypt(encrypted_data).decode('utf-8')

    # Cargar las variables de entorno directamente desde la memoria
    for line in decrypted_data.splitlines():
        if line.strip() and not line.startswith('#'):  # Ignorar líneas vacías y comentarios
            key, value = line.split('=', 1)  # Dividir en clave y valor
            os.environ[key] = value

# Cargar las variables de entorno desde el archivo .env.encrypted
load_env_from_encrypted()

# Acceder a las variables de entorno
MONGO_URI = os.getenv('MONGO_URI')