from cryptography.fernet import Fernet

# Función para desencriptar el archivo .env.encrypted
def decrypt_env_and_get_variables(encryption_key_path, encrypted_file_path):
    # Leer la clave de cifrado
    with open(encryption_key_path, 'rb') as key_file:
        key = key_file.read()

    cipher_suite = Fernet(key)

    # Leer el archivo cifrado
    with open(encrypted_file_path, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()

    # Desencriptar los datos
    decrypted_data = cipher_suite.decrypt(encrypted_data).decode('utf-8')

    # Parseado de las variables de entorno
    env_variables = {}
    for line in decrypted_data.splitlines():
        if line.strip() and not line.startswith('#'):  # Ignorar líneas vacías y comentarios
            key, value = line.split('=', 1)  # Dividir en clave y valor
            env_variables[key] = value

    return env_variables

# Rutas de los archivos
encryption_key_path = 'encryption_key.key'  # Ruta de la clave de cifrado
encrypted_file_path = '.env.encrypted'      # Ruta del archivo cifrado

# Desencriptar y obtener las variables
env_variables = decrypt_env_and_get_variables(encryption_key_path, encrypted_file_path)

# Acceder a una variable específica (por ejemplo, MONGO_URI)
mongo_uri = env_variables.get('MONGO_URI')
if mongo_uri:
    print(f"Cadena de conexión MongoDB: {mongo_uri}")
else:
    print("La variable MONGO_URI no se encontró en el archivo .env.encrypted")