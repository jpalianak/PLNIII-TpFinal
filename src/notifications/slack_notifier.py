<<<<<<< HEAD
from langchain_core.tools import tool
from slack_sdk import WebClient
from dotenv import load_dotenv
import os

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")  # ej: "C89ABCDE0"

client = WebClient(token=SLACK_BOT_TOKEN)

@tool
def notify_slack(input_str: str) -> str:
    """
    Envía un mensaje a Slack. 
    input_str debe tener el formato 'canal|mensaje'.
    """
    try:
        channel, message = input_str.split("|", 1)
        # si querés siempre usar el canal por default, podés ignorar 'channel'
        client.chat_postMessage(channel=SLACK_CHANNEL_ID, text=message)
        return f"Mensaje enviado al canal {SLACK_CHANNEL_ID}"
    except Exception as e:
=======
from langchain_core.tools import tool
from slack_sdk import WebClient
from dotenv import load_dotenv
import os

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")  # ej: "C89ABCDE0"

client = WebClient(token=SLACK_BOT_TOKEN)

@tool
def notify_slack(input_str: str) -> str:
    """
    Envía un mensaje a Slack. 
    input_str debe tener el formato 'canal|mensaje'.
    """
    try:
        channel, message = input_str.split("|", 1)
        # si querés siempre usar el canal por default, podés ignorar 'channel'
        client.chat_postMessage(channel=SLACK_CHANNEL_ID, text=message)
        return f"Mensaje enviado al canal {SLACK_CHANNEL_ID}"
    except Exception as e:
>>>>>>> d66169c081f129a63f3e88518ef7186fbd60c3c4
        return f"Error al enviar mensaje: {e}"