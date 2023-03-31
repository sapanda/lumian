from app.config import Settings
import psycopg2


def get_db_connection(
    settings: Settings = Settings()
):
    print("trying db connection")
    postgres_connection = psycopg2.connect(
        user=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name)
    return postgres_connection


postgres_connection = get_db_connection()

with postgres_connection:
    with postgres_connection.cursor() as cursor:
        cursor.execute("CREATE SCHEMA IF NOT EXISTS synthesis;")
        cursor.execute("""CREATE TABLE synthesis.transcript(
                id int NOT NULL,
                data json NOT NULL,
                PRIMARY KEY(id)
                )""")
        postgres_connection.commit()
