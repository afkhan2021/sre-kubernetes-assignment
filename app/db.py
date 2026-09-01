import os

import psycopg


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "sredb"),
        user=os.getenv("DB_USER", "sreuser"),
        password=os.environ["DB_PASSWORD"],
    )


def initialize_database():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS system_info (
                    id SERIAL PRIMARY KEY,
                    collected_at TIMESTAMPTZ NOT NULL,
                    hostname VARCHAR(255) NOT NULL,
                    cpu_count INTEGER NOT NULL,
                    memory_mb INTEGER NOT NULL,
                    disk_usage_percent DOUBLE PRECISION NOT NULL,
                    load_average DOUBLE PRECISION NOT NULL
                )
                """
            )
        conn.commit()
