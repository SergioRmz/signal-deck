import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';

const briefingFixture = {
  meta: { editionDate: '2026-06-11' },
  hero: {
    title: 'The strategic fight is shifting from who has the best model to who owns the workflow around it.',
    lede: 'Assess where strategic value is concentrating as model quality converges.'
  },
  topLine: {
    title: 'Distribution is becoming as important as the model.',
    body: 'Own the workflow, own the margin.'
  },
  radar: {
    title: 'Radar',
    items: [
      { label: 'Distribution', text: 'Distribution is carrying more strategic weight.' },
      { label: 'Workflow', text: 'Context capture is emerging as the scarcer asset.' }
    ]
  },
  deepDives: {
    title: '3 angles for reading the shift',
    items: [
      { title: '1. Distribution', body: 'Distribution compounds technical capability.' },
      { title: '2. Context', body: 'Memory and workflow embedding can become part of the moat.' },
      { title: '3. Interface', body: 'UI decisions can determine where strategic capture lands.' }
    ]
  },
  marketMap: {
    title: 'Who benefits if this thesis is right',
    items: [
      { label: 'Winners', text: 'Platforms and products that own distribution.' },
      { label: 'Pressured', text: 'Vendors that sell raw access alone.' }
    ]
  },
  watchlist: {
    title: 'What to watch',
    items: [
      { text: 'Which layer captures the recurring user relationship?' },
      { text: 'Where will the most valuable non-portable context accumulate?' }
    ]
  }
};

const compositionFixture = {
  experience: {
    visualTone: 'electric',
    readingMode: 'mixed',
    engagementGoal: 'Make the briefing feel like a strategic object you want to explore.',
    interactionModel: 'layered',
    hooks: [
      'Land with a large thesis wall that instantly frames the edition.'
    ],
    learningPrompts: [
      'Touch the thesis first, then test it against the radar.'
    ]
  },
  page: {
    heroVariant: 'thesis-wall',
    moduleOrder: [
      'mod-hero',
      'mod-topline',
      'mod-radar',
      'mod-deep-dives',
      'mod-market-map',
      'mod-watchlist'
    ],
    stickyElements: ['edition-date', 'reading-progress'],
    scrollMood: 'punctuated',
    rhythm: 'staged',
    emphasis: 'topline'
  },
  modules: [
    {
      moduleId: 'mod-hero',
      kind: 'hero',
      variant: 'thesis-wall-glow',
      sourceKey: 'hero',
      priority: 'primary',
      headline: 'Own the workflow, own the margin.',
      layoutHints: ['oversized-headline', 'offset-meta-panel', 'accent-halo'],
      interactionCue: 'Land fast and create curiosity.',
      accentMode: 'contrast'
    },
    {
      moduleId: 'mod-topline',
      kind: 'topline',
      variant: 'spotlight-card',
      sourceKey: 'topLine',
      priority: 'primary',
      layoutHints: ['high-contrast-panel', 'short-copy', 'single-claim-focus'],
      interactionCue: 'Invite the user to pause on the claim.',
      accentMode: 'accent'
    },
    {
      moduleId: 'mod-radar',
      kind: 'radar',
      variant: 'signal-ribbons',
      sourceKey: 'radar',
      priority: 'secondary',
      layoutHints: ['horizontal-rhythm', 'tight-density', 'label-first'],
      interactionCue: 'Let the reader skim quickly.',
      accentMode: 'base'
    },
    {
      moduleId: 'mod-deep-dives',
      kind: 'deep-dive-grid',
      variant: 'collectible-triptych',
      sourceKey: 'deepDives',
      priority: 'primary',
      layoutHints: ['three-up-grid', 'varied-card-heights', 'numbered-subtheses'],
      interactionCue: 'Encourage compare-and-contrast reading.',
      accentMode: 'accent'
    },
    {
      moduleId: 'mod-market-map',
      kind: 'market-map',
      variant: 'pressure-ladder',
      sourceKey: 'marketMap',
      priority: 'secondary',
      layoutHints: ['stacked-bands', 'directional-labels', 'tight-summary'],
      interactionCue: 'Shift from explanation to posture.',
      accentMode: 'heat'
    },
    {
      moduleId: 'mod-watchlist',
      kind: 'watchlist',
      variant: 'question-steps',
      sourceKey: 'watchlist',
      priority: 'supporting',
      layoutHints: ['numbered-steps', 'breathing-room', 'exit-hook'],
      interactionCue: 'Make the user want to return tomorrow.',
      accentMode: 'contrast'
    }
  ]
};

function createElement(id) {
  return {
    id,
    textContent: '',
    innerHTML: '',
    disabled: false,
    dataset: {},
    className: '',
    style: {},
    listeners: {},
    addEventListener(type, handler) {
      this.listeners[type] = handler;
    },
    click() {
      if (this.listeners.click) this.listeners.click({ currentTarget: this });
    }
  };
}

function parseModuleMarkup(html, moduleId) {
  const pattern = new RegExp(`<section[^>]*data-module-id="${moduleId}"[^>]*>`, 'i');
  return html.match(pattern)?.[0] || '';
}

async function loadApp() {
  const source = await fs.readFile(new URL('../apps/briefing-page/app.js', import.meta.url), 'utf8');
  const elements = new Map();
  const fetchCalls = [];
  const scrollCalls = [];
  const intersectionObservers = [];

  function parseRenderedModules() {
    const app = elements.get('app');
    const html = app?.innerHTML || '';
    const matches = [...html.matchAll(/<section[^>]*id="([^"]+)"[^>]*data-module-id="([^"]+)"[^>]*data-focus-state="([^"]+)"/g)];
    return matches.map(([, id, moduleId, focusState]) => ({
      id,
      dataset: { moduleId, focusState },
      scrollIntoView(options) {
        scrollCalls.push({ id, options });
      }
    }));
  }

  function parseJumpNavButtons() {
    const nav = elements.get('jumpNav');
    const html = nav?.innerHTML || '';
    const matches = [...html.matchAll(/<button[^>]*id="([^"]+)"[^>]*data-module-id="([^"]+)"[^>]*data-jump-state="([^"]+)"[^>]*>([\s\S]*?)<\/button>/g)];
    return matches.map(([, id, moduleId, jumpState, textContent]) => {
      const existing = elements.get(id) || createElement(id);
      existing.dataset = { moduleId, jumpState };
      existing.textContent = textContent.replace(/<[^>]+>/g, '').trim();
      elements.set(id, existing);
      return existing;
    });
  }

  const getElementById = (id) => {
    if (!elements.has(id)) {
      const renderedModule = parseRenderedModules().find((item) => item.id === id);
      if (renderedModule) {
        elements.set(id, renderedModule);
        return renderedModule;
      }
      const jumpNavButton = parseJumpNavButtons().find((item) => item.id === id);
      if (jumpNavButton) {
        elements.set(id, jumpNavButton);
        return jumpNavButton;
      }
      elements.set(id, createElement(id));
    }
    return elements.get(id);
  };

  class IntersectionObserver {
    constructor(callback, options = {}) {
      this.callback = callback;
      this.options = options;
      this.observed = [];
      intersectionObservers.push(this);
    }

    observe(target) {
      this.observed.push(target);
    }

    disconnect() {
      this.observed = [];
    }

    trigger(entries) {
      this.callback(entries, this);
    }
  }

  const context = {
    console,
    setTimeout,
    clearTimeout,
    IntersectionObserver,
    window: {},
    document: {
      body: { dataset: {} },
      documentElement: { dataset: {} },
      getElementById,
      querySelectorAll(selector) {
        if (selector === '[data-module-id]') {
          return parseRenderedModules();
        }
        if (selector === '[data-jump-nav-button]') {
          return parseJumpNavButtons();
        }
        return [];
      },
      querySelector(selector) {
        if (selector.startsWith('#')) {
          return getElementById(selector.slice(1));
        }
        return null;
      }
    },
    fetch: async (url) => {
      fetchCalls.push(url);
      if (String(url).includes('visual-composition')) {
        return { ok: true, json: async () => compositionFixture };
      }
      if (String(url).includes('briefing')) {
        return { ok: true, json: async () => briefingFixture };
      }
      return { ok: false, status: 404, json: async () => ({}) };
    }
  };
  context.window = context;
  vm.createContext(context);
  vm.runInContext(source, context, { filename: 'app.js' });
  await new Promise((resolve) => setTimeout(resolve, 0));
  return { context, elements, fetchCalls, scrollCalls, intersectionObservers };
}

test('bootstrap loads both briefing and visual composition payloads', async () => {
  const { fetchCalls } = await loadApp();
  assert.deepEqual(fetchCalls, [
    './data/briefing.sample.json',
    './data/visual-composition.sample.json'
  ]);
});

test('renderer exposes composition-driven cues in the rendered page', async () => {
  const { context, elements } = await loadApp();
  const app = elements.get('app');
  const button = elements.get('themeNote');

  assert.ok(app.innerHTML.includes('Touch the thesis first, then test it against the radar.'));
  assert.ok(app.innerHTML.includes('Land fast and create curiosity.'));
  assert.ok(app.innerHTML.includes('Make the user want to return tomorrow.'));
  assert.equal(context.document.body.dataset.visualTone, 'electric');
  assert.equal(context.document.body.dataset.heroVariant, 'thesis-wall');
  assert.match(button.textContent, /layered/i);
});

test('interaction controls expose initial section progress and active module state', async () => {
  const { context, elements } = await loadApp();

  assert.equal(elements.get('readingProgress').textContent, '1 / 6');
  assert.equal(elements.get('activeSectionLabel').textContent, 'Opening thesis');
  assert.equal(context.document.body.dataset.activeModule, 'mod-hero');
  assert.match(elements.get('pathSummary').textContent, /6-stop reading path/i);
});

test('next section control advances the guided reading state', async () => {
  const { context, elements } = await loadApp();

  elements.get('nextSectionButton').click();

  assert.equal(elements.get('readingProgress').textContent, '2 / 6');
  assert.equal(elements.get('activeSectionLabel').textContent, 'Top line');
  assert.equal(context.document.body.dataset.activeModule, 'mod-topline');
  assert.match(elements.get('nextSectionButton').textContent, /Radar/);
});

test('scroll choreography marks the focused module and exposes a focus cue', async () => {
  const { context, elements } = await loadApp();
  const app = elements.get('app');

  assert.equal(elements.get('focusCue').textContent, 'Land fast and create curiosity.');
  assert.equal(context.document.body.dataset.scrollMood, 'punctuated');
  assert.equal(context.document.body.dataset.activeModuleIndex, '0');
  assert.match(app.innerHTML, /data-focus-state="active"[^>]*data-module-id="mod-hero"|data-module-id="mod-hero"[^>]*data-focus-state="active"/);
});

test('scroll choreography re-renders focus when advancing to the next module', async () => {
  const { context, elements } = await loadApp();
  const app = elements.get('app');

  elements.get('nextSectionButton').click();

  assert.equal(elements.get('focusCue').textContent, 'Invite the user to pause on the claim.');
  assert.equal(context.document.body.dataset.activeModuleIndex, '1');
  assert.match(app.innerHTML, /data-focus-state="active"[^>]*data-module-id="mod-topline"|data-module-id="mod-topline"[^>]*data-focus-state="active"/);
  assert.match(app.innerHTML, /data-focus-state="resting"[^>]*data-module-id="mod-hero"|data-module-id="mod-hero"[^>]*data-focus-state="resting"/);
});

test('viewport choreography registers an observer and exposes sync state', async () => {
  const { context, intersectionObservers } = await loadApp();

  assert.equal(intersectionObservers.length, 1);
  assert.equal(intersectionObservers[0].observed.length, 6);
  assert.equal(context.document.body.dataset.viewportSync, 'observer');
});

test('next section control scrolls the next module into view', async () => {
  const { elements, scrollCalls } = await loadApp();

  elements.get('nextSectionButton').click();

  assert.equal(scrollCalls[0]?.id, 'mod-topline');
  assert.equal(scrollCalls[0]?.options?.behavior, 'smooth');
  assert.equal(scrollCalls[0]?.options?.block, 'center');
});

test('viewport observer updates the active module from real section intersections', async () => {
  const { context, elements, intersectionObservers } = await loadApp();

  intersectionObservers[0].trigger([
    {
      isIntersecting: true,
      intersectionRatio: 0.9,
      target: { dataset: { moduleId: 'mod-market-map' } }
    }
  ]);

  assert.equal(elements.get('readingProgress').textContent, '5 / 6');
  assert.equal(elements.get('activeSectionLabel').textContent, 'Market map');
  assert.equal(elements.get('focusCue').textContent, 'Shift from explanation to posture.');
  assert.equal(context.document.body.dataset.activeModule, 'mod-market-map');
  assert.equal(context.document.body.dataset.activeModuleIndex, '4');
});

test('jump nav exposes every module and highlights the active stop', async () => {
  const { elements } = await loadApp();
  const jumpNav = elements.get('jumpNav');

  assert.match(jumpNav.innerHTML, /Opening thesis/);
  assert.match(jumpNav.innerHTML, /What to watch/);
  assert.match(jumpNav.innerHTML, /data-jump-state="active"[^>]*data-module-id="mod-hero"|data-module-id="mod-hero"[^>]*data-jump-state="active"/);
});

test('jump nav can move reading focus directly to a chosen module', async () => {
  const { context, elements, scrollCalls } = await loadApp();

  context.document.getElementById('jumpNav-mod-market-map').click();

  assert.equal(elements.get('readingProgress').textContent, '5 / 6');
  assert.equal(context.document.body.dataset.activeModule, 'mod-market-map');
  assert.equal(scrollCalls.at(-1)?.id, 'mod-market-map');
});

test('jump nav re-syncs its active marker after viewport-driven updates', async () => {
  const { elements, intersectionObservers } = await loadApp();
  const jumpNav = elements.get('jumpNav');

  intersectionObservers[0].trigger([
    {
      isIntersecting: true,
      intersectionRatio: 0.9,
      target: { dataset: { moduleId: 'mod-watchlist' } }
    }
  ]);

  assert.match(jumpNav.innerHTML, /data-jump-state="active"[^>]*data-module-id="mod-watchlist"|data-module-id="mod-watchlist"[^>]*data-jump-state="active"/);
});

test('entrance choreography exposes staged motion metadata and per-module stagger indices', async () => {
  const { context, elements } = await loadApp();
  const app = elements.get('app');
  const heroMarkup = parseModuleMarkup(app.innerHTML, 'mod-hero');
  const radarMarkup = parseModuleMarkup(app.innerHTML, 'mod-radar');

  assert.equal(context.document.body.dataset.entranceChoreography, 'staged');
  assert.equal(context.document.body.dataset.motionProfile, 'punctuated');
  assert.match(heroMarkup, /data-entrance-state="active"/);
  assert.match(heroMarkup, /style="[^"]*--entrance-index:\s*0[;"]/);
  assert.match(radarMarkup, /style="[^"]*--entrance-index:\s*2[;"]/);
});

test('entrance choreography promotes visited modules from queued to entered as reading focus advances', async () => {
  const { elements } = await loadApp();
  const app = elements.get('app');

  elements.get('nextSectionButton').click();

  const heroMarkup = parseModuleMarkup(app.innerHTML, 'mod-hero');
  const toplineMarkup = parseModuleMarkup(app.innerHTML, 'mod-topline');
  const radarMarkup = parseModuleMarkup(app.innerHTML, 'mod-radar');

  assert.match(heroMarkup, /data-entrance-state="entered"/);
  assert.match(toplineMarkup, /data-entrance-state="active"/);
  assert.match(radarMarkup, /data-entrance-state="queued"/);
});

test('module depth renders composition-derived metadata rails for premium modules', async () => {
  const { elements } = await loadApp();
  const app = elements.get('app');

  assert.match(app.innerHTML, /module-depth-rail/);
  assert.match(app.innerHTML, /Priority<\/span>\s*<strong>primary<\/strong>/i);
  assert.match(app.innerHTML, /Accent<\/span>\s*<strong>contrast<\/strong>/i);
  assert.match(app.innerHTML, /oversized-headline/);
});

test('module depth keeps active priority and accent mode in sync with reading focus', async () => {
  const { context, elements } = await loadApp();

  assert.equal(context.document.body.dataset.activePriority, 'primary');
  assert.equal(context.document.body.dataset.activeAccentMode, 'contrast');

  elements.get('nextSectionButton').click();
  assert.equal(context.document.body.dataset.activePriority, 'primary');
  assert.equal(context.document.body.dataset.activeAccentMode, 'accent');

  context.document.getElementById('jumpNav-mod-market-map').click();
  assert.equal(context.document.body.dataset.activePriority, 'secondary');
  assert.equal(context.document.body.dataset.activeAccentMode, 'heat');
});
