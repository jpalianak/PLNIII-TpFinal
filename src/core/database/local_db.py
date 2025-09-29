from sqlalchemy import create_engine

# ---------- SQLite ----------
def get_sqlite_engine(db_path="FakeDB.sqlite", echo=False):
    """
    Conexión a SQLite local (archivo .sqlite).
    """
    return create_engine(f"sqlite:///{db_path}", echo=echo)

# ---------- PostgreSQL ----------
def get_postgres_engine(user="postgres", password="postgres", host="localhost", port=5432, db="mydb", echo=False):
    """
    Conexión a PostgreSQL local.
    """
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url, echo=echo)

# ---------- MySQL / MariaDB ----------
def get_mysql_engine(user="root", password="", host="localhost", port=3306, db="mydb", echo=False):
    """
    Conexión a MySQL/MariaDB local.
    """
    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url, echo=echo)