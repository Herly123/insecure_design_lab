# Hallazgos iniciales - Insecure Design Lab

## Resumen rápido
- Usuario 'admin' y 'user' provienen con contraseñas débiles y/o en texto plano en la versión insegura.
- Consultas/funciones sin protección, sin mecanismos de límite de intentos.
- Falta de cifrado de almacenamiento (insecure) y ausencia de controles de acceso.

## Vulnerabilidades detectadas (ejemplo)
- Contraseñas en texto plano (Alta).
- Sin control de intentos / bloqueo / rate limiting (Alta).
- Contraseñas débiles (Media).
