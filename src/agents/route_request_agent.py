# src/agents/route_request_agent.py
from typing import Dict
from src.agents.base_agent import BaseAgent

class RouteRequestAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="route_request",
            domain=None,          
            template_file=None,
            llm=None
        )

    def run(self, state: Dict) -> Dict:
        self.current_agent.set(self.name)
        routes = state.get("router_out", [])

        state[f'{self.name}_out'] = routes

        return state