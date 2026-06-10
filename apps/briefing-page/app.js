const app = document.getElementById('app');
const button = document.getElementById('themeNote');
const footerNote = document.getElementById('footerNote');
const readingProgress = document.getElementById('readingProgress');
const activeSectionLabel = document.getElementById('activeSectionLabel');
const pathSummary = document.getElementById('pathSummary');
const nextSectionButton = document.getElementById('nextSectionButton');
const prevSectionButton = document.getElementById('prevSectionButton');
const focusCue = document.getElementById('focusCue');

let readingState = {
  moduleOrder: [],
  modules: new Map(),
  activeIndex: 0,
  briefing: null,
  composition: null
};

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function moduleMap(composition) {
  return new Map((composition.modules || []).map((module) => [module.moduleId, module]));
}

function sectionLabelForModule(moduleId, module) {
  const fallback = {
    'mod-hero': 'Opening thesis',
    'mod-topline': 'Top line',
    'mod-radar': 'Radar',
    'mod-deep-dives': 'Deep dives',
    'mod-market-map': 'Market map',
    'mod-watchlist': 'What to watch'
  };

  return module?.kind
    ? fallback[moduleId] || module.kind.replaceAll('-', ' ')
    : fallback[moduleId] || 'Section';
}

function focusStateFor(moduleId) {
  return readingState.moduleOrder[readingState.activeIndex] === moduleId ? 'active' : 'resting';
}

function renderHeroModule(data, module) {
  const cue = module?.interactionCue
    ? `<p class="module-cue">${escapeHtml(module.interactionCue)}</p>`
    : '';

  return `
    <section id="mod-hero" data-module-id="mod-hero" data-focus-state="${focusStateFor('mod-hero')}" class="hero-panel card hero-panel--${escapeHtml(module?.variant || 'default')} ${focusStateFor('mod-hero') === 'active' ? 'is-active' : 'is-resting'}">
      <div class="hero-panel__copy">
        <span class="kicker">Opening thesis</span>
        <h2>${escapeHtml(module?.headline || data.hero.title)}</h2>
        <p class="hero-panel__body">${escapeHtml(data.hero.lede)}</p>
        ${cue}
      </div>
    </section>
  `;
}

function renderToplineModule(data, module) {
  return `
    <section id="mod-topline" data-module-id="mod-topline" data-focus-state="${focusStateFor('mod-topline')}" class="card spotlight-card spotlight-card--${escapeHtml(module?.variant || 'default')} ${focusStateFor('mod-topline') === 'active' ? 'is-active' : 'is-resting'}">
      <span class="kicker">Top line</span>
      <h2>${escapeHtml(data.topLine.title)}</h2>
      <p>${escapeHtml(data.topLine.body)}</p>
      <p class="module-cue">${escapeHtml(module?.interactionCue || '')}</p>
    </section>
  `;
}

function renderRadarModule(data, module) {
  const items = data.radar.items
    .map(
      (item) => `
        <li class="signal-pill">
          <strong>${escapeHtml(item.label)}</strong>
          <span>${escapeHtml(item.text)}</span>
        </li>
      `
    )
    .join('');

  return `
    <section id="mod-radar" data-module-id="mod-radar" data-focus-state="${focusStateFor('mod-radar')}" class="card signal-radar signal-radar--${escapeHtml(module?.variant || 'default')} ${focusStateFor('mod-radar') === 'active' ? 'is-active' : 'is-resting'}">
      <div class="section-heading section-heading--compact">
        <div>
          <span class="kicker">Radar</span>
          <h2>${escapeHtml(data.radar.title)}</h2>
        </div>
        <p class="module-cue">${escapeHtml(module?.interactionCue || '')}</p>
      </div>
      <ul class="signal-pill-list">${items}</ul>
    </section>
  `;
}

function renderDeepDivesModule(data, module) {
  const items = data.deepDives.items
    .map(
      (item, index) => `
        <article class="card collectible-card">
          <span class="collectible-index">0${index + 1}</span>
          <h3>${escapeHtml(item.title)}</h3>
          <p>${escapeHtml(item.body)}</p>
        </article>
      `
    )
    .join('');

  return `
    <section id="mod-deep-dives" data-module-id="mod-deep-dives" data-focus-state="${focusStateFor('mod-deep-dives')}" class="module-group module-group--deep-dives ${focusStateFor('mod-deep-dives') === 'active' ? 'is-active' : 'is-resting'}">
      <div class="section-heading">
        <div>
          <span class="kicker">Deep dives</span>
          <h2>${escapeHtml(data.deepDives.title)}</h2>
        </div>
        <p class="module-cue">${escapeHtml(module?.interactionCue || '')}</p>
      </div>
      <div class="grid grid--3">${items}</div>
    </section>
  `;
}

function renderMarketMapModule(data, module) {
  const items = data.marketMap.items
    .map(
      (item) => `
        <li class="pressure-band">
          <strong>${escapeHtml(item.label)}</strong>
          <span>${escapeHtml(item.text)}</span>
        </li>
      `
    )
    .join('');

  return `
    <section id="mod-market-map" data-module-id="mod-market-map" data-focus-state="${focusStateFor('mod-market-map')}" class="card market-map market-map--${escapeHtml(module?.variant || 'default')} ${focusStateFor('mod-market-map') === 'active' ? 'is-active' : 'is-resting'}">
      <div class="section-heading section-heading--compact">
        <div>
          <span class="kicker">Market map</span>
          <h2>${escapeHtml(data.marketMap.title)}</h2>
        </div>
        <p class="module-cue">${escapeHtml(module?.interactionCue || '')}</p>
      </div>
      <ul class="pressure-band-list">${items}</ul>
    </section>
  `;
}

function renderWatchlistModule(data, module) {
  const items = data.watchlist.items
    .map(
      (item, index) => `
        <li>
          <span class="watch-step">${index + 1}</span>
          <span>${escapeHtml(item.text)}</span>
        </li>
      `
    )
    .join('');

  return `
    <section id="mod-watchlist" data-module-id="mod-watchlist" data-focus-state="${focusStateFor('mod-watchlist')}" class="card watchlist-card watchlist-card--${escapeHtml(module?.variant || 'default')} ${focusStateFor('mod-watchlist') === 'active' ? 'is-active' : 'is-resting'}">
      <div class="section-heading section-heading--compact">
        <div>
          <span class="kicker">What to watch</span>
          <h2>${escapeHtml(data.watchlist.title)}</h2>
        </div>
        <p class="module-cue">${escapeHtml(module?.interactionCue || '')}</p>
      </div>
      <ol class="watch-list watch-list--stepped">${items}</ol>
    </section>
  `;
}

function renderExperienceRail(composition) {
  const hooks = (composition.experience?.hooks || [])
    .map((hook) => `<li>${escapeHtml(hook)}</li>`)
    .join('');
  const prompts = (composition.experience?.learningPrompts || [])
    .map((prompt) => `<li>${escapeHtml(prompt)}</li>`)
    .join('');

  return `
    <section class="grid grid--2 experience-rail">
      <article class="card">
        <span class="kicker">Hook</span>
        <h2>Why this edition should pull you in</h2>
        <ul class="watch-list">${hooks}</ul>
      </article>
      <article class="card">
        <span class="kicker">Learn</span>
        <h2>How to move through it</h2>
        <ul class="watch-list">${prompts}</ul>
      </article>
    </section>
  `;
}

function renderModuleById(data, composition, id) {
  const modules = moduleMap(composition);
  const module = modules.get(id);

  switch (id) {
    case 'mod-hero':
      return renderHeroModule(data, module);
    case 'mod-topline':
      return renderToplineModule(data, module);
    case 'mod-radar':
      return renderRadarModule(data, module);
    case 'mod-deep-dives':
      return renderDeepDivesModule(data, module);
    case 'mod-market-map':
      return renderMarketMapModule(data, module);
    case 'mod-watchlist':
      return renderWatchlistModule(data, module);
    default:
      return '';
  }
}

function renderCurrentView() {
  if (!readingState.briefing || !readingState.composition) {
    return;
  }

  const moduleOrder = readingState.composition.page?.moduleOrder || [];
  const modulesHtml = moduleOrder.map((id) => renderModuleById(readingState.briefing, readingState.composition, id)).join('');

  app.innerHTML = `
    ${modulesHtml}
    ${renderExperienceRail(readingState.composition)}
  `;
}

function updateReadingDock() {
  const total = readingState.moduleOrder.length;
  if (!total) return;

  const activeId = readingState.moduleOrder[readingState.activeIndex];
  const activeModule = readingState.modules.get(activeId);
  const activeLabel = sectionLabelForModule(activeId, activeModule);
  const nextId = readingState.moduleOrder[(readingState.activeIndex + 1) % total];
  const prevId = readingState.moduleOrder[(readingState.activeIndex - 1 + total) % total];
  const nextLabel = sectionLabelForModule(nextId, readingState.modules.get(nextId));
  const prevLabel = sectionLabelForModule(prevId, readingState.modules.get(prevId));
  const scrollMood = readingState.composition?.page?.scrollMood || 'steady';

  document.body.dataset.activeModule = activeId;
  document.body.dataset.activeModuleIndex = String(readingState.activeIndex);
  document.body.dataset.scrollMood = scrollMood;

  if (readingProgress) {
    readingProgress.textContent = `${readingState.activeIndex + 1} / ${total}`;
  }
  if (activeSectionLabel) {
    activeSectionLabel.textContent = activeLabel;
  }
  if (pathSummary) {
    pathSummary.textContent = `${total}-stop reading path · ${activeLabel}`;
  }
  if (focusCue) {
    focusCue.textContent = activeModule?.interactionCue || 'Follow the guided reading path.';
  }
  if (nextSectionButton) {
    nextSectionButton.textContent = `Next: ${nextLabel}`;
  }
  if (prevSectionButton) {
    prevSectionButton.textContent = `Back: ${prevLabel}`;
  }
}

function moveReadingFocus(step) {
  const total = readingState.moduleOrder.length;
  if (!total) return;
  readingState.activeIndex = (readingState.activeIndex + step + total) % total;
  renderCurrentView();
  updateReadingDock();
}

function initializeReadingPattern(briefing, composition) {
  const order = composition.page?.moduleOrder || [];
  readingState = {
    moduleOrder: order,
    modules: moduleMap(composition),
    activeIndex: 0,
    briefing,
    composition
  };
  renderCurrentView();
  updateReadingDock();
}

function applyCompositionMetadata(composition) {
  const body = document.body;
  const root = document.documentElement;
  const theme = composition.designSystem?.theme || 'dark';
  const visualTone = composition.experience?.visualTone || 'default';
  const interactionModel = composition.experience?.interactionModel || 'linear';
  const heroVariant = composition.page?.heroVariant || 'default';

  if (body) {
    body.dataset.theme = theme;
    body.dataset.visualTone = visualTone;
    body.dataset.interactionModel = interactionModel;
    body.dataset.heroVariant = heroVariant;
  }

  if (root) {
    root.dataset.theme = theme;
    root.dataset.visualTone = visualTone;
  }

  const editionMode = document.getElementById('editionMode');
  const editionFormat = document.getElementById('editionFormat');
  const heroTitle = document.getElementById('heroTitle');
  const heroLede = document.getElementById('heroLede');
  const editionDate = document.getElementById('editionDate');

  if (heroTitle) heroTitle.textContent = composition.modules?.find((item) => item.moduleId === 'mod-hero')?.headline || '';
  if (heroLede) heroLede.textContent = composition.experience?.engagementGoal || '';
  if (editionDate) editionDate.textContent = composition.sourceBriefing?.editionDate || editionDate.textContent;
  if (editionMode) editionMode.textContent = `${theme} / ${visualTone}`;
  if (editionFormat) editionFormat.textContent = `${interactionModel} single page`;
  if (footerNote) footerNote.textContent = composition.experience?.engagementGoal || footerNote.textContent;
  if (button) button.textContent = `${theme} theme · ${interactionModel} reading`;
}

async function bootstrap() {
  try {
    const [briefingResponse, compositionResponse] = await Promise.all([
      fetch('./data/briefing.sample.json'),
      fetch('./data/visual-composition.sample.json')
    ]);

    if (!briefingResponse.ok) {
      throw new Error(`Briefing HTTP ${briefingResponse.status}`);
    }

    if (!compositionResponse.ok) {
      throw new Error(`Composition HTTP ${compositionResponse.status}`);
    }

    const [briefing, composition] = await Promise.all([
      briefingResponse.json(),
      compositionResponse.json()
    ]);

    applyCompositionMetadata(composition);
    initializeReadingPattern(briefing, composition);
  } catch (error) {
    app.innerHTML = `
      <section class="card">
        <span class="kicker">Error</span>
        <h2>Could not load the composition-aware briefing.</h2>
        <p>Check <code>data/briefing.sample.json</code> and <code>data/visual-composition.sample.json</code>.</p>
      </section>
    `;
    console.error(error);
  }
}

if (button) {
  button.addEventListener('click', () => {
    button.textContent = 'Dark theme · layered reading';
    button.disabled = true;
  });
}

if (nextSectionButton) {
  nextSectionButton.addEventListener('click', () => moveReadingFocus(1));
}

if (prevSectionButton) {
  prevSectionButton.addEventListener('click', () => moveReadingFocus(-1));
}

bootstrap();
