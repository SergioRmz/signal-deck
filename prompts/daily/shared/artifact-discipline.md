# Shared Context: Artifact Discipline

Every phase must leave an auditable artifact under `runs/YYYY-MM-DD/`.

Rules:
- write the exact artifact required by the phase;
- update `runs/YYYY-MM-DD/run-timeline.json` with `completed` or `blocked`;
- preserve rejected and watch decisions instead of deleting them;
- include `blockedReason` when a phase cannot complete honestly;
- if a required prior artifact is missing, stop and mark the current phase as blocked;
- do not fabricate upstream work.

## Error capture

If the phase fails for any reason (API down, timeout, provider error, permissions), write a file `runs/YYYY-MM-DD/error-phase-XX.json` with:

```json
{
  "phase": "phase name",
  "error": "brief error description",
  "detail": "full stack trace or message if available",
  "timestamp": "ISO-8601",
  "artifactsPresent": ["list of artifacts that did exist"]
}
```

This is mandatory. A silent error without an error artifact is a discipline violation.

## Delivery rules

- Phases 01-04 do NOT send messages to the user. They only write local artifacts.
- Only phase 05 may produce a user-facing message, and only after verifying the deploy.
- If the deploy failed, phase 05 sends an honest blocker message, not a fake success.
