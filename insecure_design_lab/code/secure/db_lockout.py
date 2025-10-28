# code/secure/db_lockout.py
# Persistencia simple de bloqueos e intentos fallidos usando SQLite3.
# Usa timeout y check_same_thread=False para tolerancia/concurrencia en demos.

import sqlite3
from pathlib import Path
from typing import Tuple

DB_PATH = Path(__file__).resolve().parent / "lockout.db"

def _get_conn():
    # timeout en segundos, check_same_thread=False para permitir accesos desde distintos hilos/procesos ligeros en demo
    conn = sqlite3.connect(str(DB_PATH), timeout=5.0, check_same_thread=False)
    # Usar WAL para mejor concurrencia (opcional, seguro para demos)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
    except Exception:
        pass
    conn.execute("""
        CREATE TABLE IF NOT EXISTS locks (
            username TEXT PRIMARY KEY,
            failed_count INTEGER DEFAULT 0,
            lock_until REAL DEFAULT 0
        )
    """)
    conn.commit()
    return conn

def get_status(username: str) -> Tuple[int, float]:
    """
    Devuelve (failed_count, lock_until_epoch). Si no existe usuario, devuelve (0, 0).
    """
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT failed_count, lock_until FROM locks WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    if row:
        return int(row[0]), float(row[1] or 0)
    return 0, 0.0

def update_status(username: str, failed_count: int, lock_until: float) -> None:
    """
    Inserta o actualiza el registro del usuario con failed_count y lock_until.
    """
    conn = _get_conn()
    conn.execute("""
        INSERT INTO locks (username, failed_count, lock_until)
        VALUES (?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            failed_count=excluded.failed_count,
            lock_until=excluded.lock_until
    """, (username, failed_count, lock_until))
    conn.commit()
    conn.close()

def reset_user(username: str) -> None:
    """
    Elimina el registro del usuario (resetea contadores).
    """
    conn = _get_conn()
    conn.execute("DELETE FROM locks WHERE username=?", (username,))
    conn.commit()
    conn.close()

def clear_all() -> None:
    """
    Borra todos los registros (útil para pruebas).
    """
    conn = _get_conn()
    conn.execute("DELETE FROM locks")
    conn.commit()
    conn.close()
