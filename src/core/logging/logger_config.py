# src/core/logging/logger_config.py

import logging
import contextvars
from langchain_core.callbacks import BaseCallbackHandler
import os
import time
import queue

current_agent = contextvars.ContextVar("current_agent", default="")

# Crear carpeta logs si no existe
os.makedirs("logs", exist_ok=True)

# Logger consola
console_logger = logging.getLogger("aige_console")
console_logger.setLevel(logging.INFO)
if not console_logger.handlers:
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    console_logger.addHandler(console_handler)

# Logger archivo
file_logger = logging.getLogger("aige_file")
file_logger.setLevel(logging.INFO)
if not file_logger.handlers:
    file_handler = logging.FileHandler("logs/aige.log", encoding="utf-8")
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    file_logger.addHandler(file_handler)

class EnhancedTokenLogger(BaseCallbackHandler):
    """Callback que registra tokens, tiempo y tamaño de input/output en el log de archivo."""

    def __init__(self, accumulate=True):
        super().__init__()
        self.accumulate = accumulate  # Si True, acumula tokens en múltiples llamadas
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.start_time = None
        self.input_chars = 0
        self.output_chars = 0

    def on_llm_start(self, serialized, prompts, **kwargs):
        """Se llama antes de enviar el prompt al LLM."""
        self.start_time = time.time()
        # medir longitud del prompt enviado
        prompt_len = 0
        if isinstance(prompts, list):
            prompt_len = sum(len(p) for p in prompts)
        elif isinstance(prompts, str):
            prompt_len = len(prompts)
        if self.accumulate:
            self.input_chars += prompt_len
        else:
            self.input_chars = prompt_len

    def on_llm_end(self, response, **kwargs):
        """Se llama al recibir la respuesta del LLM."""
        usage = response.llm_output.get("token_usage", {})
        if self.accumulate:
            self.prompt_tokens += usage.get("prompt_tokens", 0)
            self.completion_tokens += usage.get("completion_tokens", 0)
            self.total_tokens += usage.get("total_tokens", 0)
        else:
            self.prompt_tokens = usage.get("prompt_tokens", 0)
            self.completion_tokens = usage.get("completion_tokens", 0)
            self.total_tokens = usage.get("total_tokens", 0)

        # medir longitud de la respuesta
        output_len = 0
        if hasattr(response, "generations") and response.generations:
            outputs = [gen[0].text for gen in response.generations if gen]
            output_len = sum(len(o) for o in outputs)
        if self.accumulate:
            self.output_chars += output_len
        else:
            self.output_chars = output_len

        elapsed = time.time() - self.start_time if self.start_time else 0
        agent_name = current_agent.get()
        file_logger.info(
            f"tokens - [{agent_name}] prompt={self.prompt_tokens}, "
            f"completion={self.completion_tokens}, total={self.total_tokens} | "
            f"elapsed={elapsed:.2f}s | in_chars={self.input_chars}, out_chars={self.output_chars}"
        )
            
# ------------------ Cola de logs para Streamlit ------------------
log_queue = queue.Queue()

class StreamlitQueueHandler(logging.Handler):
    """Handler que envía logs a una cola para Streamlit."""
    def emit(self, record):
        try:
            msg = self.format(record)
            log_queue.put(msg)
        except Exception:
            pass  # nunca queremos que falle el logging

# Creamos el handler para Streamlit y lo agregamos a los loggers existentes
streamlit_handler = StreamlitQueueHandler()
streamlit_handler.setFormatter(logging.Formatter("%(message)s"))
console_logger.addHandler(streamlit_handler)