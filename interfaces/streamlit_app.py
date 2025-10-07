import re
import time
import streamlit as st
from src.workflows.build_graph import build_main_graph
from src.core.logging.logger_config import log_queue
from src.core.guardrails.input_guard import InputGuard

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
        logs_placeholder.text_area(
            "Logs de agentes",
            value="",
            height=585,
            key="logs_text_area",
            disabled=True
        )

    status_placeholder = st.empty()
    
    if run_button and user_query.strip():
        input_guard = InputGuard()
        validated_input = input_guard.validate(user_query)
        status_placeholder.info("⏳ Procesando...")
        all_logs = []

        # Expresiones regulares para parsear tokens
        prompt_pattern = re.compile(r"prompt=(\d+)")
        completion_pattern = re.compile(r"completion=(\d+)")
        total_pattern = re.compile(r"total=(\d+)")

        # Variables acumuladas
        prompt_total = 0
        completion_total = 0
        total_tokens = 0

        start_time = time.time()

        for chunk in graph.stream({"user_query": validated_input}):

            while not log_queue.empty():
                msg = log_queue.get()
                all_logs.append(msg)

                # --- Parsear tokens ---
                m_prompt = prompt_pattern.search(msg)
                m_completion = completion_pattern.search(msg)
                m_total = total_pattern.search(msg)

                if m_prompt:
                    prompt_total += int(m_prompt.group(1))
                if m_completion:
                    completion_total += int(m_completion.group(1))
                if m_total:
                    total_tokens += int(m_total.group(1))

                logs_placeholder.text_area(
                    "Logs de agentes",
                    value="\n\n".join(all_logs),
                    height=580,
                    disabled=False
                )

            # Mostrar respuesta final
            final_resp = None
            if isinstance(chunk, dict):
                if "final_response_out" in chunk and chunk["final_response_out"] is not None:
                    final_resp = chunk["final_response_out"]
                else:
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

        # Tiempo real total
        elapsed_total = time.time() - start_time

        status_placeholder.success(
            f"✅ Consulta completada en {elapsed_total:.2f}s | "
            f"Prompt tokens: {prompt_total}, Completion tokens: {completion_total}, Total tokens: {total_tokens}"
        )

if __name__ == "__main__":
    run_app()
