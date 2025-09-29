from typing import Dict
from src.agents.base_agent import BaseAgent
from src.core.utils.fuzzy_wuzzy import call_match

class FuzzFilterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="fuzz_filter",
            domain=None,          
            template_file=None,
            llm=None
        )
        
    def run(self, state: Dict) -> Dict:
        self.current_agent.set(self.name)
        try:
            response = call_match(state.get("filter_check_out", []))
        except Exception as e:
            response = []

        state[f'{self.name}_out'] = response

        return state