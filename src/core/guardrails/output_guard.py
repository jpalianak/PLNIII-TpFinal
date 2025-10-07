from guardrails.hub import RegexMatch
from guardrails import OnFailAction
from src.core.guardrails.base_guard import BaseGuard

class OutputGuard(BaseGuard):
    """Valida la salida del modelo: sin markdown ni etiquetas de rol."""

    def __init__(self):
        validators = [
            RegexMatch(
                regex=r"(?i)^(?![\s\S]*```)(?![\s\S]*(system:|user:|assistant:|usuario:|asistente))[\s\S]*$",
                on_fail=OnFailAction.EXCEPTION,
            )
        ]
        super().__init__(validators)
