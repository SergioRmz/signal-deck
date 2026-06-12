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
  radar?: {
    title: string;
    items: Array<{
      label: string;
      text: string;
      role?: string;
    }>;
  };
  deepDives?: {
    title: string;
    items: Array<{
      title: string;
      body: string;
      mechanism?: string;
      claim?: string;
      explanation?: string;
      implication?: string;
    }>;
  };
  marketMap?: {
    title: string;
    items: Array<{
      label: string;
      text: string;
      powerShift?: string;
    }>;
  };
  reusableLesson?: {
    title: string;
    pattern: string;
    takeaway: string;
    applyWhen?: string[];
  };
  readerTranslation?: {
    title: string;
    items: Array<{
      role: string;
      headline: string;
      body: string;
      weight?: number;
    }>;
  };
  watchlist?: {
    title: string;
    items: Array<{
      text: string;
      type?: string;
    }>;
  };
};

export type CompositionModule = {
  moduleId: string;
  kind: string;
  sourceKey?: string;
  variant?: string;
  headline?: string;
  interactionCue?: string;
  accentMode?: string;
  priority?: string;
  layoutHints?: string[];
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

const BRIEFING_PATH = `${import.meta.env.BASE_URL}data/briefing.json`;
const COMPOSITION_PATH = `${import.meta.env.BASE_URL}data/composition.json`;

async function readJsonFile<T>(assetPath: string): Promise<T> {
  const response = await fetch(assetPath, {
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to load ${assetPath}: ${response.status} ${response.statusText}`);
  }

  return (await response.json()) as T;
}

export async function loadBriefing(): Promise<BriefingData> {
  return readJsonFile<BriefingData>(BRIEFING_PATH);
}

export async function loadComposition(): Promise<VisualComposition> {
  return readJsonFile<VisualComposition>(COMPOSITION_PATH);
}
