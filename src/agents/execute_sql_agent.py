import re
from typing import Dict
import pandas as pd
from src.agents.base_agent import BaseAgent

class ExecuteSQLAgent(BaseAgent):
    def __init__(self, engine):
        super().__init__(
            name="execute_sql",
            domain=None,        
            template_file=None, 
            llm=None
        )
        self.engine = engine

    def run(self, state: Dict) -> Dict:
        self.current_agent.set(self.name)
        query = state.get("query_validation_out")
        
        if not query:
            self.file_logger.error(f"[{self.name}] No se encontró 'final_query' en el state.")
            state[f"{self.name}_out"] = None
        else:
            try:
                result = pd.read_sql(query, con=self.engine)
                state[f"{self.name}_out"] = result
            except Exception as e:
                self.file_logger.error(f"[{self.name}] Error ejecutando query: {query} | {e}")
                state[f"{self.name}_out"] = None

        return state