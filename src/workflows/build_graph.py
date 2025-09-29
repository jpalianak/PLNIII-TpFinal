from langgraph.graph import StateGraph, START, END
from langgraph.graph import StateGraph
from src.agents.router_agent import RouterAgent
from src.agents.route_request_agent import RouteRequestAgent
from src.agents.customer_agent import CustomerAgent
from src.agents.order_agent import OrdersAgent
from src.agents.product_agent import ProductAgent
from src.agents.filter_check_agent import FilterCheckAgent
from src.agents.filter_condition_agent import FilterConditionAgent
from src.agents.fuzz_filter_agent import FuzzFilterAgent
from src.agents.query_generator_agent import QueryGenerationAgent
from src.agents.query_validation_agent import QueryValidationAgent
from src.agents.execute_sql_agent import ExecuteSQLAgent
from src.agents.final_response_agent import FinalResponseAgent
from src.core.utils.engine_loader import get_db_engine
from src.core.utils.llm_loader import get_llm
from typing import TypedDict

engine, engine_type = get_db_engine()
llm_agent = get_llm()

def build_main_graph():
    """
    Construye y devuelve el grafo de agentes.
    """
    
    class finalstate(TypedDict):
        user_query: str
        router_out: list[str]
        customer_out: str
        order_out: str
        product_out: str
        filter_check_out: str
        filter_condition_out: str
        fuzz_filter_out: str
        query_generation_out: str
        query_validation_out: str
        execute_sql_out: str
        final_response_out: str

    workflow = StateGraph(finalstate)

    # === Definir nodos (agentes) ===
    workflow.add_node("router", RouterAgent(llm=llm_agent).run)
    workflow.add_node("route_request", RouteRequestAgent().run)
    workflow.add_node("customer", CustomerAgent(llm=llm_agent).run)
    workflow.add_node("orders", OrdersAgent(llm=llm_agent).run)
    workflow.add_node("product", ProductAgent(llm=llm_agent).run)
    workflow.add_node("filter_check", FilterCheckAgent(llm=llm_agent).run)
    workflow.add_node("filter_condition", FilterConditionAgent().run)
    workflow.add_node("fuzz_filter", FuzzFilterAgent().run)
    workflow.add_node("query_generator", QueryGenerationAgent(llm=llm_agent).run)
    workflow.add_node("query_validation", QueryValidationAgent(llm=llm_agent, engine_type=engine_type).run)
    workflow.add_node("execute_sql", ExecuteSQLAgent(engine=engine).run)
    workflow.add_node("final_response", FinalResponseAgent(llm=llm_agent,engine=engine).run)

    def route_condition(state: dict) -> str:
        return state["route_request_out"]
    
    def filter_condition_branch(state: dict) -> str:
        return state["filter_condition_out"] 
    
    # === Definir edges ===
    workflow.add_edge(START, "router")
    workflow.add_edge("router", "route_request")
    workflow.add_conditional_edges("route_request",route_condition,{"customer": "customer","orders": "orders","product": "product"})
    workflow.add_edge("customer", "filter_check")
    workflow.add_edge("orders", "filter_check")
    workflow.add_edge("product", "filter_check")
    workflow.add_edge("filter_check", "filter_condition")
    workflow.add_conditional_edges("filter_condition",filter_condition_branch,{"yes": "fuzz_filter","no": "query_generator"})
    workflow.add_edge("fuzz_filter", "query_generator")
    workflow.add_edge("query_generator", "query_validation")
    workflow.add_edge("query_validation", "execute_sql")
    workflow.add_edge("execute_sql", "final_response")
    workflow.add_edge("final_response", END)
    
    return workflow.compile()
