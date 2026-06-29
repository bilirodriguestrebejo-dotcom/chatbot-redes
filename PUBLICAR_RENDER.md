# 🚀 Publicar en Render - PASO A PASO

## PARTE 1 — Subir código a GitHub

### Si ya tienes Git instalado (línea de comandos):

1. **Abre PowerShell o CMD** en la carpeta del proyecto:
   ```
   cd "c:\Users\Bili RT\Downloads\hello"
   ```

2. **Inicializar Git** (si es la primera vez):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - chatbot ISP"
   ```

3. **Crear repositorio en GitHub:**
   - Ve a https://github.com/new
   - Nombre: `chatbot-bili`
   - Marca "Public"
   - **NO marques** "Add a README file"
   - Haz clic en "Create repository"

4. **Subir archivos (IMPORTANTE - haz esto exactamente):**
   - En la página del repositorio, verás "Quick setup" o "uploading an existing file"
   - Haz clic en **"uploading an existing file"** o el link que diga algo similar
   - Arrastra **TODOS** los archivos desde `c:\Users\Bili RT\Downloads\hello` a la página
   - O haz clic en "choose your files" y selecciona TODOS los archivos de la carpeta
   - En "Commit changes" escribe: `Chatbot BILI - archivos iniciales`
   - Haz clic en **"Commit changes"**

4. **Conectar y subir:**
   ```bash
    git remote add origin https://github.com/TU_USUARIO/chatbot-bili.git
   git branch -M main
   git push -u origin main
   ```
   (Reemplaza `TU_USUARIO` con tu nombre de usuario de GitHub)

### Si NO tienes Git instalado:

1. **Descarga Git:** https://git-scm.com/download/win
2. **Instálalo** (siguiente, siguiente, siguiente)
3. **Reinicia tu computadora**
4. **Sigue los pasos de arriba**

---

## PARTE 2 — Desplegar en Render

1. **Ve a Render:** https://render.com
2. **Haz clic en "Sign Up"** (arriba a la derecha)
3. **Elige "Sign up with GitHub"**
4. **Autoriza a Render** para acceder a tus repositorios

5. **En el Dashboard, haz clic en "New +"** → **"Web Service"**

6. **Conecta tu repositorio:**
   - Busca `chatbot-bili` en la lista
   - Haz clic en **"Connect"**

7. **Configura el servicio:**

   | Campo | Valor |
   |-------|-------|
   | **Name** | `chatbot-bili` |
   | **Language** | `Python 3` |
   | **Branch** | `main` |
   | **Root Directory** | *(déjalo vacío)* |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `waitress-serve --port=$PORT wsgi:app` |
   | **Plan** | `Free` |

8. **Haz clic en "Deploy Web Service"**

9. **Espera 2-5 minutos** mientras Render:
   - Instala las dependencias
   - Construye la aplicación
   - La despliega

10. **Cuando veas "Live"** en verde, tu chatbot está público en:
    👉 `https://chatbot-bili.onrender.com`

---

## ✅ Verificar que funciona

1. Abre la URL: `https://chatbot-bili.onrender.com`
2. Escribe: `autogestión`
3. Teléfono: `809-555-1234`
4. Código: `BILI2024`

---

## 💡 Tips importantes

- **Primera carga tarda 30-50 segundos** (Render "despierta" la app)
- **Si falla:** Ve a la pestaña "Logs" en Render para ver el error
- **La base de datos se reinicia** cada vez que Render reinicia (pero el código `BILI2024` siempre funciona)

---

## 🔄 Para actualizar después

Cada vez que hagas cambios:
1. Sube el código a GitHub: `git push`
2. En Render: **Manual Deploy** → **Deploy latest commit**

**Nota:** El comando de inicio usa `waitress-serve` en lugar de `gunicorn` para mayor compatibilidad.
