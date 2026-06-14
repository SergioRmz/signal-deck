import { useEffect, useMemo, useState } from 'react';
import { ArrowRight, Compass, Orbit, Sparkles, Telescope, Users2 } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { type BriefingData, type CompositionModule, type VisualComposition, loadBriefing, loadComposition } from '@/lib/data';

type RendererState =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'ready'; briefing: BriefingData; composition: VisualComposition };

function moduleHeadline(kind: string, fallback: string, compositionHeadline?: string) {
  return compositionHeadline || fallback || kind;
}

function roleLabel(role?: string) {
  if (!role) {
    return 'signal';
  }

  return role.replaceAll('-', ' ');
}

function moduleMeta(module?: CompositionModule) {
  if (!module) {
    return [];
  }

  return [module.priority, module.variant, module.accentMode].filter(Boolean) as string[];
}

function watchTypeLabel(type?: string) {
  if (!type) {
    return 'watch';
  }

  return type.replaceAll('-', ' ');
}

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

  const derived = useMemo(() => {
    if (state.status !== 'ready') {
      return null;
    }

    const { briefing, composition } = state;

    const heroModule = composition.modules?.find((module) => module.moduleId === 'mod-hero');
    const topLineModule = composition.modules?.find((module) => module.moduleId === 'mod-topline');
    const readerTranslationModule = composition.modules?.find(
      (module) => module.moduleId === 'mod-reader-translation' || module.sourceKey === 'readerTranslation',
    );
    const radarModule = composition.modules?.find((module) => module.moduleId === 'mod-radar');
    const deepDivesModule = composition.modules?.find((module) => module.moduleId === 'mod-deep-dives');
    const marketMapModule = composition.modules?.find((module) => module.moduleId === 'mod-market-map');
    const reusableLessonModule = composition.modules?.find(
      (module) => module.moduleId === 'mod-reusable-lesson' || module.sourceKey === 'reusableLesson',
    );
    const watchlistModule = composition.modules?.find((module) => module.moduleId === 'mod-watchlist');
    const radarItems = briefing.radar?.items || [];
    const deepDiveItems = briefing.deepDives?.items || [];
    const marketMapItems = briefing.marketMap?.items || [];
    const readerTranslationItems = briefing.readerTranslation?.items || [];
    const watchlistItems = briefing.watchlist?.items || [];
    const moduleOrder = composition.page?.moduleOrder || [];
    const readerUpgrade =
      briefing.meta.readerContext?.desiredUpgrade || briefing.readerTranslation?.items?.[0]?.body || briefing.topLine.stakes;

    return {
      briefing,
      composition,
      heroModule,
      topLineModule,
      readerTranslationModule,
      radarModule,
      deepDivesModule,
      marketMapModule,
      reusableLessonModule,
      watchlistModule,
      radarItems,
      deepDiveItems,
      marketMapItems,
      readerTranslationItems,
      watchlistItems,
      moduleOrder,
      readerUpgrade,
    };
  }, [state]);

  if (state.status === 'loading' || !derived) {
    return (
      <main className="mx-auto flex min-h-screen w-full max-w-5xl items-center justify-center px-6 py-20 md:px-10">
        <Card className="w-full max-w-2xl border-primary/25 bg-signal-grid">
          <CardHeader className="gap-4">
            <div className="flex flex-wrap items-center gap-3">
              <Badge>signal-deck</Badge>
              <Badge variant="accent">cargando</Badge>
            </div>
            <CardTitle className="text-3xl md:text-4xl">Preparando la edición</CardTitle>
            <CardDescription className="max-w-xl text-base leading-8 text-muted-foreground">
              Estamos cargando el briefing y su composición visual.
            </CardDescription>
          </CardHeader>
        </Card>
      </main>
    );
  }

  if (state.status === 'error') {
    return (
      <main className="mx-auto flex min-h-screen w-full max-w-5xl items-center justify-center px-6 py-20 md:px-10">
        <Card className="w-full max-w-2xl border-accent/30 bg-accent/5">
          <CardHeader className="gap-4">
            <div className="flex flex-wrap items-center gap-3">
              <Badge>signal-deck</Badge>
              <Badge variant="accent">error de carga</Badge>
            </div>
            <CardTitle className="text-3xl md:text-4xl">No se pudo cargar la edición</CardTitle>
            <CardDescription className="max-w-xl text-base leading-8 text-muted-foreground">
              Verifica que el paso de sincronización haya copiado los archivos JSON a <code>public/data</code> antes de desplegar.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-2xl border border-border/80 bg-background/40 p-4 font-mono text-sm leading-7 text-foreground/90">
              {state.message}
            </div>
          </CardContent>
        </Card>
      </main>
    );
  }

  const {
    briefing,
    composition,
    heroModule,
    topLineModule,
    readerTranslationModule,
    radarModule,
    deepDivesModule,
    marketMapModule,
    reusableLessonModule,
    watchlistModule,
    radarItems,
    deepDiveItems,
    marketMapItems,
    readerTranslationItems,
    watchlistItems,
    moduleOrder,
    readerUpgrade,
  } = derived;

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-8 px-6 py-8 md:px-10 lg:px-12">
      <section className="grid gap-6 lg:grid-cols-[1.5fr_0.8fr]">
        <Card className="overflow-hidden bg-signal-grid">
          <CardHeader className="gap-5">
            <div className="flex flex-wrap items-center gap-3">
              <Badge>signal-deck</Badge>
              <Badge variant="muted">{briefing.meta.editionDate}</Badge>
              <Badge variant="accent">{composition.experience?.visualTone || 'dark tone'}</Badge>
            </div>
            <div className="space-y-4">
              <CardDescription className="max-w-2xl text-sm uppercase tracking-[0.22em] text-primary/80">
                {moduleHeadline('hero', 'Opening thesis', heroModule?.headline)}
              </CardDescription>
              <CardTitle className="max-w-4xl text-4xl font-semibold leading-tight md:text-6xl">
                {briefing.hero.title}
              </CardTitle>
              <p className="max-w-3xl text-base leading-8 text-muted-foreground md:text-lg">{briefing.hero.lede}</p>
            </div>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-2xl border border-primary/15 bg-background/30 p-4">
              <p className="mb-2 text-xs uppercase tracking-[0.18em] text-muted-foreground">Signal</p>
              <p className="text-sm leading-6 text-foreground/90">{briefing.hero.signal}</p>
            </div>
            <div className="rounded-2xl border border-primary/15 bg-background/30 p-4">
              <p className="mb-2 text-xs uppercase tracking-[0.18em] text-muted-foreground">Thesis</p>
              <p className="text-sm leading-6 text-foreground/90">{briefing.hero.thesis}</p>
            </div>
            <div className="rounded-2xl border border-primary/15 bg-background/30 p-4">
              <p className="mb-2 text-xs uppercase tracking-[0.18em] text-muted-foreground">Tension</p>
              <p className="text-sm leading-6 text-foreground/90">{briefing.hero.tension}</p>
            </div>
            <div className="rounded-2xl border border-primary/15 bg-background/30 p-4">
              <p className="mb-2 text-xs uppercase tracking-[0.18em] text-muted-foreground">Promise</p>
              <p className="text-sm leading-6 text-foreground/90">{briefing.hero.promise}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardDescription>Contexto del lector</CardDescription>
            <CardTitle className="text-2xl">Para quién está diseñada esta edición</CardTitle>
          </CardHeader>
          <CardContent className="space-y-5 text-sm text-muted-foreground">
            <div>
              <p className="mb-2 text-xs uppercase tracking-[0.18em] text-foreground/60">Roles</p>
              <div className="flex flex-wrap gap-2">
                {briefing.meta.readerContext?.roles?.map((role) => (
                  <Badge key={role} variant="muted">
                    {role}
                  </Badge>
                ))}
              </div>
            </div>
            <div>
              <p className="mb-2 text-xs uppercase tracking-[0.18em] text-foreground/60">Intereses</p>
              <div className="flex flex-wrap gap-2">
                {briefing.meta.readerContext?.interests?.map((interest) => (
                  <Badge key={interest}>{interest}</Badge>
                ))}
              </div>
            </div>
            <div className="rounded-2xl border border-border/80 bg-background/40 p-4 leading-7 text-foreground/85">
              {readerUpgrade}
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between gap-4">
              <div>
                <CardDescription>{moduleHeadline('topLine', 'Top line', topLineModule?.headline)}</CardDescription>
                <CardTitle className="mt-2 text-3xl leading-tight md:text-4xl">{briefing.topLine.title}</CardTitle>
              </div>
              <Sparkles className="mt-1 h-6 w-6 text-primary" />
            </div>
          </CardHeader>
          <CardContent className="space-y-5">
            <p className="max-w-3xl text-base leading-8 text-muted-foreground md:text-lg">{briefing.topLine.body}</p>
            <div className="rounded-2xl border border-accent/20 bg-accent/10 p-5">
              <p className="mb-2 text-xs uppercase tracking-[0.18em] text-accent-foreground/70">Strategic stakes</p>
              <p className="text-base leading-7 text-foreground">{briefing.topLine.stakes}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardDescription>Ruta editorial</CardDescription>
            <CardTitle className="text-2xl">Cómo conviene leer esta edición</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-2xl border border-border/80 bg-background/40 p-4">
              <p className="mb-2 text-xs uppercase tracking-[0.18em] text-muted-foreground">Objetivo de lectura</p>
              <p className="text-sm leading-7 text-foreground/85">{composition.experience?.engagementGoal}</p>
            </div>
            <ul className="space-y-3">
              {moduleOrder.slice(0, 8).map((moduleId) => (
                <li
                  key={moduleId}
                  className="flex items-center justify-between rounded-2xl border border-border/70 bg-background/35 px-4 py-3 text-sm text-muted-foreground"
                >
                  <span>{moduleId.replace('mod-', '').replaceAll('-', ' ')}</span>
                  <ArrowRight className="h-4 w-4 text-primary" />
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </section>

      {readerTranslationItems.length ? (
        <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
          <Card className="overflow-hidden border-accent/20 bg-[linear-gradient(180deg,rgba(12,26,47,0.95),rgba(7,17,31,0.98))]">
            <CardHeader className="gap-4 border-b border-border/60 pb-5">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <CardDescription className="flex items-center gap-2 text-primary/80">
                    <Users2 className="h-4 w-4" />
                    {moduleHeadline('readerTranslation', 'Reader translation', readerTranslationModule?.headline)}
                  </CardDescription>
                  <CardTitle className="mt-2 text-3xl md:text-4xl">
                    {briefing.readerTranslation?.title || 'What this changes for you'}
                  </CardTitle>
                </div>
                <div className="flex flex-wrap justify-end gap-2">
                  {moduleMeta(readerTranslationModule).map((item) => (
                    <Badge key={item} variant="accent">
                      {item}
                    </Badge>
                  ))}
                </div>
              </div>
              <p className="max-w-3xl text-sm leading-7 text-muted-foreground">{readerTranslationModule?.interactionCue}</p>
            </CardHeader>
            <CardContent className="grid gap-4 pt-6 md:grid-cols-2 xl:grid-cols-3">
              {readerTranslationItems.map((item, index) => (
                <Card
                  key={`${item.role}-${index}`}
                  className="border-accent/20 bg-background/45 shadow-[0_18px_48px_rgba(9,19,37,0.24)]"
                >
                  <CardHeader className="gap-3 border-b border-border/60 pb-4">
                    <div className="flex items-center justify-between gap-3">
                      <Badge variant="muted">Role {index + 1}</Badge>
                      <Badge>{roleLabel(item.role)}</Badge>
                    </div>
                    <CardTitle className="text-2xl leading-tight">{item.headline}</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4 pt-5">
                    <p className="text-sm leading-7 text-foreground/90">{item.body}</p>
                    {typeof item.weight === 'number' ? (
                      <div className="rounded-2xl border border-accent/20 bg-accent/10 px-4 py-3 text-sm text-foreground">
                        <p className="text-xs uppercase tracking-[0.18em] text-accent-foreground/75">Priority weight</p>
                        <p className="mt-1 leading-7">{item.weight}</p>
                      </div>
                    ) : null}
                  </CardContent>
                </Card>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardDescription>Por qué aparece aquí</CardDescription>
              <CardTitle className="text-2xl">La tesis cambia según tu rol operativo</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-muted-foreground">
              <p className="leading-7 text-foreground/85">
                Esta sección convierte la tesis en decisiones prácticas para cada rol antes de entrar al bloque de evidencia.
              </p>
              <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
                <p className="mb-2 text-xs uppercase tracking-[0.18em] text-foreground/60">Layout hints</p>
                <div className="flex flex-wrap gap-2">
                  {(readerTranslationModule?.layoutHints || []).map((hint) => (
                    <Badge key={hint} variant="muted">
                      {hint}
                    </Badge>
                  ))}
                </div>
              </div>
              <div className="rounded-2xl border border-accent/20 bg-accent/10 p-4">
                <p className="mb-2 text-xs uppercase tracking-[0.18em] text-accent-foreground/70">Uso práctico</p>
                <p className="leading-7 text-foreground">
                  Lee primero tu rol dominante y luego contrástalo con el resto: la ventaja aparece en los cruces, no en una sola etiqueta.
                </p>
              </div>
            </CardContent>
          </Card>
        </section>
      ) : null}

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <Card className="overflow-hidden border-primary/20 bg-primary/5">
          <CardHeader className="gap-4 border-b border-border/60 pb-5">
            <div className="flex items-center justify-between gap-4">
              <div>
                <CardDescription className="flex items-center gap-2 text-primary/80">
                  <Orbit className="h-4 w-4" />
                  {moduleHeadline('radar', 'Radar', radarModule?.headline)}
                </CardDescription>
                <CardTitle className="mt-2 text-3xl md:text-4xl">{briefing.radar?.title || 'Evidence radar'}</CardTitle>
              </div>
              <div className="flex flex-wrap justify-end gap-2">
                {moduleMeta(radarModule).map((item) => (
                  <Badge key={item} variant="muted">
                    {item}
                  </Badge>
                ))}
              </div>
            </div>
            <p className="max-w-3xl text-sm leading-7 text-muted-foreground">{radarModule?.interactionCue}</p>
          </CardHeader>
          <CardContent className="grid gap-4 pt-6 md:grid-cols-3">
            {radarItems.map((item) => (
              <article
                key={`${item.label}-${item.text}`}
                className="rounded-3xl border border-primary/20 bg-background/55 p-5 shadow-[0_20px_60px_rgba(19,33,64,0.24)]"
              >
                <div className="mb-4 flex items-center justify-between gap-3">
                  <Badge>{item.label}</Badge>
                  <Badge variant={item.role === 'monitor' ? 'muted' : 'accent'}>{roleLabel(item.role)}</Badge>
                </div>
                <p className="text-base leading-7 text-foreground/90">{item.text}</p>
              </article>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardDescription>Clave de lectura</CardDescription>
            <CardTitle className="text-2xl">Por qué este radar va antes del análisis largo</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm text-muted-foreground">
            <p className="leading-7 text-foreground/85">
              El radar te deja probar la tesis contra varias señales antes de invertir atención en el análisis de mecanismos.
            </p>
            <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
              <p className="mb-2 text-xs uppercase tracking-[0.18em] text-foreground/60">Layout hints</p>
              <div className="flex flex-wrap gap-2">
                {(radarModule?.layoutHints || []).map((hint) => (
                  <Badge key={hint} variant="muted">
                    {hint}
                  </Badge>
                ))}
              </div>
            </div>
            <div className="rounded-2xl border border-accent/20 bg-accent/10 p-4">
              <p className="mb-2 text-xs uppercase tracking-[0.18em] text-accent-foreground/70">Uso práctico</p>
              <p className="leading-7 text-foreground">
              Si una señal no sostiene la tesis, esa tensión debe subir de peso en la lectura, no esconderse como excepción.
              </p>
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="space-y-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="space-y-3">
            <CardDescription className="flex items-center gap-2 text-primary/80">
              <Telescope className="h-4 w-4" />
              {moduleHeadline('deepDive', 'Deep dives', deepDivesModule?.headline)}
            </CardDescription>
            <h2 className="text-3xl font-semibold leading-tight text-foreground md:text-5xl">
              {briefing.deepDives?.title || 'Mechanism breakdown'}
            </h2>
            <p className="max-w-3xl text-base leading-8 text-muted-foreground md:text-lg">{deepDivesModule?.interactionCue}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {moduleMeta(deepDivesModule).map((item) => (
              <Badge key={item} variant="accent">
                {item}
              </Badge>
            ))}
          </div>
        </div>

        <div className="grid gap-5 xl:grid-cols-3">
          {deepDiveItems.map((item, index) => (
            <Card
              key={`${item.title}-${index}`}
              className="group relative overflow-hidden border-primary/15 bg-[linear-gradient(180deg,rgba(15,29,51,0.96),rgba(7,17,31,0.92))]"
            >
              <CardHeader className="gap-4 border-b border-border/60 pb-5">
                <div className="flex items-center justify-between gap-3">
                  <Badge variant="muted">Deep dive {index + 1}</Badge>
                  {item.mechanism ? <Badge>{item.mechanism}</Badge> : null}
                </div>
                <CardTitle className="text-2xl leading-tight">{item.title}</CardTitle>
                <CardDescription className="text-sm leading-7 text-muted-foreground">
                  {item.claim || item.explanation || item.body}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-5 pt-6">
                <div className="space-y-3 text-sm leading-7 text-foreground/85">
                  {item.explanation ? (
                    <div className="rounded-2xl border border-border/70 bg-background/35 p-4">
                      <p className="mb-2 text-xs uppercase tracking-[0.18em] text-muted-foreground">Mecanismo</p>
                      <p>{item.explanation}</p>
                    </div>
                  ) : null}
                  <p>{item.body}</p>
                </div>
                {item.implication ? (
                  <div className="rounded-2xl border border-accent/25 bg-accent/10 p-4">
                    <p className="mb-2 text-xs uppercase tracking-[0.18em] text-accent-foreground/75">Implicación</p>
                    <p className="text-sm leading-7 text-foreground">{item.implication}</p>
                  </div>
                ) : null}
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <Card className="overflow-hidden border-primary/20 bg-[linear-gradient(180deg,rgba(15,29,51,0.92),rgba(9,17,31,0.98))]">
          <CardHeader className="gap-4 border-b border-border/60 pb-5">
            <div className="flex items-center justify-between gap-4">
              <div>
                <CardDescription className="flex items-center gap-2 text-primary/80">
                  <Compass className="h-4 w-4" />
                  {moduleHeadline('marketMap', 'Market map', marketMapModule?.headline)}
                </CardDescription>
                <CardTitle className="mt-2 text-3xl md:text-4xl">{briefing.marketMap?.title || 'Where leverage is moving'}</CardTitle>
              </div>
              <div className="flex flex-wrap justify-end gap-2">
                {moduleMeta(marketMapModule).map((item) => (
                  <Badge key={item} variant="accent">
                    {item}
                  </Badge>
                ))}
              </div>
            </div>
            <p className="max-w-3xl text-sm leading-7 text-muted-foreground">{marketMapModule?.interactionCue}</p>
          </CardHeader>
          <CardContent className="grid gap-4 pt-6">
            {marketMapItems.map((item) => (
              <article
                key={`${item.label}-${item.text}`}
                className="rounded-3xl border border-primary/15 bg-background/45 p-5 shadow-[0_18px_60px_rgba(9,19,37,0.26)]"
              >
                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div className="space-y-3">
                    <Badge>{item.label}</Badge>
                    <p className="max-w-2xl text-base leading-7 text-foreground/90">{item.text}</p>
                  </div>
                  {item.powerShift ? (
                    <div className="max-w-sm rounded-2xl border border-accent/25 bg-accent/10 p-4 text-sm leading-7 text-foreground">
                      <p className="mb-2 text-xs uppercase tracking-[0.18em] text-accent-foreground/75">Cambio de poder</p>
                      <p>{item.powerShift}</p>
                    </div>
                  ) : null}
                </div>
              </article>
            ))}
          </CardContent>
        </Card>

        <div className="grid gap-6">
          {briefing.reusableLesson ? (
            <Card className="overflow-hidden border-accent/30 bg-accent/5">
              <CardHeader className="gap-4 border-b border-border/60 pb-5">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <CardDescription>{moduleHeadline('reusableLesson', 'Reusable lesson', reusableLessonModule?.headline)}</CardDescription>
                    <CardTitle className="mt-2 text-2xl leading-tight md:text-3xl">{briefing.reusableLesson.title}</CardTitle>
                  </div>
                  <div className="flex flex-wrap justify-end gap-2">
                    {moduleMeta(reusableLessonModule).map((item) => (
                      <Badge key={item} variant="muted">
                        {item}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-5 pt-6">
                <div className="rounded-2xl border border-border/70 bg-background/35 p-4">
                  <p className="mb-2 text-xs uppercase tracking-[0.18em] text-muted-foreground">Pattern</p>
                  <p className="text-sm leading-7 text-foreground/90">{briefing.reusableLesson.pattern}</p>
                </div>
                <div className="rounded-2xl border border-accent/25 bg-accent/10 p-4">
                  <p className="mb-2 text-xs uppercase tracking-[0.18em] text-accent-foreground/75">Takeaway</p>
                  <p className="text-sm leading-7 text-foreground">{briefing.reusableLesson.takeaway}</p>
                </div>
                {briefing.reusableLesson.applyWhen?.length ? (
                  <div>
                    <p className="mb-3 text-xs uppercase tracking-[0.18em] text-foreground/60">Apply when</p>
                    <div className="flex flex-wrap gap-2">
                      {briefing.reusableLesson.applyWhen.map((item) => (
                        <Badge key={item} variant="accent">
                          {item}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ) : null}
              </CardContent>
            </Card>
          ) : null}

          <Card>
            <CardHeader>
              <CardDescription>Cierre operativo</CardDescription>
              <CardTitle className="text-2xl">Cómo convertir el análisis en postura</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-muted-foreground">
              <p className="leading-7 text-foreground/85">
                El mapa de poder traduce la tesis en posicionamiento; la lección reutilizable y la vigilancia la convierten en una forma repetible de leer el mercado.
              </p>
              <div className="rounded-2xl border border-border/70 bg-background/40 p-4">
                <p className="mb-2 text-xs uppercase tracking-[0.18em] text-foreground/60">Layout hints</p>
                <div className="flex flex-wrap gap-2">
                  {[...(marketMapModule?.layoutHints || []), ...(watchlistModule?.layoutHints || [])].map((hint) => (
                    <Badge key={hint} variant="muted">
                      {hint}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      <section className="space-y-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="space-y-3">
            <CardDescription>{moduleHeadline('watchlist', 'Watchlist', watchlistModule?.headline)}</CardDescription>
            <h2 className="text-3xl font-semibold leading-tight text-foreground md:text-5xl">
              {briefing.watchlist?.title || 'Watch framework'}
            </h2>
            <p className="max-w-3xl text-base leading-8 text-muted-foreground md:text-lg">{watchlistModule?.interactionCue}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {moduleMeta(watchlistModule).map((item) => (
              <Badge key={item}>{item}</Badge>
            ))}
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {watchlistItems.map((item, index) => (
            <Card key={`${item.text}-${index}`} className="border-border/80 bg-background/45">
              <CardHeader className="gap-3 border-b border-border/60 pb-4">
                <div className="flex items-center justify-between gap-3">
                  <Badge variant="muted">Pregunta {index + 1}</Badge>
                  <Badge variant={item.type === 'metric' ? 'accent' : 'muted'}>{watchTypeLabel(item.type)}</Badge>
                </div>
              </CardHeader>
              <CardContent className="pt-5">
                <p className="text-sm leading-7 text-foreground/90">{item.text}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </main>
  );
}
