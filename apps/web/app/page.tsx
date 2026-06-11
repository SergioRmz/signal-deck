import { ArrowRight, Orbit, Sparkles, Telescope } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { type CompositionModule, loadBriefing, loadComposition } from '@/lib/data';

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

export default async function HomePage() {
  const [briefing, composition] = await Promise.all([loadBriefing(), loadComposition()]);
  const heroModule = composition.modules?.find((module) => module.moduleId === 'mod-hero');
  const topLineModule = composition.modules?.find((module) => module.moduleId === 'mod-topline');
  const radarModule = composition.modules?.find((module) => module.moduleId === 'mod-radar');
  const deepDivesModule = composition.modules?.find((module) => module.moduleId === 'mod-deep-dives');
  const radarItems = briefing.radar?.items || [];
  const deepDiveItems = briefing.deepDives?.items || [];

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-8 px-6 py-8 md:px-10 lg:px-12">
      <section className="grid gap-6 lg:grid-cols-[1.5fr_0.8fr]">
        <Card className="overflow-hidden bg-signal-grid">
          <CardHeader className="gap-5">
            <div className="flex flex-wrap items-center gap-3">
              <Badge>signal-deck / next foundation</Badge>
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
              <p className="max-w-3xl text-base leading-8 text-muted-foreground md:text-lg">
                {briefing.hero.lede}
              </p>
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
            <CardDescription>Reader context</CardDescription>
            <CardTitle className="text-2xl">Who this edition is trying to upgrade</CardTitle>
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
              <p className="mb-2 text-xs uppercase tracking-[0.18em] text-foreground/60">Interests</p>
              <div className="flex flex-wrap gap-2">
                {briefing.meta.readerContext?.interests?.map((interest) => (
                  <Badge key={interest}>{interest}</Badge>
                ))}
              </div>
            </div>
            <div className="rounded-2xl border border-border/80 bg-background/40 p-4 leading-7 text-foreground/85">
              {briefing.meta.readerContext?.desiredUpgrade}
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
            <CardDescription>Composition signal</CardDescription>
            <CardTitle className="text-2xl">What this foundation already externalizes</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-2xl border border-border/80 bg-background/40 p-4">
              <p className="mb-2 text-xs uppercase tracking-[0.18em] text-muted-foreground">Engagement goal</p>
              <p className="text-sm leading-7 text-foreground/85">{composition.experience?.engagementGoal}</p>
            </div>
            <ul className="space-y-3">
              {(composition.page?.moduleOrder || []).slice(0, 6).map((moduleId) => (
                <li
                  key={moduleId}
                  className="flex items-center justify-between rounded-2xl border border-border/70 bg-background/35 px-4 py-3 text-sm text-muted-foreground"
                >
                  <span>{moduleId}</span>
                  <ArrowRight className="h-4 w-4 text-primary" />
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </section>

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
            <CardDescription>Reading cue</CardDescription>
            <CardTitle className="text-2xl">Why the radar exists at this point in the page</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm text-muted-foreground">
            <p className="leading-7 text-foreground/85">
              The composition wants the reader to test the thesis quickly before committing to the heavier argument.
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
              <p className="mb-2 text-xs uppercase tracking-[0.18em] text-accent-foreground/70">Migration status</p>
              <p className="leading-7 text-foreground">
                Radar is now rendered from the real briefing payload instead of staying implicit in the composition sample.
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
            <p className="max-w-3xl text-base leading-8 text-muted-foreground md:text-lg">
              {deepDivesModule?.interactionCue}
            </p>
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
                      <p className="mb-2 text-xs uppercase tracking-[0.18em] text-muted-foreground">Why it matters</p>
                      <p>{item.explanation}</p>
                    </div>
                  ) : null}
                  <p>{item.body}</p>
                </div>
                {item.implication ? (
                  <div className="rounded-2xl border border-accent/25 bg-accent/10 p-4">
                    <p className="mb-2 text-xs uppercase tracking-[0.18em] text-accent-foreground/75">Implication</p>
                    <p className="text-sm leading-7 text-foreground">{item.implication}</p>
                  </div>
                ) : null}
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </main>
  );
}
