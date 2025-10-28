# Conclusiones (esqueleto)

- Cambios aplicados:
  - Hashing con PBKDF2 + salt.
  - Implementación de comparación segura (hmac.compare_digest).
- Pendientes / recomendaciones:
  - Forzar contraseñas robustas / validar entropía.
  - Implementar rate limiting y bloqueo por intentos fallidos.
  - Añadir MFA (2FA).
  - Registrar y monitorear intentos de autenticación.
