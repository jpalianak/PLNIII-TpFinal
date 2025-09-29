import os
import yaml
import sqlite3
import random
from faker import Faker

fake = Faker()

# rutas coherentes con tu proyecto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
db_file = os.path.join(project_root, "data", "db", "fake_db.sqlite")
yaml_file = os.path.join(project_root, "config", "tables.yaml")

# conexión sqlite
os.makedirs(os.path.dirname(db_file), exist_ok=True)
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# cargar yaml
with open(yaml_file, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

tables = config["tables"]

# ----------- crear tablas dinámicamente -------------
for table_key, table_info in tables.items():
    table_name = table_info["logical_name"]
    column_defs = [f"{logical_col} TEXT" for logical_col in table_info["columns"].values()]
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    cursor.execute(f"CREATE TABLE {table_name} ({', '.join(column_defs)})")
    print(f"Tabla {table_name} creada con columnas: {list(table_info['columns'].values())}")

conn.commit()

# ----------- configuración IDs ----------------
ID_WIDTH = 6  # cantidad de dígitos de los IDs

def format_id(num: int) -> str:
    """Convierte un entero en un string con ceros a la izquierda."""
    return str(num).zfill(ID_WIDTH)

# ----------- funciones para datos fake --------------
def fake_value(col_name):
    """Genera un valor en función del nombre lógico de columna."""
    if "nombre" in col_name:
        return fake.name()
    if "descripcion" in col_name:
        return fake.sentence(nb_words=4)
    if "tipo" in col_name or "familia" in col_name:
        return fake.word()
    if "fecha" in col_name:
        return fake.date_this_year().strftime("%Y%m%d")
    if "precio" in col_name or "valor" in col_name or "tasa" in col_name:
        return str(round(random.uniform(10, 1000), 2))
    if "cantidad" in col_name:
        return str(random.randint(1, 50))
    if "unidad_negocio" in col_name:
        return random.choice(["NAC", "INT"])
    if "vendedor" in col_name:
        return str(random.randint(100, 999))
    return fake.word()

# ----------- poblar tablas en orden correcto ----------------
num_rows = {
    "clientes": 50,
    "productos": 100,
    "encabezado_pedidos": 200,
    "items_pedidos": 500
}

# IDs almacenados para relaciones
clientes_ids = []
productos_ids = []
pedidos_ids = []

id_counters = {
    "clientes": 0,
    "productos": 0,
    "encabezado_pedidos": 0,
    "items_pedidos": 0
}

populate_order = ["clientes", "productos", "encabezado_pedidos", "items_pedidos"]

for table_name in populate_order:
    table_info = next(v for k, v in tables.items() if v["logical_name"] == table_name)
    n = num_rows.get(table_name, 10)
    logical_cols = list(table_info["columns"].values())

    for _ in range(n):
        row = {}

        if table_name == "clientes":
            id_counters["clientes"] += 1
            row["cliente_id"] = format_id(id_counters["clientes"])
            clientes_ids.append(row["cliente_id"])
            for col in logical_cols:
                if col != "cliente_id":
                    row[col] = fake_value(col)

        elif table_name == "productos":
            id_counters["productos"] += 1
            row["producto_id"] = format_id(id_counters["productos"])
            productos_ids.append(row["producto_id"])
            for col in logical_cols:
                if col != "producto_id":
                    row[col] = fake_value(col)

        elif table_name == "encabezado_pedidos":
            id_counters["encabezado_pedidos"] += 1
            row["pedido_id"] = format_id(id_counters["encabezado_pedidos"])
            pedidos_ids.append(row["pedido_id"])
            for col in logical_cols:
                if col == "cliente_id":
                    row[col] = random.choice(clientes_ids)
                elif col != "pedido_id":
                    row[col] = fake_value(col)

        elif table_name == "items_pedidos":
            id_counters["items_pedidos"] += 1
            row["item_numero"] = format_id(id_counters["items_pedidos"])
            for col in logical_cols:
                if col == "pedido_id":
                    row[col] = random.choice(pedidos_ids)
                elif col == "producto_id":
                    row[col] = random.choice(productos_ids)
                elif col != "item_numero":
                    row[col] = fake_value(col)

        # inserción
        cols = ", ".join(row.keys())
        placeholders = ", ".join("?" for _ in row)
        cursor.execute(f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})", list(row.values()))

conn.commit()
conn.close()
print("Base fake coherente generada en fake_db.sqlite")
