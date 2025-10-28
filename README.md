# Insecure Design Lab

**Autor:** Herly Machado Parra  
**Proyecto:** Insecure Design Lab (2025)  
**Ubicación local:** `~/insecure_design_lab`

---

## Descripción general

Este laboratorio compara dos diseños de autenticación para mostrar, de forma educativa, cómo pequeñas decisiones de diseño provocan brechas de seguridad. Incluye:

- `code/insecure/` — Ejemplo intencionadamente inseguro (contraseñas en texto plano, sin límites de intento).
- `code/secure/` — Versión mejorada (hash + salt, bloqueo temporal, logging).
- Mecanismos opcionales de persistencia y mejora (SQLite en demo, Redis para producción, rate-limiting por IP, alertas).

**Propósito:** uso académico y demostrativo para prácticas de seguridad, auditoría de código y formación en mitigaciones (no desplegar insecure en producción).

---

## Requisitos

- Python 3.10+  
- Linux (Debian/Ubuntu o derivado)  
- Bash  
- (Opcional) Redis, Docker, pip, pytest para pruebas

Instalación de utilidades recomendadas:

sudo apt update
sudo apt install python3-pip sqlite3 -y
python3 -m pip install -r requirements.txt  # si creas requirements

##📁 Estructura del proyecto (para visualizarla mejor, abrir el README.md)

insecure_design_lab/
├── code/
│   ├── insecure/
│   │   └── app.py                # Ejemplo inseguro (contraseñas en texto plano)
│   └── secure/
│       ├── app.py                # Versión segura (PBKDF2 + bloqueo + logging)
│       ├── db_lockout.py         # Persistencia de bloqueo (SQLite) - demo
│       └── db_lockout_redis.py   # PoC Redis (opcional, atomicidad & TTL)
│
├── docs/
│   ├── hallazgos.md              # Notas de vulnerabilidades observadas
│   └── conclusiones.md           # Conclusiones y recomendaciones
│
├── logs/
│   └── auth.log                  # Registro de autenticación (audit)
│
├── tests/
│   ├── test_lab.py               # Pruebas comparativas (Python)
│   ├── test_lab.sh               # Wrapper Bash para demo y resumen de logs
│   └── test_lockout_db.py        # Test unitario para persistencia lockout
│
├── uml/
│   ├── original/                 # Diagramas del diseño inseguro
│   └── secure/                   # Diagramas del diseño seguro
│
├── docker/                       # (opcional) contenedores / compose
│   └── docker-compose.yml
│
├── requirements.txt              # (opcional) dependencias pip (pytest, redis, requests)
└── README.md

-------------------------------------------------
Generar/validar UML con PlantUML                | 
plantuml uml/original/login_insecure.puml       |
plantuml uml/secure/login_secure.puml           |
ls -l uml/original/*.png uml/secure/*.png       |
                                                |    
O buscar en la ruta especificada arriba         |
------------------------------------------------

##Flujo de demostración (orden de ejecución)

./tests/test_lab.sh — Ejecuta la demo completa:

Lanza pruebas de login correcto/incorrecto en insecure y secure.

Ejecuta demo de fuerza bruta contra insecure (encuentra contraseña).

Ejecuta demo de fuerza bruta contra secure (bloqueos aplicados).

Resume logs/auth.log y cuenta bloqueos por usuario.

code/insecure/app.py — flujo:

Recibe credenciales → compara con texto plano → respuesta True/False.

code/secure/app.py — flujo:

Verifica is_blocked(username) → si bloqueado rechaza login.

Si no bloqueado, verifica credenciales contra PBKDF2-HMAC-SHA256.

En fallo: record_failed_attempt(username) (persistir en SQLite o Redis).

Al alcanzar MAX_FAILED: crear bloqueo temporal (TTL).

Registrar evento en logs/auth.log.

Opcionalmente, code/secure/db_lockout_redis.py puede sustituir a SQLite para entornos concurrentes.


##Parámetros configurables (code/secure/app.py)


| Parámetro         | Descripción                     | Valor por defecto |
| ----------------- | ------------------------------- | ----------------- |
| `ITERATIONS`      | Iteraciones PBKDF2              | 100_000           |
| `MAX_FAILED`      | Intentos antes de bloqueo       | 3                 |
| `LOCKOUT_SECONDS` | Duración del bloqueo (segundos) | 60 (demo usa 5s)  |
| `WINDOW_SECONDS`  | Ventana para contar fallos      | 300               |
| `LOG_FILE`        | Ruta del archivo de log         | `logs/auth.log`   |

=====================================================================
#Cómo ejecutar (rápido)
Quick start — Docker (recomendado para reproducir)

Levantar servicios (Redis + API + demo container):

cd ~/insecure_design_lab/docker
docker-compose up --build


API disponible en http://localhost:8000

Swagger: http://localhost:8000/docs

Detener y remover orphans:

docker-compose down --remove-orphans
docker system prune -af --volumes  # opcional, limpieza


Entrar al contenedor de la demo:

docker exec -it insecure_design_lab bash
desde dentro:
pytest -q
python code/secure/app.py  # CLI demo

---------------------------------------------------------------------
API — endpoints (FastAPI)

POST /login
Body JSON: {"username":"admin","password":"123456"}
Respuestas:

200 → {"status":"ok","message":"Acceso concedido"}

401 → {"detail":"Acceso denegado o cuenta bloqueada"}

POST /admin/unlock/{username}
Desbloquea un usuario (demo). Ej.: POST /admin/unlock/admin → {"status":"ok","message":"Usuario 'admin' desbloqueado"}

GET /health → {"status":"running"}

Ejemplo curl:

curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'

curl -X POST http://localhost:8000/admin/unlock/admin
--------------------------------------------------------------------
Comprobaciones rápidas (logs / Redis)

Logs:

tail -n 100 logs/auth.log
# Buscar "Usuario 'admin' bloqueado" o "Login exitoso para 'admin'"


Redis (si está activo, con compose el host es redis o 127.0.0.1):

redis-cli -h 127.0.0.1 -p 6379 keys 'auth:*'
redis-cli -h 127.0.0.1 -p 6379 get auth:admin:failed
redis-cli -h 127.0.0.1 -p 6379 get auth:admin:lock_until
# Para desbloquear:
redis-cli -h 127.0.0.1 -p 6379 del auth:admin:failed auth:admin:lock_until
---------------------------------------------------------------------Cambiar la contraseña del demo (admin)

La contraseña demo inicial está fijada en code/secure/app.py al crear _users["admin"]. En tu repo actual la contraseña en claro inicial es 123456.

Para cambiarla:

Edita code/secure/app.py y modifica la línea de inicialización del hash del admin, o usa el endpoint de administración si lo implementas.

Luego rebuild docker API (si cambiaste el archivo montado en volumen puede no ser necesario rebuild):

docker-compose build lab_api
docker-compose up -d lab_api
---------------------------------------------------------------------
Tests

Ejecutar tests unitarios dentro del entorno host o contenedor:

python3 -m pip install -r requirements.txt
pytest -q


tests/test_lab.py y tests/test_lockout_db.py validan: logins, fuerza bruta y persistencia de lockouts.

--------------------------
##Salida esperada (resumen)
---------------------------

A continuación se muestra un resumen de la salida esperada cuando ejecutas la demo y pruebas principales. Sirve como referencia para verificar el correcto funcionamiento del laboratorio.

### 1) Tests automáticos
Al ejecutar `pytest -q` (o `./tests/test_lab.sh`) deberías ver:

. [100%]
1 passed in 6.4s

yaml
Copiar código
o, si ejecutas el wrapper que corre ambas demos:
== Tests básicos ==
Insecure: login admin/123456 -> True
Secure : login admin/123456 -> True
Insecure: login admin/wrong -> False
Secure : login admin/wrong -> False
...
1 passed in Xs

markdown
Copiar código

### 2) Demo de fuerza bruta
- Fuerza bruta contra `code/insecure` (sin bloqueo):

== Brute-force demo con lista corta (sin bloqueo) ==
Insecure: contraseña encontrada para 'admin' -> 123456

markdown
Copiar código

- Fuerza bruta contra `code/secure` (con bloqueo por intentos):

== Brute-force demo contra secure (con bloqueo por intentos) ==
Secure : contraseña encontrada para 'admin' -> None

shell
Copiar código

### 3) Comprobación del bloqueo en la versión segura
Simulación de intentos fallidos y bloqueo (demo):

attempt 1 for attacker -> False
attempt 2 for attacker -> False
attempt 3 for attacker -> False
attempt 4 for attacker -> False
Esperando X segundos para que caduque bloqueo (LOCKOUT_SECONDS en demo)...
attempt after wait -> False

markdown
Copiar código

Donde `LOCKOUT_SECONDS` es el valor configurado en `code/secure/app.py` (demo suele usar 5–10s).

### 4) Ejecución con Docker + API (FastAPI)
- Levantar con docker-compose:
cd docker
docker-compose up --build

diff
Copiar código

- Comprobar que la API está arriba (Swagger):
abrir en el navegador:
http://localhost:8000/docs

rust
Copiar código

- Peticiones de ejemplo:

Login fallido / bloqueado:
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrong"}'
# => {"detail":"Acceso denegado o cuenta bloqueada"}
Login exitoso (contraseña demo):

bash
Copiar código
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'
# => {"status":"ok","message":"Acceso concedido"}
Desbloquear usuario (demo):

bash
Copiar código
curl -X POST http://localhost:8000/admin/unlock/admin
# => {"status":"ok","message":"Usuario 'admin' desbloqueado"}
Health check:

bash
Copiar código
curl http://localhost:8000/health
# => {"status":"running"}
Nota: si tu API responde {"detail":"Not Found"} para /admin/unlock, revisa que code/secure/api.py tenga la ruta correcta y que el contenedor en docker-compose esté cargando la versión actual del archivo (comprueba volúmenes o rebuild).

5) Logs y comprobaciones internas
Ver logs de autenticación:

bash
Copiar código
tail -n 50 logs/auth.log
# Buscar líneas como:
# "Login exitoso para 'admin'"
# "Usuario 'admin' bloqueado hasta <epoch>"
Si usas Redis (compose):

bash
Copiar código
redis-cli -h 127.0.0.1 -p 6379 keys 'auth:*'
redis-cli -h 127.0.0.1 -p 6379 get auth:admin:failed
redis-cli -h 127.0.0.1 -p 6379 get auth:admin:lock_until
# Para "desbloquear" manualmente:
redis-cli -h 127.0.0.1 -p 6379 del auth:admin:failed auth:admin:lock_until
6) Ubicación de la contraseña demo
La contraseña inicial del usuario admin usada en las demos está fijada en memoria al iniciar el módulo seguro:

Archivo: code/secure/app.py

Ejemplo de valor por defecto en el laboratorio: 123456

Si quieres cambiarla edita code/secure/app.py (luego reinicia/rebuild containers si es necesario).


