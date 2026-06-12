# Cloudflare Pages deployment

## Current deployment target

The deployable renderer now lives in:

```text
apps/web/
```

It is a fully static **React + Vite** renderer:

- consumes `briefing.json` and `composition.json`
- syncs those artifacts into `apps/web/public/data/` before `dev` and `build`
- emits the Pages-ready static site into `apps/web/dist/`

The previous framework-free prototype has been removed from the active repository. The Vite renderer is the single presentation surface for local iteration and external deployment.

## Recommended Cloudflare Pages configuration

If using a dashboard Pages configuration, use this when `apps/web` is configured as the Pages root:

- **Framework preset**: `Vite`
- **Root directory**: `apps/web`
- **Build command**: `npm install && npm run build`
- **Build output directory**: `dist`

If configuring the project from the repository root instead:

- **Framework preset**: `Vite`
- **Root directory**: `/`
- **Build command**: `cd apps/web && npm install && npm run build`
- **Build output directory**: `apps/web/dist`

## Workers Builds configuration

The connected GitHub check currently runs through Cloudflare Workers Builds, so the root `wrangler.toml` also encodes the deploy path:

```toml
[build]
command = "cd apps/web && npm install && npm run build"

[assets]
directory = "./apps/web/dist"
```

This makes a fresh Cloudflare build produce `apps/web/dist/` before Wrangler uploads static assets.

## Variables and data artifacts

The build can be pointed at explicit artifact paths with:

- `SIGNAL_DECK_BRIEFING_PATH`
- `SIGNAL_DECK_COMPOSITION_PATH`

Both paths are resolved relative to `apps/web/`.

By default, the renderer reads the canonical repository fixtures from:

```text
../../data/briefing.sample.json
../../data/visual-composition.sample.json
```

Before compiling, `apps/web/scripts/sync-renderer-data.mjs` copies those files into:

```text
apps/web/public/data/briefing.json
apps/web/public/data/composition.json
```

That keeps the final deployment a pure static site.

## Basic flow

1. Connect the repository to Cloudflare Pages.
2. Select the desired branch (`main` or a preview branch).
3. Point Pages at `apps/web`.
4. Run the Vite build.
5. Publish `dist`.

## Why this approach fits the current product

- It remains static and cheap to operate.
- It is lighter than the previous Next.js path for the current renderer needs.
- It keeps content contracts and visual composition payloads explicit.
- It gives the project one deployment target instead of maintaining a legacy prototype beside the component renderer.
