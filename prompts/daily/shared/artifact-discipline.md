# Shared Context: Artifact Discipline

<artifact_discipline>
Every phase must leave an auditable artifact under the date-scoped run directory. The artifact is the durable interface between agents.

Required discipline:

- write the exact artifact required by the phase;
- update `runs/YYYY-MM-DD/run-timeline.json` with `completed` or `blocked` for the current phase;
- preserve rejected and watch decisions instead of deleting them from history;
- include `blockedReason` when a phase cannot complete honestly;
- do not send intermediate Telegram messages;
- Do not send intermediate Telegram messages from scouting, dedupe, synthesis, or build phases;
- only the final delivery phase may produce a user-facing message, and only after public URL verification succeeds.

If a required prior artifact is missing, stop and mark the current phase as blocked. Do not fabricate upstream work.
</artifact_discipline>
