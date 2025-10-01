from calendar import c
import json
import re
import sys
import os
import ast
import yaml

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from operator import add
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableMap
from src.core.utils.llm_loader import get_llm
from src.core.utils.template_loader import load_agent_template
from src.core.utils.load_specific_agent_instructions import load_agent_instructions

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.core.logging.logger_config import console_logger, file_logger, current_agent, EnhancedTokenLogger
from src.core.utils.config_system_loader import load_system_config

#default_token_logger = EnhancedTokenLogger()

config, base_dir = load_system_config()

kb_path = os.path.join(base_dir, config["knowledge_base"]["path"])
with open(kb_path, 'rb') as f:
    loaded_dict = json.load(f)
    
class overallstate(TypedDict):
    user_query: str
    table_lst: list[str]
    table_extract : Annotated[list[str], add]
    column_extract : Annotated[list[str], add]
    agent_domain: str
    agent_template: str

def sq_node(state: overallstate, callbacks=None):
    q = state['user_query']
    lst = state['table_lst']
    agent_domain = state.get('agent_domain')
    agent_template = state.get('agent_template')

    o = solve_subquestion(q, lst, agent_domain, agent_template, callbacks=callbacks)
    try:
        table_extract = ast.literal_eval(o)
    except Exception as e:
        file_logger.error(f"{current_agent.get()} Error parseando salida: {o} | {e}")
        table_extract = []
    return {"table_extract": table_extract}

def solve_subquestion(q, lst,agent_domain, agent_template,callbacks=None):
    ''' Resuelve las subpreguntas para cada tabla seleccionada '''
    final = []
    for tab in lst:
        table_info = loaded_dict[tab]
        desc = table_info["table_description"]
        final.append([tab, desc])
    result_dict = {item[0]: item[1] for item in final}
    subquestion = agent_subquestion(q, str(result_dict),agent_domain, agent_template, callbacks=callbacks)
    return subquestion


def agent_subquestion(q, v, agent_domain, agent_template, callbacks=None):

    token = current_agent.set(f"{current_agent.get()}[subquestion]")

    specific_prompt = load_agent_instructions(agent_domain, agent_template)

    chain = (
        RunnableMap({
            "tables": lambda x: x["tables"],
            "user_query": lambda x: x["user_query"],
            "agent_instructions": lambda x: x["agent_instructions"]
        })
        | load_agent_template("general", "subquestion")
        | get_llm()
        | StrOutputParser()
    )

    response = chain.invoke({"tables": v, "user_query": q, "agent_instructions": specific_prompt},config={"callbacks": callbacks}).replace("", "")
    
    match = re.search(r"\[\s*\[.*?\]\s*(,\s*\[.*?\]\s*)*\]", response, re.DOTALL)
    result = match.group(0) if match else None

    current_agent.reset(token)
           
    return result

def column_node(state: overallstate, callbacks=None):

    subq = state['table_extract']
    mq = state['user_query']
    o = solve_column_selection(mq, subq,callbacks=callbacks)
    result = {"column_extract": o}

    return result

def solve_column_selection(main_q, list_sub,callbacks=None):

    final_col = []
    inter = []
    for tab in list_sub:
        if len(tab)==0:
            continue
        table_name = tab[-1]
        question = tab[:-1]
        columns = loaded_dict[table_name]["columns"]
        out_column = agent_column_selection(main_q, question, str(columns),callbacks=callbacks)
        trans_col = eval(out_column)
        for col_selec in trans_col:
            new_col = ["name of table:" + table_name] + col_selec
            inter.append(new_col)
        final_col.extend(inter)

    return final_col

def agent_column_selection(mq, q,c,callbacks=None):

    token = current_agent.set(f"{current_agent.get()}[column_selection]")

    chain = (
        RunnableMap({
            "columns": lambda x: x["columns"],
            "query": lambda x: x["query"],
            "main_question": lambda x: x["main_question"]
        })
        | load_agent_template("general", "column_extractor")
        | get_llm()
        | StrOutputParser()
    )
    
    response = chain.invoke({"columns": c, "query": q, "main_question": mq},config={"callbacks": callbacks}).replace("", "")
        
    match = re.search(r"\[\s*\[.*?\]\s*(,\s*\[.*?\]\s*)*\]", response, re.DOTALL)
    if match:
        result = match.group(0)
    else:
        result = '[[]]'
        
    current_agent.reset(token)
                           
    return result


builder_final = StateGraph(overallstate)
builder_final.add_node("sq_node", sq_node)
builder_final.add_node("column_node", column_node)

builder_final.add_edge(START, "sq_node")
builder_final.add_edge("sq_node", "column_node")

builder_final.add_edge("column_node", END)
graph_final = builder_final.compile()
