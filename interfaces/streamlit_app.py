import streamlit as st
from src.workflows.build_graph import build_main_graph
from src.core.logging.logger_config import log_queue 

graph = build_main_graph()

def _pretty(obj):
    """Pretty-print dicts / lists a string."""
    try:
        import json
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except Exception:
        return str(obj)

def run_app():
    st.set_page_config(layout="wide")
    st.title("Sistema Multiagentes - Interfaz de Consulta")

    col_left, col_right = st.columns([1, 1])

    # -------- Columna izquierda: Input + Resultado --------
    with col_left:
        user_query = st.text_area("Ingrese su consulta:", height=150, key="user_query")
        run_button = st.button("Ejecutar consulta", key="run_button")
        st.markdown("<br><br>", unsafe_allow_html=True)
        result_placeholder = st.empty()
        # Creamos el placeholder de resultado final UNA sola vez
        result_placeholder.text_area(
            "Respuesta final",
            value="",
            height=300,
            key="result_text_area",
            disabled=True
        )

    # -------- Columna derecha: Logs --------
    with col_right:
        logs_placeholder = st.empty()
        # Creamos el placeholder de logs UNA sola vez
        logs_placeholder.text_area(
            "Logs de agentes",
            value="",
            height=585,
            key="logs_text_area",
            disabled=True
        )

    status_placeholder = st.empty()
    
    # -------- Ejecutar grafo --------
    if run_button and user_query.strip():
        status_placeholder.info("⏳ Procesando...")
        all_logs = []

        for chunk in graph.stream({"user_query": user_query}):

            while not log_queue.empty():
                msg = log_queue.get()
                all_logs.append(msg)

                logs_placeholder.text_area(
                    "Logs de agentes",
                    value="\n\n".join(all_logs),
                    height=580,
                    disabled=False
                )

            final_resp = None
            if isinstance(chunk, dict):
                # Chequeamos si existe 'final_response_out' directamente
                if "final_response_out" in chunk and chunk["final_response_out"] is not None:
                    final_resp = chunk["final_response_out"]
                else:
                    # También dentro de agentes del chunk
                    for agent_data in chunk.values():
                        if isinstance(agent_data, dict) and "final_response_out" in agent_data:
                            final_resp = agent_data["final_response_out"]
                            break

            if final_resp is not None:
                result_placeholder.text_area(
                    "Respuesta final",
                    value=final_resp,
                    height=300,
                    disabled=False
                )

        status_placeholder.success("✅ Consulta completada")

if __name__ == "__main__":
    run_app()

