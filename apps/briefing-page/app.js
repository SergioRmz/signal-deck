const app = document.getElementById('app');
const button = document.getElementById('themeNote');

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function renderBriefing(data) {
  document.getElementById('heroTitle').textContent = data.meta.heroTitle;
  document.getElementById('heroLede').textContent = data.meta.heroLede;
  document.getElementById('editionDate').textContent = data.meta.editionDate;
  document.getElementById('editionMode').textContent = data.meta.mode;
  document.getElementById('editionFormat').textContent = data.meta.format;
  document.getElementById('footerNote').textContent = data.meta.footerNote;

  const radarItems = data.radar
    .map(
      (item) =>
        `<li><strong>${escapeHtml(item.label)}:</strong> ${escapeHtml(item.text)}</li>`
    )
    .join('');

  const deepDiveItems = data.deepDives.items
    .map(
      (item) => `
        <article class="card">
          <h3>${escapeHtml(item.title)}</h3>
          <p>${escapeHtml(item.body)}</p>
        </article>
      `
    )
    .join('');

  const marketItems = data.marketMap.items
    .map(
      (item) => `<p><strong>${escapeHtml(item.label)}:</strong> ${escapeHtml(item.text)}</p>`
    )
    .join('');

  const watchItems = data.watchlist.items
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join('');

  app.innerHTML = `
    <section class="grid grid--2">
      <article class="card thesis">
        <span class="kicker">Top line</span>
        <h2>${escapeHtml(data.topLine.title)}</h2>
        <p>${escapeHtml(data.topLine.body)}</p>
      </article>

      <article class="card signal-list">
        <span class="kicker">Radar</span>
        <ul>${radarItems}</ul>
      </article>
    </section>

    <section class="section-heading">
      <div>
        <span class="kicker">Deep dives</span>
        <h2>${escapeHtml(data.deepDives.heading)}</h2>
      </div>
    </section>

    <section class="grid grid--3">${deepDiveItems}</section>

    <section class="grid grid--2 market-section">
      <article class="card">
        <span class="kicker">Market map</span>
        <h2>${escapeHtml(data.marketMap.title)}</h2>
        <div class="stack">${marketItems}</div>
      </article>

      <article class="card">
        <span class="kicker">What to watch</span>
        <h2>${escapeHtml(data.watchlist.title)}</h2>
        <ol class="watch-list">${watchItems}</ol>
      </article>
    </section>
  `;
}

async function bootstrap() {
  try {
    const response = await fetch('./data/briefing.sample.json');

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    renderBriefing(data);
  } catch (error) {
    app.innerHTML = `
      <section class="card">
        <span class="kicker">Error</span>
        <h2>No se pudo cargar el briefing.</h2>
        <p>Revisa <code>data/briefing.sample.json</code> y vuelve a intentar.</p>
      </section>
    `;
    console.error(error);
  }
}

if (button) {
  button.addEventListener('click', () => {
    button.textContent = 'Diseñado para briefings sobrios, densos y externos';
    button.disabled = true;
  });
}

bootstrap();
