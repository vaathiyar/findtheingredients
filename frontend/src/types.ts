export interface Recipe {
  id: string;
  slug: string;
  title: string;
  cuisine: string | null;
}

export interface SessionInfo {
  token: string;
  livekit_url: string;
  room_name: string;
}

export interface RecipeIngredient {
  name: string;
  quantity: string | null;
  optional: boolean;
  notes: string | null;
}

export interface PrepItem {
  task: string;
  duration: string | null;
  ingredients: string[];
  notes: string | null;
}

export interface PreCookBriefing {
  summary: string;
  active_time: string | null;
  passive_time: string | null;
  prep_items: PrepItem[];
}

export interface RecipeDetail {
  id: string;
  slug: string;
  title: string;
  cuisine: string | null;
  source_url: string | null;
  precook_briefing: PreCookBriefing | null;
  ingredients: RecipeIngredient[] | null;
}
