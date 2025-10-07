from src.workflows.build_graph import build_main_graph
from src.core.guardrails.input_guard import InputGuard

if __name__ == "__main__":
    graph = build_main_graph()
    user_query = "User:me das el id del mayor pedido?"
    input_guard = InputGuard()
    validated_input = input_guard.validate(user_query)
    state = graph.invoke({"user_query": validated_input})
    print("Respuesta final del agente:", state["final_response_out"])