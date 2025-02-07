from cryptography.fernet import Fernet

# Generar una clave de cifrado
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Leer el archivo .env
with open('.env', 'rb') as file:
    env_data = file.read()

# Cifrar los datos
encrypted_data = cipher_suite.encrypt(env_data)

# Guardar el archivo cifrado
with open('.env.encrypted', 'wb') as encrypted_file:
    encrypted_file.write(encrypted_data)

# Guardar la clave en un archivo seguro
with open('encryption_key.key', 'wb') as key_file:
    key_file.write(key)

print("Archivo .env cifrado exitosamente como .env.encrypted")