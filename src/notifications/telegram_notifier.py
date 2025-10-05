from langchain_core.tools import tool

@tool
def notify_telegram(message: str) -> str:
    """Envía un mensaje de Telegram con la respuesta final al chat indicado."""
    print(f"[TELEGRAM] -> {message}")
    return "Telegram enviado"