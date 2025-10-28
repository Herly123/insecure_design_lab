# code/insecure/app.py
"""
Módulo de demostración INTENCIONALMENTE VULNERABLE.

Contenido:
- Usuarios con contraseñas en texto plano.
- No aplicar en producción.
Propósito: laboratorio educativo para comparar con la versión segura.
"""

import getpass
from typing import Dict

# ---- Demo: usuarios con contraseñas en texto plano (vulnerable) ----
users: Dict[str, str] = {
    "admin": "123456",   # contraseña en texto plano (insegura)
    "user": "password"
}

def login(username: str, password: str) -> bool:
    """
    Login simple: comparación en texto plano.
    Retorna True si coincide username+password, False en caso contrario.
    """
    return username in users and users[username] == password

def get_users() -> Dict[str, str]:
    """
    Devuelve una copia de la estructura 'users' para pruebas.
    ADVERTENCIA: contiene contraseñas en texto plano.
    """
    return dict(users)

if __name__ == "__main__":
    try:
        username = input("Usuario: ").strip()
        password = getpass.getpass("Contraseña: ")
        if login(username, password):
            print(f"Bienvenido {username}")
        else:
            print("Usuario o contraseña incorrectos")
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")

