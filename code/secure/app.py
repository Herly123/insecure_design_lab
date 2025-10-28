# code/secure/app.py
# Auth seguro con PBKDF2 + salt, bloqueo por intentos y soporte de persistencia:
# - Redis si está disponible
# - db_lockout.py si existe
# - Memoria en caso contrario

import hashlib
import hmac
import secrets
import time
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict

# ==========================================================
# CONFIGURACIÓN BASE
# ==========================================================
ITERATIONS = 200_000
MAX_FAILED = 3
LOCKOUT_SECONDS = 10

# ==========================================================
# LOGGING CONFIGURACIÓN
# ==========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "auth.log"
LOG_MAX_BYTES = 5 * 1024 * 1024
LOG_BACKUPS = 3

logger = logging.getLogger("secure_auth")
if not logger.handlers:
    handler = RotatingFileHandler(LOG_FILE, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUPS)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# ==========================================================
# DETECCIÓN DE REDIS Y DB_LOCKOUT
# ==========================================================
_USE_REDIS = False
_USE_DB = False
db_lockout = None
rds = None

try:
    import redis
    rds = redis.Redis(host="redis", port=6379, decode_responses=True)
    rds.ping()
    _USE_REDIS = True
    logger.info("Redis detectado y habilitado para persistencia de lockout")
except Exception as e:
    logger.warning("Redis no disponible: %s", e)

if not _USE_REDIS:
    try:
        from code.secure import db_lockout
        _USE_DB = True
        logger.info("db_lockout habilitado via paquete")
    except Exception:
        pass

# ==========================================================
# USUARIOS CON HASH Y SALT
# ==========================================================
def _hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)

_users: Dict[str, Dict[str, bytes]] = {}
_admin_salt = secrets.token_bytes(16)
_users["admin"] = {"salt": _admin_salt, "hash": _hash_password("123456", _admin_salt)}
_user_salt = secrets.token_bytes(16)
_users["user"] = {"salt": _user_salt, "hash": _hash_password("password", _user_salt)}

# ==========================================================
# FUNCIONES DE PERSISTENCIA (Redis, DB o memoria)
# ==========================================================
_failed_attempts: Dict[str, int] = {}
_lockout_until: Dict[str, float] = {}

def _get_status(username: str):
    if _USE_REDIS:
        try:
            failed = int(rds.get(f"auth:{username}:failed") or 0)
            lock_until = float(rds.get(f"auth:{username}:lock_until") or 0.0)
            return failed, lock_until
        except Exception:
            logger.exception("Error leyendo estado desde Redis")
    elif _USE_DB:
        try:
            return db_lockout.get_status(username)
        except Exception:
            logger.exception("Error en db_lockout.get_status")
    return _failed_attempts.get(username, 0), _lockout_until.get(username, 0.0)

def _update_status(username: str, failed_count: int, lock_until: float):
    if _USE_REDIS:
        try:
            rds.set(f"auth:{username}:failed", failed_count)
            rds.set(f"auth:{username}:lock_until", lock_until)
            return
        except Exception:
            logger.exception("Error actualizando estado en Redis")
    elif _USE_DB:
        try:
            db_lockout.update_status(username, failed_count, lock_until)
            return
        except Exception:
            logger.exception("Error actualizando en db_lockout")
    _failed_attempts[username] = failed_count
    _lockout_until[username] = lock_until

def _reset_user(username: str):
    if _USE_REDIS:
        try:
            rds.delete(f"auth:{username}:failed", f"auth:{username}:lock_until")
            return
        except Exception:
            logger.exception("Error eliminando estado de Redis")
    elif _USE_DB:
        try:
            db_lockout.reset_user(username)
            return
        except Exception:
            logger.exception("Error en db_lockout.reset_user")
    _failed_attempts.pop(username, None)
    _lockout_until.pop(username, None)

# ==========================================================
# LÓGICA DE LOGIN
# ==========================================================
def login(username: str, password: str) -> bool:
    now = time.time()
    failed_count, lock_until = _get_status(username)

    if lock_until and now < lock_until:
        logger.info("Cuenta '%s' bloqueada hasta %s", username, lock_until)
        return False

    if username not in _users:
        failed_count += 1
        logger.warning("Intento con usuario no existente '%s'", username)
        if failed_count >= MAX_FAILED:
            new_lock = time.time() + LOCKOUT_SECONDS
            _update_status(username, 0, new_lock)
            logger.warning("Bloqueo aplicado a '%s' hasta %s", username, new_lock)
        else:
            _update_status(username, failed_count, 0.0)
        return False

    user = _users[username]
    hashed = _hash_password(password, user["salt"])
    ok = hmac.compare_digest(hashed, user["hash"])

    if ok:
        logger.info("Login exitoso para '%s'", username)
        _reset_user(username)
        return True
    else:
        failed_count += 1
        if failed_count >= MAX_FAILED:
            new_lock = time.time() + LOCKOUT_SECONDS
            _update_status(username, 0, new_lock)
            logger.warning("Bloqueo aplicado a '%s' hasta %s", username, new_lock)
        else:
            _update_status(username, failed_count, 0.0)
        logger.info("Contraseña incorrecta para '%s'", username)
        return False

# ==========================================================
# UTILIDADES
# ==========================================================
def get_users():
    return {k: {"salt": v["salt"], "hash": v["hash"]} for k, v in _users.items()}

def _set_lock_params(max_failed: int = 3, lockout_seconds: int = 10):
    global MAX_FAILED, LOCKOUT_SECONDS
    MAX_FAILED = max_failed
    LOCKOUT_SECONDS = lockout_seconds
    logger.info("[DEMO] Lockout ajustado: %d intentos, %d segundos", max_failed, lockout_seconds)

# ==========================================================
# CLI para prueba manual
# ==========================================================
if __name__ == "__main__":
    print("=== Login seguro con Redis persistente (si disponible) ===")
    user = input("Usuario: ").strip()
    pwd = input("Contraseña: ")
    ok = login(user, pwd)
    print("✅ Acceso concedido" if ok else "❌ Acceso denegado")

