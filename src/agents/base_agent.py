# src/agents/base_agent.py
from typing import Dict, Optional
from src.core.logging.logger_config import console_logger, EnhancedTokenLogger, current_agent, file_logger
from src.core.utils.template_loader import load_agent_template
from langchain_core.output_parsers import StrOutputParser
import time

class BaseAgent:
    def __init__(self, name: str, domain: str, template_file: Optional[str] = None, llm=None):
        self.name = name
        self.domain = domain
        self.template_file = template_file
        self.llm = llm
        self.token_logger = EnhancedTokenLogger()
        self.current_agent = current_agent
        self.console_logger = console_logger
        self.file_logger = file_logger

    def run_chain(self, input_dict: Dict, chain=None) -> str:
        """
        Ejecuta el chain de LangChain/LangGraph si el agente lo necesita.
        Devuelve un string (la salida del parser).
        """
        if chain is None:
            if not self.template_file:
                raise NotImplementedError(f"{self.name} no tiene template_file definido para el chain.")
            if not self.domain:
                raise NotImplementedError(f"{self.name} no tiene domain definido para el chain.")
            if not self.llm:
                raise NotImplementedError(f"{self.name} no tiene llm definido para el chain.")

            chain = (
                load_agent_template(self.domain, self.template_file)
                | self.llm
                | StrOutputParser()
            )

        self.current_agent.set(self.name)
        start_time = time.time()
        
        output = chain.invoke(input_dict, config={"callbacks": [self.token_logger]})
        
        end_time = time.time()
        elapsed = end_time - start_time

        self.console_logger.info(
            f"\n================ [AGENTE: {self.name}] =================\n"
            f"Tokens: prompt={self.token_logger.prompt_tokens}, "
            f"completion={self.token_logger.completion_tokens}, "
            f"total={self.token_logger.total_tokens}\n"
            f"Output:\n{output}\n"
            f"Tiempo: {elapsed:.2f} s\n"
            f"====================================================\n"
        )
        
        return output

    def run(self, state: Dict) -> Dict:
        """
        Cada agente concreto implementa su lógica modificando el state.
        """
        raise NotImplementedError(f"{self.name} debe implementar el método run(state)")
