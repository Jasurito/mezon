/**
 * API contract, mirrored from backend/app/schemas (api.py, legal.py, analytics.py).
 * When the backend schema changes, `make api-client` (openapi-typescript) will replace this
 * hand-written copy; until then keep field names identical.
 */
export type Locale = "ru" | "uz-Latn" | "uz-Cyrl";
export type ActionKind = "question" | "evidence" | "motion" | "objection" | "argument" | "decision" | "continue";
export type Reaction = "nod" | "object" | "surprised" | "think" | "gavel";
export type EditionStatus = "current" | "historical" | "unconfirmed";
export type Difficulty = "beginner" | "intermediate" | "advanced";

export interface UserOut { user_id: string; display_name: string | null; created_at: string }

export interface OptionView { id: string; label: string }
export interface ActionView {
  action_id: string; kind: ActionKind; label: string;
  target_character: string | null; evidence_id: string | null;
  options: OptionView[] | null; hint_citation_ids: string[];
}

export type GameEvent =
  | { type: "say"; speaker: string; text: string; emotion: string }
  | { type: "react"; character: string; reaction: Reaction }
  | { type: "stage_changed"; stage: string; title: string }
  | { type: "evidence_added"; evidence_id: string }
  | { type: "score"; delta: number; total: number }
  | { type: "legal_note"; citation_id: string; text: string }
  | { type: "mistake"; category: string; text: string };

export interface EvidenceView { id: string; title: string; type: "document" | "object" | "testimony"; reviewed: boolean; presented: boolean }

export interface GameState {
  session_id: string; scenario_id: string; locale: Locale;
  stage: string; stage_title: string; stage_index: number; stage_count: number;
  score: number; max_score: number;
  evidence: EvidenceView[]; available_actions: ActionView[]; events: GameEvent[];
  finished: boolean; legal_date: string;
}

export interface ScenarioCard {
  scenario_id: string; title: string; category: string; difficulty: Difficulty; minutes: number;
  topics: string[]; cover: string | null; fictional_notice: string; available: boolean;
}
export interface CharacterView { id: string; name: string; role: string; sprite: string }
export interface LegalActView { document_key: string; title: string; source_url: string | null }
export interface ScenarioDetail {
  scenario_id: string; title: string; fictional_notice: string; legal_date: string; story: string;
  player_role: { character_id: string; title: string };
  characters: CharacterView[];
  claims: { side: "plaintiff" | "defendant"; text: string }[];
  documents: { id: string; title: string }[];
  legal_acts: LegalActView[];
}

export interface EditionView { effective_from: string | null; effective_to: string | null; status: EditionStatus }
export interface ArticlePartView { part_number: number; kind: string; text: string }
export interface CitationView {
  citation_id: string | null; article_id: number; document_key: string; document_title: string; document_type: string;
  document_number: string | null; article_number: string; article_title: string | null; chapter: string | null;
  part: number | null; parts: ArticlePartView[]; text: string; language: string; is_official_text: boolean | null;
  edition: EditionView; source_url: string | null; last_verified_at: string | null; translation_note: string | null;
}

export interface DecisionView {
  decision_id: string; stage: string; chosen: string | null; chosen_label: string; best: string; best_label: string;
  correct: boolean; explanation: string; citation_ids: string[];
}
export interface MistakeView { category: string; title: string; explanation: string; correct_action: string | null; citation_ids: string[] }
export interface RecommendationView { topic: string; citation_ids: string[]; scenario_id: string | null }
export interface SessionResult {
  session_id: string; scenario_id: string; outcome: string; outcome_title: string; ruling_text: string;
  score: number; max_score: number; correct_decision_rate: number; time_spent_sec: number;
  decisions: DecisionView[]; mistakes: MistakeView[]; citations: CitationView[];
  recommendations: RecommendationView[]; disclaimer: string;
}

export type QuizKind = "pre" | "post";
export interface QuizOut { scenario_id: string; kind: QuizKind; questions: { question_id: string; text: string; options: { id: string; text: string }[] }[]; total: number }
export interface QuizReviewItem { question_id: string; chosen_option: string | null; correct: boolean; correct_option: string; explanation: string; citation_ids: string[] }
export interface LearningGain { pre: number; post: number; max: number; delta: number; note: string }
export interface QuizAttemptOut { attempt_id: number; score: number; max: number; review: QuizReviewItem[]; learning_gain: LearningGain | null }

export interface DashboardOut {
  user: { user_id: string; display_name: string | null };
  knowledge_level: { score: number | null; label: string };
  completed: { session_id: string; scenario_id: string; title: string; outcome: string | null; outcome_title: string; score: number; max_score: number; finished_at: string }[];
  learning_gain: { scenario_id: string; pre: number; post: number; max: number; note: string }[];
  mistake_categories: { category: string; title: string; count: number }[];
  recommended: (ScenarioCard & { reason?: string })[];
}

export interface HealthResponse { status: "ok" | "degraded"; db: boolean; articles: number | null; chunks: number | null; scenarios: number; llm_configured: boolean; embedder: string }

/** Mentor SSE stream, already parsed. */
export type MentorEvent =
  | { event: "sources"; data: { source_id: string; citation: CitationView }[] }
  | { event: "block"; data: { text: string; source_ids: string[]; verified: boolean } }
  | { event: "done"; data: { insufficient_sources: boolean; ai_unavailable: boolean; message?: string; disclaimer: string } }
  | { event: "error"; data: { code: string; message: string } };
export interface MentorAsk { session_id: string | null; question: string; locale: Locale; history: { role: "user" | "assistant"; text: string }[] }

export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string, public details: unknown = {}) { super(message); }
}

/** One interface, two implementations (mock now, live when the backend is deployed). */
export interface Api {
  health(): Promise<HealthResponse>;
  createUser(displayName?: string | null): Promise<UserOut>;
  dashboard(userId: string, locale: Locale): Promise<DashboardOut>;
  scenarios(locale: Locale): Promise<ScenarioCard[]>;
  scenario(id: string, locale: Locale): Promise<ScenarioDetail>;
  quiz(scenarioId: string, kind: QuizKind, locale: Locale): Promise<QuizOut>;
  submitQuiz(scenarioId: string, body: { user_id: string; kind: QuizKind; answers: Record<string, string> }, locale: Locale): Promise<QuizAttemptOut>;
  createSession(body: { user_id: string; scenario_id: string; locale: Locale }): Promise<GameState>;
  session(id: string, locale?: Locale): Promise<GameState>;
  setSessionLocale(id: string, locale: Locale): Promise<GameState>;
  act(id: string, actionId: string, params?: { option?: string }): Promise<GameState>;
  result(id: string, locale?: Locale): Promise<SessionResult>;
  citation(id: string, date: string | null, locale: Locale): Promise<CitationView>;
  mentor(body: MentorAsk, signal?: AbortSignal): AsyncGenerator<MentorEvent>;
  /** Evidence document body. NOT in the backend contract yet: needs an endpoint (e.g. GET /api/scenarios/{id}/documents/{doc}). */
  document(scenarioId: string, evidenceId: string, locale: Locale): Promise<string[]>;
  events(body: { user_id: string; session_id?: string; events: { type: string; payload: unknown; ts: string }[] }): Promise<void>;
}
