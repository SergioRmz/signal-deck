# Architecture

## Objetivo de esta fase

Separar con claridad tres capas para no mezclar producto, contenido y despliegue desde el día uno.

## Capas

### 1. Contenido / inteligencia editorial
Responsable de:

- recibir insumos
- priorizar señales
- construir tesis
- producir artefactos estructurados

En una fase posterior, esta capa puede emitir JSON, Markdown o ambos.

En esta base inicial, el contrato entre contenido y presentación es un archivo JSON local:

- `apps/briefing-page/data/briefing.sample.json`

### 2. Presentación
Responsable de:

- renderizar el briefing como single page
- mantener un diseño sobrio y legible
- transformar artefactos estructurados en una lectura premium

En esta base inicial, la presentación es una página estática hecha con HTML/CSS/JS sin framework.

### 3. Distribución
Responsable de:

- publicar externamente
- versionar entregas
- enlazar desde Telegram u otros canales

Cloudflare Pages encaja bien aquí por simplicidad, costo y mantenimiento.

## Decisión técnica inicial

Para la primera iteración usamos una página estática porque:

- reduce complejidad innecesaria
- acelera el feedback editorial
- evita decidir demasiado pronto un framework
- deja abierta la migración futura a un renderer más sofisticado

## Evolución prevista

### Fase 1
- página estática de referencia
- contenido mock
- deploy simple

### Fase 2
- esquema de datos estable para el briefing
- generación automática de contenido intermedio
- inyección de contenido real en la página

### Fase 3
- histórico de briefings
- vistas temáticas
- métricas de lectura o navegación

## Carpetas

- `apps/briefing-page/`: artefacto visual principal
- `docs/`: decisiones, visión y operación

## Convención

El repo debe privilegiar:

- nombres obvios
- pocos niveles de anidación
- separación clara entre contenido, app y despliegue
