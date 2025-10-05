# pip install pyTelegramBotAPI --upgrade
import os
import telebot
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN:
    raise ValueError("Falta TELEGRAM_BOT_TOKEN en .env")
if not CHAT_ID:
    raise ValueError("Falta TELEGRAM_CHAT_ID en .env")

bot = telebot.TeleBot(TOKEN)

@tool
def notify_telegram(message: str):
    """Enviar mensaje directo al chat_id definido"""
    try:
        bot.send_message(CHAT_ID, message)
        return f"Enviado a {CHAT_ID}"
    except Exception as e:
        return f"Error: {e}"

