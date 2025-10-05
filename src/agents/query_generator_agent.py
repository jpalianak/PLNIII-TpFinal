# src/agents/query_generation_agent.py
from typing import Dict
from src.agents.base_agent import BaseAgent
from src.core.utils.config_agents_loader import load_agents_config
from src.core.utils.engine_loader import get_db_engine

class QueryGenerationAgent(BaseAgent):
    def __init__(self, llm):
        config,_ = load_agents_config()
        agents_config = config["agents"]["query_generation"]
        _,engine_type = get_db_engine()
        super().__init__(
            name="query_generation",
            domain=agents_config["domain"],
            template_file=agents_config["template_file"],
            llm=llm
        )
        self.engine_type = engine_type

    def run(self, state: Dict) -> Dict:
        self.current_agent.set(self.name)

        response = self.run_chain({
            "query": state.get("user_query", ""),
            "columns": state.get("filter_check_out", {}).get("filtered_col", []),
            "filters": state.get("fuzz_filter_out", ''),
            "engine_type": self.engine_type
        }).replace("```", "")

        state[f'{self.name}_out'] = response

        return state