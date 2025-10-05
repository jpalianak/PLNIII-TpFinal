from typing import Dict
import pandas as pd
from src.agents.base_agent import BaseAgent
from src.core.utils.config_agents_loader import load_agents_config
from src.core.utils.config_system_loader import load_system_config
from src.notifications.email_notifier import notify_email
from src.notifications.slack_notifier import notify_slack
from src.notifications.telegram_notifier import notify_telegram
from dotenv import load_dotenv
import os
import logging
from guardrails import Guard, OnFailAction
from guardrails.hub import RegexMatch

load_dotenv()

recipient = os.getenv("DEFAULT_RECIPIENT")

class FinalResponseAgent(BaseAgent):
    def __init__(self, llm, engine):
        # Cargar configuración
        config, _ = load_agents_config()
        config_system, _ = load_system_config()
        agents_config = config["agents"]["final_response"]
        agents_system = config_system["system"]
        
        super().__init__(
            name="final_response",
            domain=agents_config["domain"],
            template_file=agents_config["template_file"],
            llm=llm
        )
        self.engine = engine  

        # Configurar canal de notificación
        self.notification_channel = agents_system.get("notification_channel", "none").lower()

        self.channel_tools = {
            "email": notify_email,
            "slack": notify_slack,
            "telegram": notify_telegram
        }

    def _validate_output(self, response: str) -> str:
        """
        Valida y limpia texto de salida del modelo con Guardrails.
        - Rechaza bloques markdown (```) o etiquetas de rol (System/User/Assistant/Usuario/Asistente).
        - Si falla, limpia el texto automáticamente.
        - Devuelve la versión final validada o limpiada.
        """
        output_guard = Guard.for_string(
            validators=[
                RegexMatch(
                    regex=r"^(?![\s\S]*```)(?![\s\S]*(?i)(system:|user:|assistant:|usuario:|asistente:))[\s\S]*$",
                    on_fail=OnFailAction.EXCEPTION,
                ),
            ]
        )

        try:
            validated = output_guard.parse(response)

            # Manejar distintas versiones de Guardrails (v0.6.x)
            if isinstance(validated, str):
                validated_text = validated
            elif hasattr(validated, "output"):
                validated_text = validated.output
            elif hasattr(validated, "validated_output"):
                validated_text = validated.validated_output
            elif hasattr(validated, "raw_output"):
                validated_text = validated.raw_output
            else:
                validated_text = str(validated)

            logging.info("[Guardrails] Respuesta validada correctamente.")
            return validated_text.strip()

        except Exception as e:
            logging.warning(f"[Guardrails] Respuesta inválida. Se limpiará. Error: {e}")

            import re
            # Limpieza manual de texto sospechoso
            cleaned = re.sub(r"```.*?```", " ", response, flags=re.S)  # elimina bloques markdown
            cleaned = re.sub(r"(?i)\b(system:|user:|assistant:|usuario:|asistente:)\b", "", cleaned)
            cleaned = re.sub(r"\s+", " ", cleaned).strip()  # elimina espacios extra

            logging.info("[Guardrails] Texto limpiado automáticamente.")
            return cleaned

    def run(self, state: Dict) -> Dict:
        self.current_agent.set(self.name)

        # Ejecutar la consulta SQL final
        df_result = pd.read_sql(state["query_validation_out"], con=self.engine)
        response = self.run_chain({
            "user_query": state["user_query"],
            "sql_result": df_result,
            "filters": state.get("fuzz_filter_out", "")
        })
        # agregar validacion
        response = self._validate_output(response)
        state[f"{self.name}_out"] = response

        # ---- Notificación según configuración ----
        tool_to_use = self.channel_tools.get(self.notification_channel)
        if tool_to_use and self.notification_channel != "none":
            # Definir destinatario y mensaje

            message = f"Este mensaje fue generado automáticamente por el sistema de agentes AIGE.\n\nAquí está el resultado de tu consulta:\n\n{response}"
            
            # Llamar a la tool
            try:
                result = tool_to_use.invoke(f"{recipient}|{message}")
                print(f"[NOTIFICACIÓN] Canal: {self.notification_channel} -> {result}")
            except Exception as e:
                print(f"[ERROR NOTIFICACIÓN] Canal: {self.notification_channel} -> {e}")

        return state