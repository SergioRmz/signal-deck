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
    { moduleId: 'mod-hero', kind: 'hero', variant: 'thesis-wall-glow', sourceKey: 'hero', interactionCue: 'Land fast and create curiosity.' },
    { moduleId: 'mod-topline', kind: 'topline', variant: 'spotlight-card', sourceKey: 'topLine', interactionCue: 'Invite the user to pause on the claim.' },
    { moduleId: 'mod-radar', kind: 'radar', variant: 'signal-ribbons', sourceKey: 'radar', interactionCue: 'Let the reader skim quickly.' },
    { moduleId: 'mod-deep-dives', kind: 'deep-dive-grid', variant: 'collectible-triptych', sourceKey: 'deepDives', interactionCue: 'Encourage compare-and-contrast reading.' },
    { moduleId: 'mod-market-map', kind: 'market-map', variant: 'pressure-ladder', sourceKey: 'marketMap', interactionCue: 'Shift from explanation to posture.' },
    { moduleId: 'mod-watchlist', kind: 'watchlist', variant: 'question-steps', sourceKey: 'watchlist', interactionCue: 'Make the user want to return tomorrow.' }
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

async function loadApp() {
  const source = await fs.readFile(new URL('../apps/briefing-page/app.js', import.meta.url), 'utf8');
  const elements = new Map();
  const fetchCalls = [];

  const getElementById = (id) => {
    if (!elements.has(id)) elements.set(id, createElement(id));
    return elements.get(id);
  };

  const context = {
    console,
    setTimeout,
    clearTimeout,
    window: {},
    document: {
      body: { dataset: {} },
      documentElement: { dataset: {} },
      getElementById
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
  return { context, elements, fetchCalls };
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
