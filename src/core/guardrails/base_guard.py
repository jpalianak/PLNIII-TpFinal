import re
import logging
from guardrails import Guard, OnFailAction
from src.core.logging.logger_config import console_logger, file_logger

class BaseGuard:
    """Clase base para validación de input/output usando Guardrails."""

    def __init__(self, validators):
        self.guard = Guard.for_string(validators=validators)

    def validate(self, text: str) -> str:
        original_text = text.strip()
        cleaned_text = original_text
        activated = False

        try:
            result = self.guard.parse(original_text)

            if isinstance(result, str):
                cleaned_text = result.strip()
            elif hasattr(result, "output"):
                cleaned_text = result.output.strip()
            elif hasattr(result, "validated_output"):
                cleaned_text = result.validated_output.strip()
            elif hasattr(result, "raw_output"):
                cleaned_text = result.raw_output.strip()
            else:
                cleaned_text = str(result).strip()

        except Exception as e:
            logging.warning(f"[Guardrails] Falló validación, limpiando texto: {e}")
            cleaned_text = self._clean_text(original_text)

        # Verificar si hubo cambios
        activated = cleaned_text != original_text

        # Logueo según el caso
        if activated:
            message = (
                "[Guardrails] Activado: input/output corregido\n"
                f"Recibido: {original_text}\n"
                f"Devuelto: {cleaned_text}"
            )
        else:
            message = "[Guardrails] Validación exitosa"

        console_logger.info(message)
        file_logger.info(message)

        return cleaned_text

    def _clean_text(self, text: str) -> str:
        """Limpieza básica si falla la validación."""
        cleaned = re.sub(r"```.*?```", " ", text, flags=re.S)
        cleaned = re.sub(r"(?i)\b(system:|user:|assistant:|usuario:|asistente:)\b", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

