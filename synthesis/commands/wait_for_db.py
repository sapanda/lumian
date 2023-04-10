import psycopg2
import time

from app.config import Settings


def wait_for_db(settings: Settings = Settings()):
    """ Wait for the database to be available """

    db_up = False
    while not db_up:
        try:
            postgres_connection = psycopg2.connect(
                user=settings.db_user,
                password=settings.db_password,
                host=settings.db_host,
                port=settings.db_port,
                database=settings.db_name)
            db_up = True
        except psycopg2.OperationalError:
            time.sleep(1)
        finally:
            if postgres_connection:
                postgres_connection.close()


wait_for_db()
