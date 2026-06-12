# Deploy en Cloudflare Pages

## Enfoque recomendado ahora

El renderer desplegable más alineado con el estado actual del producto vive en:

```text
apps/web/
```

Ahora es un renderer **React + Vite** completamente estático:

- consume `briefing.json` y `composition.json`
- sincroniza esos artefactos a `apps/web/public/data/` antes de `dev` y `build`
- produce salida lista para Pages en `apps/web/dist/`

## Configuración sugerida en Cloudflare Pages

- **Framework preset**: `Vite`
- **Root directory**: `apps/web`
- **Build command**: `npm install && npm run build`
- **Build output directory**: `dist`

Si prefieres configurar desde la raíz del repo en vez de usar `apps/web` como root:

- **Framework preset**: `Vite`
- **Root directory**: `/`
- **Build command**: `cd apps/web && npm install && npm run build`
- **Build output directory**: `apps/web/dist`

## Variables y datos

El build usa estos paths:

- `SIGNAL_DECK_BRIEFING_PATH`
- `SIGNAL_DECK_COMPOSITION_PATH`

Ambos se resuelven relativos a `apps/web/`.

Antes de compilar, `apps/web/scripts/sync-renderer-data.mjs` copia esos archivos hacia:

```text
apps/web/public/data/briefing.json
apps/web/public/data/composition.json
```

Eso mantiene el deploy final como sitio estático puro.

## Flujo básico

1. conectar el repo a Cloudflare Pages
2. seleccionar la rama deseada (`main` o una rama de preview)
3. apuntar el proyecto a `apps/web`
4. ejecutar el build de Vite
5. publicar `dist`

## Ventajas de este enfoque

- sigue siendo estático
- despliegue simple
- build más liviano que Next para este caso
- encaja mejor con el modelo actual de renderer editorial
- deja abierta una migración futura a una app más compleja solo si realmente hace falta

## Alternativa todavía válida

El prototipo original en:

```text
apps/briefing-page/
```

sigue siendo desplegable como sitio estático sin build, pero ya no es la ruta principal para la evolución del renderer componentizado.
