# src/agents/final_response_agent.py
from typing import Dict
import pandas as pd
from src.agents.base_agent import BaseAgent
from src.core.utils.config_agents_loader import load_agents_config

class FinalResponseAgent(BaseAgent):
    def __init__(self, llm, engine):
        config,_ = load_agents_config()
        agents_config = config["agents"]["final_response"]
        super().__init__(
            name="final_response",
            domain=agents_config["domain"],
            template_file=agents_config["template_file"],
            llm=llm
        )
        self.engine = engine  

    def run(self, state: Dict) -> Dict:
        self.current_agent.set(self.name)
        df_result = pd.read_sql(state["query_validation_out"], con=self.engine)

        response = self.run_chain({
            "user_query": state["user_query"],
            "sql_result": df_result,
            "filters": state.get("fuzz_filter_out", "")
        })

        state[f"{self.name}_out"] = response

        return state