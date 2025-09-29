from typing import Dict
import ast

from src.agents.base_agent import BaseAgent
from src.core.utils.config_agents_loader import load_agents_config
from src.core.utils.remove_duplicates import remove_duplicates

class FilterCheckAgent(BaseAgent):
    def __init__(self, llm):
        config,_ = load_agents_config()
        agents_config = config["agents"]["filter_check"]
        super().__init__(
            name="filter_check",
            domain=agents_config["domain"],
            template_file=agents_config["template_file"],
            llm=llm
        )
        # Lista de agentes de los que tomaremos la salida
        self.input_from = agents_config.get("input_from", [])

    def run(self, state: Dict) -> Dict:
        self.current_agent.set(self.name)
        print("filter_check_agent State: ", state)
        f = {}
        for agent in self.input_from:
            key = f"{agent}_out"
            if key in state:
                f[key] = state.get(key)

        col_details = remove_duplicates(f, valid_keys=[f"{a}_out" for a in self.input_from])

        response = self.run_chain({
            "columns": str(col_details),
            "query": state['user_query']
        }).replace('```', '')

        try:
            filter_extractor = ast.literal_eval(response)
            state[f"{self.name}_out"] = {
                    'filter_extractor': filter_extractor,
                    'filtered_col': str(col_details)
                }
        except Exception as e:
            self.logger.error(f"[{self.name}] Error parseando salida: {response} | {e}")
            state[f"{self.name}_out"] = {
                    'filter_extractor': [],
                    'filtered_col': str(col_details)
                }
            
        return state
