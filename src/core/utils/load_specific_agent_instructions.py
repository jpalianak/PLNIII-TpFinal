import os
import yaml

def load_agent_instructions(agent_domain, agent_template, base_path="templates"):
    path = os.path.join(base_path, agent_domain, f"{agent_template}.yaml")
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("instructions", "")