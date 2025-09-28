# 🧠 Procesamiento Natural del Lenguaje – Sistema Multiagente con LLM

Este proyecto implementa un **sistema de agentes inteligentes** que interactúan con una base de datos SQlite. Se utilizan **LLMs**, **LangGraph**, **LangChain**, y una arquitectura de agentes especializados que cooperan para responder consultas en lenguaje natural.

---

## 📂 Estructura del proyecto

```
.
├── main.py                     # Punto de entrada principal
├── main_kg_generator.py         # Generador de base de conocimiento (KB)
├── .env                         # Variables de entorno
├── config/                      # Archivos de configuración (sistema, agentes, tablas)
├── data/
│   ├── db/                      # Base de datos SQLite fake
│   └── scripts/                 # Generador de base de datos fake
├── docs/                        # Diagramas y presentaciones
├── logs/                        # Logs de ejecución
├── src/
│   ├── agents/                  # Agentes especializados
│   ├── core/                    # Módulos base (DB, logging, utils)
│   ├── knowledge/               # Generador y almacenamiento de conocimiento
│   ├── workflows/               # Definición de grafos de ejecución
│   └── __init__.py
├── templates/                   # Prompts y plantillas para agentes
├── tests/                       # Casos de prueba
└── README.md
```

---

## ⚙️ Requisitos

* Python 3.10+
* [LangChain](https://www.langchain.com/)
* [SQLAlchemy](https://www.sqlalchemy.org/)
* [Faker](https://faker.readthedocs.io/)
* [PyYAML](https://pyyaml.org/)
* Una API key para el proveedor LLM (configurada en `.env`)

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

## ▶️ Uso

1. **Configurar variables de entorno** en `.env` (ejemplo: clave del modelo LLM, configuración de DB).
2. **Generar la base fake**:

```bash
python data/scripts/fake_db_generator.py
```

3. **Ejecutar el sistema principal**:

```bash
python main.py
```

4. **Generar base de conocimiento (KB)**:

```bash
python main_kg_generator.py
```

---

## 🛠️ Configuración

* `config/tables.yaml` → Define las tablas, nombres lógicos y columnas.
* `config/agents.yaml` → Define los agentes y su comportamiento.
* `config/system.yaml` → Configuración global del sistema.
* `.env` → Claves y parámetros sensibles.

---

## 📖 Documentación

* `docs/Diagram.drawio` → Diagrama de arquitectura.
* `docs/Presentación-AIGE.pptx` → Presentación general del proyecto.

---

## 📜 Logs y pruebas

* Los logs se almacenan en `logs/aige.log`.
* Los tests unitarios se ubican en `tests/`.

---

✍️ Autor: **Juan Pablo Alianak**
