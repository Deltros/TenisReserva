FROM python:3.10-slim

# Evita preguntas de configuración
ENV DEBIAN_FRONTEND=noninteractive

# Instalamos dependencias para Google Chrome
RUN apt-get update && apt-get install -y \
    wget gnupg ca-certificates fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libnspr4 libnss3 libxss1 libxcb-dri3-0 libu2f-udev libdrm2 libgbm1 --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Instalamos Google Chrome
RUN wget -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Creamos usuario de la app
RUN useradd -m rolando

# Instala dependencias de Python
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Directorio de trabajo
USER rolando
WORKDIR /home/rolando/app

# Carpeta para el perfil de Chrome utilizado por el script
RUN mkdir -p /home/rolando/.config/google-chrome-bot

# Copiamos el proyecto
COPY --chown=rolando:rolando . .

CMD ["python", "reserva_cancha.py"]
