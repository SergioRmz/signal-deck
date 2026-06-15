import { type ReactElement, useEffect, useMemo, useState } from 'react';
import {
  ArrowRight,
  BrainCircuit,
  Compass,
  Crosshair,
  Eye,
  GitBranch,
  Layers3,
  Orbit,
  Radar,
  Route,
  Sparkles,
  Telescope,
  Users2,
  Zap,
} from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { type BriefingData, type CompositionModule, type VisualComposition, loadBriefing, loadComposition } from '@/lib/data';

type RendererState =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'ready'; briefing: BriefingData; composition: VisualComposition };

type BriefingContext = {
  briefing: BriefingData;
  composition: VisualComposition;
  modulesById: Map<string, CompositionModule>;
  heroModule?: CompositionModule;
  topLineModule?: CompositionModule;
  readerTranslationModule?: CompositionModule;
  radarModule?: CompositionModule;
  deepDivesModule?: CompositionModule;
  marketMapModule?: CompositionModule;
  reusableLessonModule?: CompositionModule;
  watchlistModule?: CompositionModule;
  moduleOrder: string[];
  readerUpgrade: string;
};

type ModuleRenderer = (context: BriefingContext) => ReactElement | null;

const MODULE_FALLBACKS: Record<string, string> = {
  'mod-hero': 'Tesis central',
  'mod-topline': 'Núcleo estratégico',
  'mod-reader-translation': 'Traducción por rol',
  'mod-radar': 'Radar de evidencia',
  'mod-deep-dives': 'Laboratorio de mecanismos',
  'mod-market-map': 'Mapa de poder',
  'mod-reusable-lesson': 'Lección reutilizable',
  'mod-watchlist': 'Sensores próximos',
};

function moduleHeadline(kind: string, fallback: string, compositionHeadline?: string) {
  void kind;
  void compositionHeadline;
  return fallback;
}

const LABELS_ES: Record<string, string> = {
  'software-engineer': 'Ingeniería de software',
  founder: 'Fundador',
  operator: 'Operaciones',
  operador: 'Operaciones',
  'supports-thesis': 'apoya la tesis',
  'complicates-thesis': 'matiza la tesis',
  monitor: 'vigilar',
  primary: 'principal',
  secondary: 'secundario',
  supporting: 'soporte',
  accent: 'acento',
  contrast: 'contraste',
  heat: 'tensión',
  base: 'base',
  'role-translation-grid': 'lentes por rol',
  'signal-ribbons': 'cintas de señal',
  'collectible-triptych': 'tríptico de mecanismos',
  'pressure-ladder': 'escalera de presión',
  'pattern-lift': 'patrón reutilizable',
  'question-steps': 'preguntas activas',
  question: 'pregunta',
  distribution: 'Distribución',
  workflow: 'Flujo de trabajo',
  product: 'Producto',
  editor: 'Editor estratégico',
  'editor estratégico': 'Editor estratégico',
  builder: 'Constructor',
  constructor: 'Constructor',
  learner: 'Aprendiz ejecutivo',
  'executive learner': 'Aprendiz ejecutivo',
  'aprendiz ejecutivo': 'Aprendiz ejecutivo',
  electric: 'eléctrico',
  'dark editorial': 'editorial oscuro',
};

function toSpanishLabel(value?: string) {
  if (!value) {
    return '';
  }

  return LABELS_ES[value.toLowerCase()] || value.replaceAll('-', ' ');
}

function roleLabel(role?: string) {
  return toSpanishLabel(role) || 'señal';
}

function moduleMeta(module?: CompositionModule) {
  void module;
  return [];
}

function topLineGuidance(briefing: BriefingData) {
  return briefing.topLine.stakes || briefing.hero.promise || 'Primero entiende el cambio estructural; después juzga la evidencia.';
}

function radarGuidance(briefing: BriefingData) {
  const monitor = briefing.radar?.items.find((item) => item.role === 'monitor')?.text;
  return monitor || 'Lee cada señal como una prueba de la tesis, no como una tarjeta suelta.';
}

function deepDiveGuidance(briefing: BriefingData) {
  const first = briefing.deepDives?.items[0];
  return first?.implication || 'Compara los mecanismos: ahí se ve quién captura margen, poder y distribución.';
}

function readerLensGuidance(readerUpgrade: string) {
  return readerUpgrade || 'Ubica qué decisión cambia para cada rol antes de entrar al detalle técnico.';
}

function watchlistGuidance(briefing: BriefingData) {
  return briefing.watchlist?.items[0]?.text || 'Cierra con las preguntas que separan una tesis útil de una narrativa cómoda.';
}

function watchTypeLabel(type?: string) {
  return toSpanishLabel(type) || 'vigilar';
}

function splitSignalText(value?: string) {
  if (!value) {
    return [];
  }

  return value
    .split(/(?<=[.!?])\s+/)
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, 3);
}

function moduleLabel(moduleId: string, module?: CompositionModule) {
  void module;
  return MODULE_FALLBACKS[moduleId] || moduleId.replace('mod-', '').replaceAll('-', ' ');
}

function LoadingState() {
  return (
    <main className="editorial-shell flex min-h-screen items-center justify-center px-6 py-20">
      <Card className="canvas-card w-full max-w-2xl">
        <CardHeader className="gap-4">
          <div className="flex flex-wrap items-center gap-3">
            <Badge>signal-deck</Badge>
            <Badge variant="accent">cargando</Badge>
          </div>
          <CardTitle className="display-title text-4xl md:text-6xl">Preparando la edición</CardTitle>
          <CardDescription className="max-w-xl text-base leading-8 text-muted-foreground">
            Estamos montando la composición editorial, no solo cargando texto.
          </CardDescription>
        </CardHeader>
      </Card>
    </main>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <main className="editorial-shell flex min-h-screen items-center justify-center px-6 py-20">
      <Card className="canvas-card w-full max-w-2xl border-accent/30">
        <CardHeader className="gap-4">
          <div className="flex flex-wrap items-center gap-3">
            <Badge>signal-deck</Badge>
            <Badge variant="accent">error de carga</Badge>
          </div>
          <CardTitle className="display-title text-4xl md:text-6xl">No se pudo cargar la edición</CardTitle>
          <CardDescription className="max-w-xl text-base leading-8 text-muted-foreground">
            Verifica que el paso de sincronización haya copiado los archivos JSON a <code>public/data</code> antes de desplegar.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-2xl border border-border/80 bg-background/40 p-4 font-mono text-sm leading-7 text-foreground/90">
            {message}
          </div>
        </CardContent>
      </Card>
    </main>
  );
}

function ThesisHero({ briefing, composition, heroModule, topLineModule, readerUpgrade }: BriefingContext) {
  const thesisFragments = splitSignalText(briefing.hero.thesis || briefing.topLine.body);

  return (
    <section className="hero-stage" data-module-id="mod-hero">
      <div className="hero-copy">
        <div className="flex flex-wrap items-center gap-3">
          <Badge>signal-deck</Badge>
          <Badge variant="muted">{briefing.meta.editionDate}</Badge>
          <Badge variant="accent">{toSpanishLabel(composition.experience?.visualTone || 'dark editorial')}</Badge>
        </div>
        <p className="eyebrow mt-8">{moduleHeadline('hero', 'Tesis de apertura', heroModule?.headline)}</p>
        <h1 className="hero-title">{briefing.hero.title}</h1>
        <p className="hero-lede">{briefing.hero.lede}</p>
      </div>

      <aside className="thesis-instrument" aria-label="Instrumento editorial de la tesis">
        <div className="instrument-orbit">
          <span />
          <span />
          <span />
        </div>
        <p className="eyebrow">Núcleo de lectura</p>
        <h2>{briefing.topLine.title}</h2>
        <p>{briefing.topLine.stakes || readerUpgrade}</p>
        <div className="instrument-metrics">
          <div>
            <strong>{briefing.radar?.items.length || 0}</strong>
            <span>señales</span>
          </div>
          <div>
            <strong>{briefing.deepDives?.items.length || 0}</strong>
            <span>mecanismos</span>
          </div>
          <div>
            <strong>{briefing.watchlist?.items.length || 0}</strong>
            <span>sensores</span>
          </div>
        </div>
      </aside>

      <div className="hero-briefing-strip">
        {(thesisFragments.length ? thesisFragments : [briefing.hero.signal, briefing.hero.tension, briefing.hero.promise]).filter(Boolean).map((fragment, index) => (
          <article key={`${fragment}-${index}`}>
            <span>0{index + 1}</span>
            <p>{fragment}</p>
          </article>
        ))}
        <article className="strip-emphasis">
          <span>clave</span>
          <p>{topLineGuidance(briefing)}</p>
        </article>
      </div>
    </section>
  );
}

function TopLineSpotlight({ briefing }: BriefingContext) {
  const fragments = splitSignalText(briefing.topLine.body);

  return (
    <section className="reading-path" data-module-id="mod-topline">
      <div>
        <p className="eyebrow">Tesis operativa</p>
        <h2 className="section-title">{briefing.topLine.title}</h2>
        <p className="section-copy">{briefing.topLine.body}</p>
      </div>
      <div className="path-rail" aria-label="Lectura guiada de la tesis">
        {fragments.map((fragment, index) => (
          <article key={`${fragment}-${index}`} className="path-node">
            <span className="path-index">{String(index + 1).padStart(2, '0')}</span>
            <div>
              <strong>{index === 0 ? 'Cambio estructural' : index === 1 ? 'Efecto económico' : 'Pregunta crítica'}</strong>
              <p>{fragment}</p>
            </div>
            <ArrowRight className="h-4 w-4" />
          </article>
        ))}
      </div>
    </section>
  );
}

function ReaderLensLab({ briefing, readerTranslationModule, readerUpgrade }: BriefingContext) {
  const items = briefing.readerTranslation?.items || [];
  if (!items.length) {
    return null;
  }

  return (
    <section className="module-section lens-lab" data-module-id="mod-reader-translation">
      <div className="section-kicker">
        <Users2 className="h-5 w-5" />
        <span>{moduleHeadline('readerTranslation', 'Traducción por rol', readerTranslationModule?.headline)}</span>
      </div>
      <div className="section-heading-row">
        <div>
          <h2 className="section-title">{briefing.readerTranslation?.title || 'Qué cambia para ti'}</h2>
          <p className="section-copy">{readerLensGuidance(readerUpgrade)}</p>
        </div>
        <MetaBadges module={readerTranslationModule} />
      </div>

      <div className="lens-grid">
        {items.map((item, index) => (
          <article key={`${item.role}-${index}`} className="lens-card">
            <div className="lens-card__topline">
              <Badge variant="muted">Rol {index + 1}</Badge>
              <span>{typeof item.weight === 'number' ? `${Math.round(item.weight * 100)}% peso` : 'lente'}</span>
            </div>
            <h3>{roleLabel(item.role)}</h3>
            <strong>{item.headline}</strong>
            <p>{item.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function EvidenceOrbit({ briefing, radarModule }: BriefingContext) {
  const items = briefing.radar?.items || [];
  if (!items.length) {
    return null;
  }

  if (radarModule?.variant === 'signal-ribbons') {
    return (
      <section className="module-section evidence-ribbons" data-module-id="mod-radar">
        <div className="section-kicker">
          <Orbit className="h-5 w-5" />
          <span>{moduleHeadline('radar', 'Radar de evidencia', radarModule?.headline)}</span>
        </div>
        <div className="section-heading-row">
          <div>
            <h2 className="section-title">{briefing.radar?.title || 'Radar de evidencia'}</h2>
            <p className="section-copy">{radarGuidance(briefing)}</p>
          </div>
          <MetaBadges module={radarModule} />
        </div>

        <div className="ribbon-stack" aria-label="Cintas de señal para probar la tesis">
          {items.map((item, index) => (
            <article key={`${item.label}-${item.text}`} className="signal-ribbon">
              <div className="signal-ribbon__rail">
                <span>{String(index + 1).padStart(2, '0')}</span>
                <Badge variant={item.role === 'monitor' ? 'muted' : 'accent'}>{roleLabel(item.role)}</Badge>
              </div>
              <div>
                <h3>{item.label}</h3>
                <p>{item.text}</p>
              </div>
            </article>
          ))}
        </div>
      </section>
    );
  }

  return (
    <section className="module-section evidence-orbit" data-module-id="mod-radar">
      <div className="section-kicker">
        <Orbit className="h-5 w-5" />
        <span>{moduleHeadline('radar', 'Radar de evidencia', radarModule?.headline)}</span>
      </div>
      <div className="section-heading-row">
        <div>
          <h2 className="section-title">{briefing.radar?.title || 'Radar de evidencia'}</h2>
          <p className="section-copy">{radarGuidance(briefing)}</p>
        </div>
        <MetaBadges module={radarModule} />
      </div>

      <div className="orbit-board">
        <div className="orbit-core">
          <Radar className="h-8 w-8" />
          <span>tesis bajo prueba</span>
        </div>
        {items.map((item, index) => (
          <article key={`${item.label}-${item.text}`} className={`orbit-signal orbit-signal-${(index % 6) + 1}`}>
            <Badge variant={item.role === 'monitor' ? 'muted' : 'accent'}>{roleLabel(item.role)}</Badge>
            <h3>{item.label}</h3>
            <p>{item.text}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function MechanismStudio({ briefing, deepDivesModule }: BriefingContext) {
  const items = briefing.deepDives?.items || [];
  if (!items.length) {
    return null;
  }

  return (
    <section className="module-section mechanism-studio" data-module-id="mod-deep-dives">
      <div className="section-kicker">
        <Telescope className="h-5 w-5" />
        <span>{moduleHeadline('deepDive', 'Laboratorio de mecanismos', deepDivesModule?.headline)}</span>
      </div>
      <div className="section-heading-row">
        <div>
          <h2 className="section-title">{briefing.deepDives?.title || 'Laboratorio de mecanismos'}</h2>
          <p className="section-copy">{deepDiveGuidance(briefing)}</p>
        </div>
        <MetaBadges module={deepDivesModule} />
      </div>

      <div className="mechanism-grid">
        {items.map((item, index) => (
          <article key={`${item.title}-${index}`} className="mechanism-card">
            <div className="mechanism-card__index">0{index + 1}</div>
            <div>
              <Badge>{item.mechanism || 'mecanismo'}</Badge>
              <h3>{item.title}</h3>
            </div>
            <div className="mechanism-flow" aria-label="Mapa causal del análisis">
              <div>
                <span>Tesis</span>
                <p>{item.claim || item.title}</p>
              </div>
              <GitBranch className="h-5 w-5" />
              <div>
                <span>Mecanismo</span>
                <p>{item.explanation || item.body}</p>
              </div>
              <Zap className="h-5 w-5" />
              <div>
                <span>Implicación</span>
                <p>{item.implication || item.body}</p>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function PowerMap({ briefing, marketMapModule }: BriefingContext) {
  const items = briefing.marketMap?.items || [];
  if (!items.length) {
    return null;
  }

  if (marketMapModule?.variant === 'pressure-ladder') {
    return (
      <section className="module-section pressure-ladder" data-module-id="mod-market-map">
        <div className="section-kicker">
          <Compass className="h-5 w-5" />
          <span>{moduleHeadline('marketMap', 'Mapa de poder', marketMapModule?.headline)}</span>
        </div>
        <div className="section-heading-row">
          <div>
            <h2 className="section-title">{briefing.marketMap?.title || 'Dónde se mueve la ventaja'}</h2>
            <p className="section-copy">Aquí el formato no es una grilla: es una escalera de presión competitiva.</p>
          </div>
          <MetaBadges module={marketMapModule} />
        </div>

        <div className="ladder-steps" aria-label="Escalera de presión competitiva">
          {items.map((item, index) => (
            <article key={`${item.label}-${index}`} className="ladder-step">
              <span className="ladder-step__index">{String(index + 1).padStart(2, '0')}</span>
              <div>
                <h3>{item.label}</h3>
                <p>{item.text}</p>
                {item.powerShift ? <strong>{item.powerShift}</strong> : null}
              </div>
            </article>
          ))}
        </div>
      </section>
    );
  }

  return (
    <section className="module-section power-map" data-module-id="mod-market-map">
      <div className="section-kicker">
        <Compass className="h-5 w-5" />
        <span>{moduleHeadline('marketMap', 'Mapa de poder', marketMapModule?.headline)}</span>
      </div>
      <div className="section-heading-row">
        <div>
          <h2 className="section-title">{briefing.marketMap?.title || 'Dónde se mueve la ventaja'}</h2>
          <p className="section-copy">No es una lista de actores: es un cambio de palancas, presión y oportunidad.</p>
        </div>
        <MetaBadges module={marketMapModule} />
      </div>

      <div className="power-grid">
        {items.map((item, index) => (
          <article key={`${item.label}-${index}`} className="power-cell">
            <span className="power-cell__axis">Eje {index + 1}</span>
            <h3>{item.label}</h3>
            <p>{item.text}</p>
            {item.powerShift ? <strong>{item.powerShift}</strong> : null}
          </article>
        ))}
      </div>
    </section>
  );
}

function ReusableLesson({ briefing, reusableLessonModule }: BriefingContext) {
  if (!briefing.reusableLesson) {
    return null;
  }

  return (
    <section className="lesson-panel" data-module-id="mod-reusable-lesson">
      <div className="section-kicker">
        <BrainCircuit className="h-5 w-5" />
        <span>{moduleHeadline('reusableLesson', 'Lección reutilizable', reusableLessonModule?.headline)}</span>
      </div>
      <div className="lesson-panel__body">
        <div>
          <h2>{briefing.reusableLesson.title}</h2>
          <p>{briefing.reusableLesson.pattern}</p>
        </div>
        <div className="lesson-panel__rules">
          {(briefing.reusableLesson.applyWhen || []).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
        <strong>{briefing.reusableLesson.takeaway}</strong>
      </div>
    </section>
  );
}

function WatchSensors({ briefing, watchlistModule }: BriefingContext) {
  const items = briefing.watchlist?.items || [];
  if (!items.length) {
    return null;
  }

  return (
    <section className="watch-sensors" data-module-id="mod-watchlist">
      <div>
        <div className="section-kicker">
          <Eye className="h-5 w-5" />
          <span>{moduleHeadline('watchlist', 'Sensores próximos', watchlistModule?.headline)}</span>
        </div>
        <h2 className="section-title">{briefing.watchlist?.title || 'Qué vigilar ahora'}</h2>
      </div>
      <div className="sensor-stack">
        {items.map((item, index) => (
          <article key={`${item.text}-${index}`}>
            <Crosshair className="h-5 w-5" />
            <div>
              <span>{watchTypeLabel(item.type)}</span>
              <p>{item.text}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function MetaBadges({ module }: { module?: CompositionModule }) {
  const items = moduleMeta(module);
  if (!items.length) {
    return null;
  }

  return (
    <div className="meta-badges">
      {items.map((item) => (
        <Badge key={item} variant="muted">
          {item}
        </Badge>
      ))}
    </div>
  );
}

const MODULE_RENDERERS: Record<string, ModuleRenderer> = {
  'mod-topline': TopLineSpotlight,
  'mod-reader-translation': ReaderLensLab,
  'mod-radar': EvidenceOrbit,
  'mod-deep-dives': MechanismStudio,
  'mod-market-map': PowerMap,
  'mod-reusable-lesson': ReusableLesson,
  'mod-watchlist': WatchSensors,
};

export default function App() {
  const [state, setState] = useState<RendererState>({ status: 'loading' });

  useEffect(() => {
    document.title = 'signal-deck';

    let active = true;

    Promise.all([loadBriefing(), loadComposition()])
      .then(([briefing, composition]) => {
        if (!active) {
          return;
        }

        setState({ status: 'ready', briefing, composition });
      })
      .catch((error: unknown) => {
        if (!active) {
          return;
        }

        const message = error instanceof Error ? error.message : 'Unknown renderer error';
        setState({ status: 'error', message });
      });

    return () => {
      active = false;
    };
  }, []);

  const context = useMemo<BriefingContext | null>(() => {
    if (state.status !== 'ready') {
      return null;
    }

    const { briefing, composition } = state;
    const modules = composition.modules || [];
    const modulesById = new Map(modules.map((module) => [module.moduleId, module]));
    const moduleOrder = composition.page?.moduleOrder?.length
      ? composition.page.moduleOrder
      : ['mod-hero', 'mod-topline', 'mod-reader-translation', 'mod-radar', 'mod-deep-dives', 'mod-market-map', 'mod-reusable-lesson', 'mod-watchlist'];
    const readerUpgrade =
      briefing.meta.readerContext?.desiredUpgrade || briefing.readerTranslation?.items?.[0]?.body || briefing.topLine.stakes || briefing.hero.promise || '';

    return {
      briefing,
      composition,
      modulesById,
      heroModule: modulesById.get('mod-hero'),
      topLineModule: modulesById.get('mod-topline'),
      readerTranslationModule: modulesById.get('mod-reader-translation'),
      radarModule: modulesById.get('mod-radar'),
      deepDivesModule: modulesById.get('mod-deep-dives'),
      marketMapModule: modulesById.get('mod-market-map'),
      reusableLessonModule: modulesById.get('mod-reusable-lesson'),
      watchlistModule: modulesById.get('mod-watchlist'),
      moduleOrder,
      readerUpgrade,
    };
  }, [state]);

  if (state.status === 'loading' || !context) {
    return <LoadingState />;
  }

  if (state.status === 'error') {
    return <ErrorState message={state.message} />;
  }

  return (
    <main className="editorial-shell">
      <div className="editorial-chrome" aria-hidden="true" />
      <div className="editorial-container">
        <ThesisHero {...context} />
        {context.moduleOrder
          .filter((moduleId) => moduleId !== 'mod-hero')
          .map((moduleId) => {
            const Renderer = MODULE_RENDERERS[moduleId];
            return Renderer ? <Renderer key={moduleId} {...context} /> : null;
          })}
      </div>
    </main>
  );
}
