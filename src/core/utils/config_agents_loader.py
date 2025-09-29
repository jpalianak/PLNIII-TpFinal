import os
import yaml

def load_agents_config():
    """
    Carga la configuración de agents.yaml
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    config_path = os.path.join(base_dir, "config", "agents.yaml")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config, base_dir