# Data contracts and canonical fixtures

This directory contains the canonical machine-readable surface for signal-deck:

- `signal-input.sample.json` and `signal-input.schema.json` for upstream editorial packets
- `briefing.sample.json` and `briefing.schema.json` for generated briefing payloads
- `visual-composition.sample.json` and `visual-composition.schema.json` for presentation intent

The React + Vite renderer copies the selected briefing and composition payloads into `apps/web/public/data/` before `dev` and `build`, keeping the deployed site fully static while the repository keeps canonical artifacts in one framework-independent location.
