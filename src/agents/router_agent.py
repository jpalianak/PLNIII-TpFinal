from typing import Dict
import ast

from src.agents.base_agent import BaseAgent
from src.core.utils.config_agents_loader import load_agents_config

class RouterAgent(BaseAgent):
    def __init__(self, llm):
        config,_ = load_agents_config()
        agents_config = config["agents"]["router"]
        super().__init__(
            name="router",
            domain=agents_config["domain"],
            template_file=agents_config["template_file"],
            llm=llm
        )

    def run(self, state: Dict) -> Dict:
        
        response = self.run_chain({"question": state["user_query"]}).replace('```', '')

        try:
            parsed_response = ast.literal_eval(response)
        except Exception as e:
            self.logger.error(f"[{self.name}] Error parseando salida: {response} | {e}")
            parsed_response = []

        state[f'{self.name}_out'] = parsed_response
        
        return state