import os
from src.knowledge.kb_generator import generate_kb_from_yaml

if __name__ == "__main__":
    project_root = os.path.dirname(__file__)
    yaml_path = os.path.join(project_root, "config/tables.yaml")
    output_path = os.path.join(project_root, "src/knowledge/knowledge.json")
    generate_kb_from_yaml(yaml_path, output_path)