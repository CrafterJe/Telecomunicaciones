# Telecomunicaciones - Backend

El backend del proyecto **Telecomunicaciones** fue desarrollado en **Python** utilizando **Flask**.

## Requisitos

Antes de ejecutar el proyecto, asegúrate de tener instalado:

- Python 3.x
- Las dependencias necesarias listadas en `requirements.txt`

## Instalación

Clona el repositorio y accede a la carpeta del backend:

```bash
git clone https://github.com/tu-repositorio.git
cd backend
```

Instala las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

## Ejecución

El backend usa **Flask** con Blueprints para organizar las rutas de los diferentes módulos. También incorpora **Flask-CORS** para permitir peticiones desde el frontend.

Para iniciar el servidor, ejecuta el siguiente comando:

```bash
python main.py
```

El servidor se ejecutará y estará disponible en `http://localhost:5000/` por defecto.

### Configuración de CORS

El backend está configurado para aceptar peticiones desde:
- `http://localhost:4200`
- `http://192.168.100.12:4200`

### Blueprints registrados:

El backend está estructurado con **Blueprints** para modularizar las rutas:
- `productos`
- `usuarios`
- `pagos`
- `creditos`
- `transacciones`
- `carrito` (con prefijo `/carrito`)
- `signup`

## Configuración

Si necesitas modificar la API, revisa el archivo `.env`, donde puedes cambiar la API de la base de datos.

## Recursos adicionales

Para más información sobre el backend del proyecto, revisa la documentación del código o contacta al equipo de desarrollo.
