from src.workflows.build_graph import build_main_graph

if __name__ == "__main__":
    graph = build_main_graph()
    state = graph.invoke({"user_query": "me das el id del mayor pedido?. Quiero ennviar la respuesta por telegram, email y slack"})
    print("Respuesta final del agente:", state["final_response_out"])