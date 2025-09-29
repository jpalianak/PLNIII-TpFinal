import os
from src.core.utils.config_system_loader import load_system_config
from src.core.database.local_db import get_sqlite_engine
#from src.core.database.totvs import get_sqlserver_engine 

def get_db_engine():
    """
    Devuelve el engine adecuado según la configuración del sistema.
    Soporta local y cloud. Lanza error si la configuración es inválida.
    """
    config, base_dir = load_system_config()
    connection_type = config.get("system", {}).get("connection_type", "").lower()

    if connection_type == "local":
        db_path = os.path.join(base_dir, config["local_database"]["path"])
        engine = get_sqlite_engine(db_path=db_path)
        engine_type = engine.dialect.name
        return engine, engine_type

    elif connection_type == "cloud":
        #engine = get_sqlserver_engine()
        engine_type = engine.dialect.name
        return engine, engine_type

    else:
        raise ValueError(
            f"connection_type inválido o no definido en system.yaml: '{connection_type}'. "
            "Debe ser 'local' o 'cloud'."
        )