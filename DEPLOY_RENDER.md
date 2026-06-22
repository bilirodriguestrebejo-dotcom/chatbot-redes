# Deploy en Render

Esta app Flask puede publicarse como un Web Service en Render.

## Valores para Render

- Language: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn wsgi:app`

## Pasos

1. Sube esta carpeta completa a un repositorio de GitHub.
2. Entra a https://dashboard.render.com/.
3. Crea un servicio nuevo con `New > Web Service`.
4. Conecta tu repositorio de GitHub.
5. Usa los valores indicados arriba.
6. Espera a que termine el deploy.

Cuando Render termine, te dara una URL publica parecida a:

`https://nombre-de-tu-app.onrender.com`

Esa URL la puedes enviar a tus amigos y funcionara aunque cierres Visual Studio Code o apagues tu computadora.
