# src/agents/query_validation_agent.py
from typing import Dict
from src.agents.base_agent import BaseAgent
from src.core.utils.config_agents_loader import load_agents_config

class QueryValidationAgent(BaseAgent):
    def __init__(self, llm, engine_type):
        config,_ = load_agents_config()
        agents_config = config["agents"]["query_validation"]
        super().__init__(
            name="query_validation",
            domain=agents_config["domain"],
            template_file=agents_config["template_file"],
            llm=llm
        )
        self.engine_type = engine_type
        
    def run(self, state: Dict) -> Dict:
        self.current_agent.set(self.name)
        response = self.run_chain({
            "columns": state.get("filter_check_out", {}).get("filtered_col", []),
            "query": state.get("user_query", ""),
            "filters": state.get("fuzz_filter_out", ""),
            "sql_query": state.get("query_generation_out", ""),
            "engine_type": self.engine_type,
        }).replace("```", "")

        state[f'{self.name}_out'] = response

        return state
