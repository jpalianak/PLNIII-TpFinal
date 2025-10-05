import telebot
import threading

class TelegramChannel:
    def __init__(self, token, chat_id, graph):
        self.bot = telebot.TeleBot(token)
        self.chat_id = chat_id
        self.graph = graph

    def start(self):
        """Inicia el bot en un hilo separado (no bloquea el main)."""
        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message):
            user_query = message.text
            print(f"[Telegram] Consulta recibida: {user_query}")

            try:
                result = self.graph.invoke({"user_query": user_query})
                response = result.get("final_response_out", "No se obtuvo respuesta del agente.")
            except Exception as e:
                response = f"Error procesando la consulta: {e}"

            self.bot.send_message(message.chat.id, response)

        thread = threading.Thread(target=self.bot.infinity_polling, daemon=True)
        thread.start()

    def send_message(self, text):
        """Permite enviar mensajes salientes (notificaciones automáticas)."""
        self.bot.send_message(self.chat_id, text)
