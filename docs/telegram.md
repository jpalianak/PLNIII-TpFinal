# Telegram Notifier – Guía rápida

Este proyecto permite enviar notificaciones a un chat de Telegram usando un **bot** creado con [BotFather](https://t.me/botfather).

---

## 1. Crear un bot en Telegram
1. Abre Telegram y busca **@BotFather**.
2. Ejecuta el comando:
   ```text
   /newbot
   ```
3. Asigna un nombre y un **username** (debe terminar en `bot`, por ejemplo: `MiNotifierBot`).
4. BotFather te dará un **token de acceso** similar a:
   ```text
   8303590848:AAHiILI3pacwMv5w
   ```.

---

## 2. Iniciar un chat con tu bot
1. BotFather te dará un enlace como:
   ```
   https://t.me/TuBotUsername
   ```
2. Haz clic en el enlace y envía un mensaje al bot (ejemplo: `/start`).

---

## 3. Obtener tu `chat_id`
1. Abre en tu navegador esta URL, reemplazando `TOKEN` por el que te dio BotFather:
   ```
   https://api.telegram.org/botTOKEN/getUpdates
   ```
   Ejemplo:
   ```
   https://api.telegram.org/bot8303590848:AAHiILI3pacwMv5w/getUpdates
   ```

2. Verás un JSON con información de tu chat. Busca el bloque:
   ```json
   "chat": {
       "id": 1463242335,
       "first_name": "Jonathan",
       "last_name": "Cagua",
       "type": "private"
   }
   ```
   El valor de `"id"` (`1463242335` en este caso) es tu **CHAT_ID**.

---

## 4. Configurar variables en `.env`
Agregar en el `.env` :

```env
TELEGRAM_BOT_TOKEN=8303590848:AAHiILI3pacwMv5w
TELEGRAM_CHAT_ID=1463242335
```