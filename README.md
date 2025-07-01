# TenisReserva

Script automatizado para reservar horas de tenis usando Selenium.

## Configuración

1. Copia `.env.example` a `.env` y edita los valores con tus datos reales.
2. Ajusta `CHROME_USER_DATA_DIR` si quieres guardar el perfil de Chrome en otra ubicación. El valor por defecto es `/tmp/chrome-profile`.

## Uso con Docker Compose

El repositorio incluye un `docker-compose.yml` que ejecuta el script en un contenedor.

```bash
# Ejecuta una vez para construir la imagen y lanzar el contenedor
docker compose up
```

Los valores de entorno se cargan desde el archivo `.env`.

