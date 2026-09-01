import os
import socket
from datetime import datetime, timezone

import psutil
import psycopg


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "sredb"),
        user=os.getenv("DB_USER", "sreuser"),
        password=os.environ["DB_PASSWORD"],
    )


def collect_system_info():
    return {
        "collected_at": datetime.now(timezone.utc),
        "hostname": socket.gethostname(),
        "cpu_count": psutil.cpu_count(logical=True) or 0,
        "memory_mb": round(psutil.virtual_memory().total / (1024 * 1024)),
        "disk_usage_percent": psutil.disk_usage("/").percent,
        "load_average": os.getloadavg()[0],
    }


def save_system_info(info):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO system_info (
                    collected_at,
                    hostname,
                    cpu_count,
                    memory_mb,
                    disk_usage_percent,
                    load_average
                )
                VALUES (
                    %(collected_at)s,
                    %(hostname)s,
                    %(cpu_count)s,
                    %(memory_mb)s,
                    %(disk_usage_percent)s,
                    %(load_average)s
                )
                """,
                info,
            )
        conn.commit()


if __name__ == "__main__":
    system_info = collect_system_info()

    print("Collected system information:")
    print(system_info)

    save_system_info(system_info)

    print("System information saved successfully.")
