# signal-deck

Sistema editorial para producir y entregar briefings ejecutivos de tecnología, IA y economía.

La primera meta del repo es una base seria, simple y mantenible para dos piezas:

1. **la inteligencia editorial**: selección, síntesis y estructuración de señales
2. **la entrega**: una single page dark-theme, accesible externamente, apta para Cloudflare Pages

## Principios del proyecto

- **Simplicidad operativa**: menos moving parts, menos deuda.
- **Salida premium**: no resumir noticias; producir tesis, contexto e implicaciones.
- **Escalabilidad editorial**: estructura clara para crecer sin convertir el repo en un cajón.
- **Deploy fácil**: base compatible con hosting estático en Cloudflare Pages.

## Estructura

```text
signal-deck/
├── README.md
├── .gitignore
├── apps/
│   └── briefing-page/
│       ├── index.html
│       ├── styles.css
│       └── app.js
└── docs/
    ├── architecture.md
    ├── product-brief.md
    └── deployment/
        └── cloudflare-pages.md
```

## Qué contiene esta primera base

- una **single page dark-theme** de referencia
- un **renderer estático** que consume un briefing en JSON local
- una estructura de contenido pensada para briefings ejecutivos
- documentación inicial de producto, arquitectura y despliegue

## Cómo correr localmente

### Opción simple
Desde la raíz del repo:

```bash
cd apps/briefing-page
python3 -m http.server 4173
```

Luego abre:

```text
http://localhost:4173
```

## Siguiente fase sugerida

1. fijar el esquema editorial de entrada/salida
2. decidir el pipeline de generación del briefing
3. conectar la página a datos reales o a artefactos generados
4. desplegar en Cloudflare Pages

## Estado

Repositorio inicializado con una base estática deliberadamente simple para iterar rápido sobre:

- información
- narrativa
- visualización
- distribución
