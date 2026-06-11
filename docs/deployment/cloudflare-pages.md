# Deploy en Cloudflare Pages

## Enfoque inicial

La página vive en:

```text
apps/briefing-page/
```

Eso permite desplegarla como sitio estático sin build complejo.

## Configuración sugerida en Cloudflare Pages

- **Framework preset**: None
- **Build command**: dejar vacío
- **Build output directory**: `apps/briefing-page`
- **Opcional pero recomendable en el repo**: guardar `wrangler.toml` en la raíz con:

```toml
pages_build_output_dir = "./apps/briefing-page"
```

Eso deja la intención de despliegue codificada dentro del repositorio, en lugar de depender solo de una configuración manual en el dashboard.

## Flujo básico

1. conectar el repo a Cloudflare Pages
2. seleccionar la rama `main`
3. usar `apps/briefing-page` como directorio de publicación
4. desplegar

## Ventajas de este enfoque

- cero dependencia de framework
- deploy rápido
- menos puntos de falla
- ideal para iterar primero sobre contenido y diseño

## Evolución posible

Si más adelante hace falta un pipeline de build, se puede migrar a:

- Vite estático
- Astro
- Next.js exportado estáticamente

pero por ahora no hace falta pagar ese costo de complejidad.
