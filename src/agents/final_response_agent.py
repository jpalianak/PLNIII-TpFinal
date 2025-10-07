from typing import Dict
import pandas as pd
from src.agents.base_agent import BaseAgent
from src.core.utils.config_agents_loader import load_agents_config
from src.core.utils.config_system_loader import load_system_config
from src.notifications.email_notifier import notify_email
from src.notifications.slack_notifier import notify_slack
from src.notifications.telegram_notifier import notify_telegram
from src.core.guardrails.output_guard import OutputGuard
from dotenv import load_dotenv
import os
import logging

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

        self.output_guard = OutputGuard()
        
        self.notification_channel = agents_system.get("notification_channel", "none").lower()

        self.channel_tools = {
            "email": notify_email,
            "slack": notify_slack,
            "telegram": notify_telegram,
            "none": None
        }

    def run(self, state: Dict) -> Dict:
        self.current_agent.set(self.name)

        # Ejecutar la consulta SQL final
        df_result = pd.read_sql(state["query_validation_out"], con=self.engine)
        response = self.run_chain({
            "user_query": state["user_query"],
            "sql_result": df_result,
            "filters": state.get("fuzz_filter_out", "")
        })
        
        response = self.output_guard.validate(response)
        
        state[f"{self.name}_out"] = response

        # --- Detectar canales mencionados por el usuario ---
        user_query_lower = state["user_query"].lower()
        user_channels = [c for c in ["email", "slack", "telegram"] if c in user_query_lower]

        # --- Agregar canal por defecto del sistema ---
        channels_to_use = set(user_channels)
        if self.notification_channel != "none":
            channels_to_use.add(self.notification_channel)

        message = (
            f"Este mensaje fue generado automáticamente por el sistema de agentes AIGE.\n\n"
            f"Aquí está el resultado de tu consulta:\n\n{response}"
        )

        # --- Enviar notificación a todos los canales detectados ---
        for channel in channels_to_use:
            tool_to_use = self.channel_tools.get(channel)
            if tool_to_use is not None:
                try:
                    result = tool_to_use.invoke(f"{recipient}|{message}")
                    print(f"[NOTIFICACIÓN] Canal: {channel} -> {result}")
                except Exception as e:
                    print(f"[ERROR NOTIFICACIÓN] Canal: {channel} -> {e}")

        return state