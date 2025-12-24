# Guía de Monetización y Distribución 💰

Esta guía explica cómo convertir este proyecto en un negocio rentable.

## 1. Base de Datos en la Nube (PostgreSQL)
Para un sistema comercial, necesitas una base de datos centralizada. Recomendamos:
- **Neon.tech**: Ofrece PostgreSQL gratuito, rápido y sin servidores que administrar.
- **Supabase**: Incluye base de datos y sistema de autenticación ya listo.

**Instrucciones:**
1. Crea un proyecto en [Neon.tech](https://neon.tech).
2. Obtén la `Connection String`.
3. En el proyecto, usa la librería `psycopg2` para conectar `src/auth/manager.py` con tu tabla de usuarios.

## 2. Generación del ejecutable (.EXE)
Para vender el software, debes entregarlo como un único archivo que no requiera instalar Python.

**Instrucciones:**
1. Instala PyInstaller: `pip install pyinstaller`
2. Ejecuta el comando desde la raíz:
   ```bash
   pyinstaller --noconfirm --onefile --windowed --name "GeneradorHorariosPro" --add-data "src;src" --add-data "assets;assets" launcher_desktop.py
   ```
3. El archivo final aparecerá en la carpeta `dist/`.

## 3. Modelo de Negocio Sugerido
- **Versión Desktop**: Venta de licencias únicas o anuales mediante una "Key" que el usuario ingresa al abrir el .exe.
- **Versión Web**: Suscripción mensual (SaaS) usando Stripe o MercadoPago para desbloquear el botón de "Optimizar".
