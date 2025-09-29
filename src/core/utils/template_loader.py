import yaml
from langchain.prompts import ChatPromptTemplate

def load_agent_template(agent_name, template_name, base_path="templates"):
    """
    Carga un template YAML de un agente específico y devuelve un ChatPromptTemplate.
    """
    path = f"{base_path}/{agent_name}/{template_name}.yaml"
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    return ChatPromptTemplate.from_messages([
        ("system", data["system"]),
        ("human", data["human"])
    ])
