from typing import Dict
from src.agents.base_agent import BaseAgent
from src.agents.column_extract_agent import graph_final
from src.core.utils.config_agents_loader import load_agents_config
from src.core.logging.logger_config import EnhancedTokenLogger


class ProductAgent(BaseAgent):
    def __init__(self, llm):
        config,_ = load_agents_config()
        agents_config = config["agents"]["product"]
        super().__init__(
            name="product",
            domain=agents_config["domain"],
            template_file=agents_config["template_file"],
            llm=llm
        )
        self.table_list = agents_config["table_list"]

    def run(self, state: Dict) -> Dict:
        
        self.current_agent.set(self.name)

        response = self.run_chain(
            {"user_query": state["user_query"], "table_lst": self.table_list, "agent_domain": self.domain, "agent_template": self.template_file},
            chain=graph_final.with_config({"callbacks": [self.token_logger]})
        )
        
        return {f'{self.name}_out': response}