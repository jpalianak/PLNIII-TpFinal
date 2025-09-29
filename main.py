from src.workflows.build_graph import build_main_graph

if __name__ == "__main__":
    graph = build_main_graph()
    state = graph.invoke({"user_query": "me das el top 5 de los clientes con mayores valor de $ en pedidos?"})
    print("Respuesta final del agente:", state["final_response_out"])