from calendar import c
from typing import Dict
from src.agents.base_agent import BaseAgent

class FilterConditionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="filter_condition",
            domain=None,          
            template_file=None,
            llm=None
        )

    def run(self, state: Dict) -> Dict:
        self.current_agent.set(self.name)
        filter_extractor = state.get("filter_check_out", {}).get("filter_extractor", [])
        cond = "no" if len(filter_extractor) <= 1 else "yes"

        state[f"{self.name}_out"] = cond

        return state