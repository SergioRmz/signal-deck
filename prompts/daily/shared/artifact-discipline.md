# Shared Context: Artifact Discipline

Cada fase debe dejar un artefacto auditable bajo `runs/YYYY-MM-DD/`.

Reglas:
- escribir el artefacto exacto que la fase requiere;
- actualizar `runs/YYYY-MM-DD/run-timeline.json` con `completed` o `blocked`;
- preservar decisiones de rechazo y watch en lugar de borrarlas;
- incluir `blockedReason` cuando una fase no puede completarse honestamente;
- si un artefacto previo requerido falta, detener y marcar la fase como bloqueada;
- no fabricar trabajo previo inexistente.

## Error capture

Si la fase falla por cualquier motivo (API caída, timeout, error del proveedor, permisos), escribir un archivo `runs/YYYY-MM-DD/error-phase-XX.json` con:

```json
{
  "phase": "nombre de la fase",
  "error": "descripción breve del error",
  "detail": "stack trace o mensaje completo si está disponible",
  "timestamp": "ISO-8601",
  "artifactsPresent": ["lista de artefactos que sí existían"]
}
```

Esto es obligatorio. Un error silencioso sin artefacto de error es una violación de disciplina.

## Delivery rules

- Las fases 01-04 NO envían mensajes al usuario. Solo escriben artefactos locales.
- Solo la fase 05 puede producir un mensaje para el usuario, y solo después de verificar el deploy.
- Si el deploy falló, la fase 05 envía un mensaje honesto de bloqueo, no finge éxito.
