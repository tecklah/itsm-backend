import psycopg2
from langchain_community.utilities.sql_database import SQLDatabase


def get_db_connection(dbname, username, password, host="localhost", port="5432"):
    try:
        return psycopg2.connect(
            dbname=dbname,
            user=username,
            password=password,
            host=host,
            port=port,
        )
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")


def get_langchain_db_connection(dbname, username, password, host="localhost"):
    """Return a SQLDatabase, supporting both TCP and Cloud SQL Unix sockets.

    For Cloud SQL on Cloud Run, DB_HOST is typically set to
    "/cloudsql/<PROJECT>:<REGION>:<INSTANCE>", and connections must be made
    via the unix socket using a SQLAlchemy query parameter, not as a TCP host.
    """

    if host and host.startswith("/cloudsql/"):
        # Cloud SQL unix socket: use host as query parameter
        uri = (
            f"postgresql+psycopg2://{username}:{password}@/{dbname}?host={host}"
        )
    else:
        # Normal TCP host (local dev, etc.)
        uri = f"postgresql+psycopg2://{username}:{password}@{host}/{dbname}"

    return SQLDatabase.from_uri(uri)
