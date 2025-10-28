#!/usr/bin/env python3
"""
tests/test_lab.py
Pruebas comparativas que ahora demuestran bloqueo por intentos en code/secure/app.py
"""
import os
import importlib.util
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
def load_module_from_path(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

insecure_mod = load_module_from_path(os.path.join(ROOT, 'code', 'insecure', 'app.py'), 'insecure_app')
secure_mod = load_module_from_path(os.path.join(ROOT, 'code', 'secure', 'app.py'), 'secure_app')

print("== Tests básicos ==")
print("Insecure: login admin/123456 ->", insecure_mod.login('admin', '123456'))
print("Secure  : login admin/123456 ->", secure_mod.login('admin', '123456'))

print("Insecure: login admin/wrong ->", insecure_mod.login('admin', 'wrong'))
print("Secure  : login admin/wrong ->", secure_mod.login('admin', 'wrong'))

print("\n== Brute-force demo con lista corta (sin bloqueo) ==")
common_passwords = ['123', 'password', '123456', 'qwerty', 'letmein', '12345678', 'admin', '123456789']

def brute_force_login(module, username, pwd_list):
    for p in pwd_list:
        if module.login(username, p):
            return p
    return None

# Brute-force contra insecure
found_insecure = brute_force_login(insecure_mod, 'admin', common_passwords)
print(f"Insecure: contraseña encontrada para 'admin' -> {found_insecure}")

# Reset: para secure, reajustamos parámetros para que el test demuestre bloqueo rápido
if hasattr(secure_mod, "_set_lock_params"):
    secure_mod._set_lock_params(max_failed=3, lockout_seconds=5)  # bloqueo rápido para demo

print("\n== Brute-force demo contra secure (con bloqueo por intentos) ==")
found_secure = brute_force_login(secure_mod, 'admin', common_passwords)
print(f"Secure  : contraseña encontrada para 'admin' -> {found_secure}")

print("\n== Comprobación de bloqueo en secure ==")
# Intentos adicionales: forzamos 3 intentos fallidos seguidos para bloquear
for i in range(4):
    ok = secure_mod.login('attacker', 'wrong'+str(i))
    print(f"attempt {i+1} for attacker -> {ok}")

print("Esperando 6 segundos para que caduque bloqueo (LOCKOUT_SECONDS=5 en demo)...")
time.sleep(6)

print("Reintentando after lockout expiry:")
print("attempt after wait ->", secure_mod.login('attacker', 'wrong-final'))

print("\n== Observaciones finales ==")
print("- La versión 'secure' ahora aplica bloqueo temporal tras 3 fallos (configurable).")
print("- Esto evita que un brute-force simple encuentre la contraseña durante el periodo de bloqueo.")
print("- Recomendaciones: persistir contadores en Redis/DB para sistemas reales, añadir rate limiting por IP, MFA y notificaciones de seguridad.")
