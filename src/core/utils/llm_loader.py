import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm():
    """
    Devuelve una instancia configurada del modelo de lenguaje de OpenAI.
    Lanza una excepción si no se encuentra la clave.
    """
    return ChatOpenAI(model="gpt-5-nano")#temperature=0, 
