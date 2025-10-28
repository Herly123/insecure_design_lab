# tests/test_lockout_db.py
import sqlite3
import time
import os

DB_PATH = os.path.join("code", "secure", "lockout.db")

def test_lock_exists_for_admin():
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    cur.execute("SELECT * FROM locks WHERE username='admin'")
    row = cur.fetchone()
    db.close()

    assert row is not None, "No hay fila de lock para 'admin'"

    username, attempts, expiry = row
    assert username == "admin", f"Usuario inesperado: {username}"
    assert isinstance(attempts, int), "Campo attempts no es entero"
    assert isinstance(expiry, float), "Campo expiry no es float"
    assert expiry > 0, "El valor de expiry no debe ser 0 o negativo"

    # Verificar lógica del tiempo (puede haber expirado)
    now = time.time()
    if expiry > now:
        print(f"Bloqueo activo, expira en {expiry - now:.2f} segundos")
    else:
        print(f"Bloqueo expirado hace {now - expiry:.2f} segundos (esperado si ya pasó el lockout)")

