import os

import psycopg


def get_connection():
    return psycopg.connect(
        dbname=os.getenv("POSTGRES_DB", "pulsemart"),
        user=os.getenv("POSTGRES_USER", "pulselake"),
        password=os.getenv("POSTGRES_PASSWORD", "pulselake_local"),
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=int(os.getenv("POSTGRES_PORT", "55432")),
    )
