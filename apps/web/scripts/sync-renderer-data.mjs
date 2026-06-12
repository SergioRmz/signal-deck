import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const webRoot = path.resolve(__dirname, '..');
const publicDataDir = path.resolve(webRoot, 'public/data');

const DEFAULT_BRIEFING_PATH = '../briefing-page/data/briefing.sample.json';
const DEFAULT_COMPOSITION_PATH = '../briefing-page/data/visual-composition.sample.json';

async function maybeLoadDotEnvFile(filename) {
  const envPath = path.resolve(webRoot, filename);

  try {
    const raw = await readFile(envPath, 'utf8');

    for (const line of raw.split(/\r?\n/)) {
      const trimmed = line.trim();

      if (!trimmed || trimmed.startsWith('#')) {
        continue;
      }

      const separatorIndex = trimmed.indexOf('=');

      if (separatorIndex === -1) {
        continue;
      }

      const key = trimmed.slice(0, separatorIndex).trim();
      const value = trimmed.slice(separatorIndex + 1).trim().replace(/^['"]|['"]$/g, '');

      if (!(key in process.env)) {
        process.env[key] = value;
      }
    }
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      return;
    }

    throw error;
  }
}

function resolveDataPath(relativePath) {
  return path.resolve(webRoot, relativePath);
}

async function copyJson(sourceRelativePath, destinationName) {
  const absoluteSourcePath = resolveDataPath(sourceRelativePath);
  const destinationPath = path.resolve(publicDataDir, destinationName);
  const raw = await readFile(absoluteSourcePath, 'utf8');

  JSON.parse(raw);
  await writeFile(destinationPath, `${raw.trim()}\n`, 'utf8');

  return { absoluteSourcePath, destinationPath };
}

await maybeLoadDotEnvFile('.env');
await maybeLoadDotEnvFile('.env.local');
await mkdir(publicDataDir, { recursive: true });

const briefingSource = process.env.SIGNAL_DECK_BRIEFING_PATH || DEFAULT_BRIEFING_PATH;
const compositionSource = process.env.SIGNAL_DECK_COMPOSITION_PATH || DEFAULT_COMPOSITION_PATH;

const briefingResult = await copyJson(briefingSource, 'briefing.json');
const compositionResult = await copyJson(compositionSource, 'composition.json');

console.log(`Synced briefing data from ${briefingResult.absoluteSourcePath} -> ${briefingResult.destinationPath}`);
console.log(`Synced composition data from ${compositionResult.absoluteSourcePath} -> ${compositionResult.destinationPath}`);
