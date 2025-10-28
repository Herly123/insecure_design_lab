#!/usr/bin/env bash
set -euo pipefail

# Ejecutar tests (Python)
python3 tests/test_lab.py

# -- Resumen de logs (si existe) --
LOGFILE="logs/auth.log"
if [ -f "$LOGFILE" ]; then
  echo
  echo "==== Resumen rápido de logs: $LOGFILE ===="
  echo "Total de líneas en el log: $(wc -l < "$LOGFILE")"
  echo

  echo "-- Conteo de bloqueos (total) --"
  grep -i "bloqueado" "$LOGFILE" || true
  echo "Total bloqueos: $(grep -i "bloqueado" "$LOGFILE" | wc -l)"

  echo
  echo "-- Bloqueos por usuario --"
  grep -i "Usuario '.*' bloqueado" "$LOGFILE" \
    | sed -E "s/.*Usuario '([^']+)'.*/\1/" \
    | sort | uniq -c | sort -nr || true

  echo
  echo "-- Intentos fallidos por usuario (aprox.) --"
  grep -i "Intento fallido para usuario" "$LOGFILE" \
    | sed -E "s/.*Intento fallido para usuario '([^']+)'.*/\1/" \
    | sort | uniq -c | sort -nr || true

  echo
  echo "-- Logins exitosos por usuario --"
  grep "Login exitoso para" "$LOGFILE" \
    | sed -E "s/.*Login exitoso para '([^']+)'.*/\1/" \
    | sort | uniq -c | sort -nr || true

  echo
  echo "Para ver el log completo: tail -n 200 $LOGFILE"
else
  echo "No se encontró $LOGFILE"
fi
