from src.workflows.build_graph import build_main_graph
from src.notifications.telegram_notifier_bi import TelegramChannel
from dotenv import load_dotenv
import os
import time

load_dotenv() 

def main():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = int(os.getenv("TELEGRAM_CHAT_ID"))

    graph = build_main_graph()

    print("Modo Telegram activado — escuchando consultas del usuario...")
    telegram_channel = TelegramChannel(bot_token, chat_id, graph)
    telegram_channel.start()

    # Mantener el proceso vivo
    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()