import os
import sys
import yaml
import time
import json
import tqdm
import pandas as pd
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableMap

from src.core.utils.engine_loader import get_db_engine
from src.core.utils.llm_loader import get_llm
from src.core.utils.template_loader import load_agent_template


load_dotenv()

engine, engine_type = get_db_engine()

template = load_agent_template("general", "knowledge")

model = get_llm()

chain = (
    RunnableMap({
        "description": lambda x: x["description"],
        "data_sample": lambda x: x["data_sample"]
    })
    | template
    | model
    | StrOutputParser()
)

def read_sql(table, engine, columns=None, n_samples=5):
    """
    Lee n_samples filas de una tabla, usando alias según el mapping lógico.
    
    Parámetros:
        table (str): nombre lógico de la tabla
        engine (sqlalchemy.Engine): engine de SQLAlchemy
        columns (dict[str,str] | None): mapping {col_fisico: col_logico}, si None trae todas
        n_samples (int): cantidad de filas a obtener
    
    Retorna:
        pd.DataFrame con las filas seleccionadas (columnas lógicas)
    """
    if columns:
        # Usamos directamente los nombres lógicos como columnas
        cols_str = ", ".join(columns.values())
    else:
        cols_str = "*"

    # Generar query según el motor
    if engine_type == "mssql":
        query = f"SELECT TOP {n_samples} {cols_str} FROM {table} ORDER BY NEWID();"
    elif engine_type == "sqlite":
        query = f"SELECT {cols_str} FROM {table} ORDER BY RANDOM() LIMIT {n_samples};"
    elif engine_type in ["postgresql", "mysql", "mariadb"]:
        query = f"SELECT {cols_str} FROM {table} ORDER BY RANDOM() LIMIT {n_samples};"
    elif engine_type == "oracle":
        query = f"""
        SELECT {cols_str} 
        FROM {table} 
        WHERE ROWNUM <= {n_samples}
        ORDER BY DBMS_RANDOM.VALUE
        """
    else:
        query = f"SELECT {cols_str} FROM {table} LIMIT {n_samples};"

    return pd.read_sql(query, con=engine)


def generate_kb_from_yaml(yaml_path, output_path):
    with open(yaml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    kb = {}
    
    for _, cfg in tqdm.tqdm(config["tables"].items()):
        # Usar el logical_name como nombre real de la tabla
        logical_name = cfg.get("logical_name")
        desc = cfg["description"]
        cols = cfg.get("columns", None)

        # Ahora los nombres de columnas en la DB ya son lógicos,
        # así que solo pasamos el dict.values()
        df = read_sql(logical_name, engine, columns=cols)
        df_dict = str(df.to_dict())
        
        response = chain.invoke({"description": desc, "data_sample": df_dict}).replace("```", "")
        kb[logical_name] = eval(response)  
        time.sleep(5)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)

    print(f"Base de conocimiento guardada en {output_path}")
    print("\nBase de conocimiento generada:\n")
    for table, data in kb.items():
        print(f"{table}:\n{data}\n")
