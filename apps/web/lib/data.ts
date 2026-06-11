import { readFile } from 'node:fs/promises';
import path from 'node:path';

export type BriefingData = {
  meta: {
    briefingId: string;
    editionDate: string;
    language?: string;
    topics?: string[];
    readerContext?: {
      roles?: string[];
      interests?: string[];
      desiredUpgrade?: string;
    };
  };
  hero: {
    title: string;
    lede: string;
    signal?: string;
    thesis?: string;
    tension?: string;
    promise?: string;
  };
  topLine: {
    title: string;
    body: string;
    stakes?: string;
  };
};

export type CompositionModule = {
  moduleId: string;
  kind: string;
  variant?: string;
  headline?: string;
  interactionCue?: string;
  accentMode?: string;
};

export type VisualComposition = {
  experience?: {
    visualTone?: string;
    engagementGoal?: string;
    readingMode?: string;
  };
  page?: {
    moduleOrder?: string[];
  };
  modules?: CompositionModule[];
};

const DEFAULT_BRIEFING_PATH = '../briefing-page/data/briefing.sample.json';
const DEFAULT_COMPOSITION_PATH = '../briefing-page/data/visual-composition.sample.json';

async function readJsonFile<T>(relativePath: string): Promise<T> {
  const absolutePath = path.resolve(process.cwd(), relativePath);
  const raw = await readFile(absolutePath, 'utf8');
  return JSON.parse(raw) as T;
}

export async function loadBriefing(): Promise<BriefingData> {
  return readJsonFile<BriefingData>(process.env.SIGNAL_DECK_BRIEFING_PATH || DEFAULT_BRIEFING_PATH);
}

export async function loadComposition(): Promise<VisualComposition> {
  return readJsonFile<VisualComposition>(process.env.SIGNAL_DECK_COMPOSITION_PATH || DEFAULT_COMPOSITION_PATH);
}
