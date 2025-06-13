# TenisReserva en Docker

Este proyecto automatiza la reserva de canchas utilizando Selenium y Chrome. Se provee un contenedor Docker para ejecutarlo en cualquier sistema con Docker y un servidor X disponible.

## Configuración

1. Instala **Docker** y **docker-compose** en tu sistema Ubuntu.
2. Copia `.env.example` a `.env` y completa los valores de `URL_AGENDAMIENTO`, `URL_AGENDAMIENTO_TEST`, `RUT` y `CELULAR`.

```bash
cp .env.example .env
nano .env
```

3. Construye la imagen Docker:

```bash
docker compose build
```

## Ejecución

1. Permite que Docker utilice tu sesión X11 (solo se necesita una vez por sesión):

```bash
xhost +local:docker
```

2. Inicia el contenedor, el cual abrirá una ventana de Google Chrome en tu máquina:

```bash
docker compose up
```

El script `reserva_cancha.py` se ejecutará automáticamente. Chrome utilizará el directorio `~/.config/google-chrome-bot` para guardar su perfil de usuario (se monta como volumen para que persista entre ejecuciones).

Para detener el contenedor presiona `Ctrl+C` en la terminal.

## Ejecución sin docker-compose

Si prefieres correrlo directamente con `docker run`:

```bash
xhost +local:docker

docker run -it --rm \
  --env-file .env \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $HOME/chrome-bot:/home/rolando/.config/google-chrome-bot \
  --network host \
  tenis-reserva
```

Asegúrate de reemplazar `tenis-reserva` por el nombre que hayas asignado a la imagen si es distinto.
