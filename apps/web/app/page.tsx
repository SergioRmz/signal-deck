import { ArrowRight, Sparkles } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { loadBriefing, loadComposition } from '@/lib/data';

function moduleHeadline(kind: string, fallback: string, compositionHeadline?: string) {
  return compositionHeadline || fallback || kind;
}

export default async function HomePage() {
  const [briefing, composition] = await Promise.all([loadBriefing(), loadComposition()]);
  const heroModule = composition.modules?.find((module) => module.moduleId === 'mod-hero');
  const topLineModule = composition.modules?.find((module) => module.moduleId === 'mod-topline');

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
                  <Badge key={role} variant="muted">{role}</Badge>
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
              {(composition.page?.moduleOrder || []).slice(0, 4).map((moduleId) => (
                <li key={moduleId} className="flex items-center justify-between rounded-2xl border border-border/70 bg-background/35 px-4 py-3 text-sm text-muted-foreground">
                  <span>{moduleId}</span>
                  <ArrowRight className="h-4 w-4 text-primary" />
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </section>
    </main>
  );
}
