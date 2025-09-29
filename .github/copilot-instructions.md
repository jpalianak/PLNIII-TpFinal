# Copilot Instructions for AIGE (Asistente Inteligente para Gestión Empresarial)

## Project Overview
- **AIGE** is a modular, agent-based platform for business management, integrating LLMs, specialized agents, and orchestration via LangGraph.
- Agents interact with real ERP data (Totvs, SAP, Oracle, etc.), answer queries, monitor conditions, and propose actions in natural language.
- The architecture is designed for extensibility: new agents, tools, and connectors can be added with minimal friction.

## Key Architectural Patterns
- **Agents** (`src/agents/`): Each agent encapsulates a business domain (e.g., customer, product, order) and inherits from a shared `base_agent.py`.
- **Orchestration**: `main.py` and `main_kg_generator.py` are entry points. The flow is orchestrated using LangGraph, with `router_agent.py` and `route_request_agent.py` handling agent selection.
- **Tools & Utilities**: Shared logic and helpers are in `src/core/` (e.g., database, logging, utils).
- **Knowledge Base**: `src/knowledge/knowledge.json` and `kb_generator.py` manage domain knowledge for agents.
- **Templates**: YAML templates in `templates/` define agent prompts and behaviors, split into `general/` and `specific/`.
- **Data**: Simulated and real data live in `data/`, with scripts for generating fake data (`data/scripts/fake_db_generator.py`).

## Developer Workflows
- **Run main flow**: `python main.py` (starts LangGraph orchestration)
- **Generate fake DB**: `python data/scripts/fake_db_generator.py` (creates SQLite test data)
- **Configuration**: Edit YAML files in `config/` for system, agents, and tables
- **Logs**: Output is written to `logs/aige.log`
- **Testing**: Place tests in `tests/` (no test runner specified; use `pytest` or similar)

## Project-Specific Conventions
- **Agent Naming**: All agent classes end with `_agent.py` and are located in `src/agents/`.
- **Prompt Templates**: Use YAML files in `templates/` for agent prompt configuration; keep general and specific prompts separate.
- **Database Access**: Use helpers in `src/core/database/` for all DB interactions; do not access SQLite directly in agents.
- **Extensibility**: To add a new agent, create a new file in `src/agents/`, update `config/agents.yaml`, and add a template in `templates/`.

## Integration Points
- **LLM**: Configured via environment variables and YAML; see `.env` and `config/system.yaml`.
- **ERP Connectors**: Extend `src/core/database/` for new ERP backends.
- **Web UI**: (If present) is in `interfaces/web_app/` (Streamlit).

## Examples
- To add a "supplier" agent:
  1. Create `src/agents/supplier_agent.py` inheriting from `base_agent.py`.
  2. Add configuration to `config/agents.yaml`.
  3. Add prompt template to `templates/specific/supplier.yaml`.

## References
- See `README.md` for high-level architecture and setup.
- See `src/agents/` for agent patterns.
- See `src/core/database/` for DB helpers.
- See `templates/` for prompt conventions.

---

For questions about unclear conventions or missing documentation, ask for clarification or check the latest `README.md`.
