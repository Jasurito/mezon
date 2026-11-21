/**
 * In-browser mock of the FastAPI backend (same contract as lib/api/types.ts).
 * Persists users, sessions (action logs) and quiz attempts in localStorage, so reloads and
 * locale switches behave like the real server-authoritative API.
 */
import { latnToCyrl } from "@/lib/translit";
import {
  ApiError, NPC_MAX_LEN, type Api, type CitationView, type DashboardOut, type GameState, type Locale, type MentorEvent,
  type NpcAnswer, type QuizKind, type ScenarioCard, type ScenarioDetail, type SessionResult,
} from "../types";
import { actTitle, QUIZ, tx } from "./content";
import { availableActions, evaluate, IllegalAction, LEGAL_DATE, MAX_SCORE, replay, stageInfo, type LoggedAction } from "./engine";

const SCENARIO = "consumer_dispute_001";
const KEY = "mezon.mock.v1";

interface StoredSession { id: string; user_id: string; scenario_id: string; locale: Locale; log: LoggedAction[]; started_at: string; finished_at: string | null }
interface StoredAttempt { id: number; user_id: string; scenario_id: string; kind: QuizKind; score: number; max: number; ts: string }
interface Db { users: Record<string, { display_name: string | null; created_at: string }>; sessions: Record<string, StoredSession>; attempts: StoredAttempt[] }

const load = (): Db => {
  try { return { users: {}, sessions: {}, attempts: [], ...JSON.parse(localStorage.getItem(KEY) || "{}") }; }
  catch { return { users: {}, sessions: {}, attempts: [] }; }
};
const save = (db: Db) => { try { localStorage.setItem(KEY, JSON.stringify(db)); } catch { /* private mode: keep in memory only */ } };
const delay = (ms = 120) => new Promise((r) => setTimeout(r, ms));
const notFound = (what: string) => new ApiError(404, "NOT_FOUND", what);
const uz = (L: Locale, s: string) => (L === "uz-Cyrl" ? latnToCyrl(s) : s);

function card(L: Locale): ScenarioCard {
  return {
    scenario_id: SCENARIO, title: tx(L, "title"), category: tx(L, "category"), difficulty: "beginner", minutes: 15,
    topics: [tx(L, "topic1"), tx(L, "topic2"), tx(L, "topic3")], cover: null, fictional_notice: tx(L, "fictional"), available: true,
  };
}
const SOON = [
  { id: "consumer_dispute_002", t: "soon.2", c: "category" }, { id: "public_appeal_001", t: "soon.3", c: "soon.cat3" }, { id: "mediation_001", t: "soon.4", c: "soon.cat4" },
];
function soonCards(L: Locale): ScenarioCard[] {
  return SOON.map((s) => ({ scenario_id: s.id, title: tx(L, s.t), category: tx(L, s.c), difficulty: "beginner", minutes: 15, topics: [], cover: null, fictional_notice: tx(L, "fictional"), available: false }));
}

function citation(id: string, L: Locale): CitationView {
  const [key, , num] = id.split(".");
  if (!["CPRL", "CC", "CPC"].includes(key) || !num) throw notFound("citation");
  const parts = { "CPRL.art.X": 3, "CPC.art.Z": 2, "CPC.art.W": 4 }[id] ?? 2;
  return {
    citation_id: id, article_id: 400 + num.charCodeAt(0), document_key: key, document_title: actTitle(L, key),
    document_type: key === "CPRL" ? "law" : "code", document_number: null, article_number: num, article_title: null, chapter: null,
    part: null, parts: Array.from({ length: parts }, (_, i) => ({ part_number: i + 1, kind: "text", text: "" })), text: "",
    language: L, is_official_text: null, edition: { effective_from: null, effective_to: null, status: "current" },
    source_url: "https://lex.uz/", last_verified_at: "2026-11-20", translation_note: null,
  };
}

function gameState(sess: StoredSession, L: Locale): GameState {
  const { state, events } = replay(sess.log, L);
  const info = stageInfo(state, L);
  return {
    session_id: sess.id, scenario_id: sess.scenario_id, locale: L, stage: state.stage, stage_title: info.title,
    stage_index: info.index, stage_count: info.count, score: state.score, max_score: MAX_SCORE,
    evidence: state.evidence.map((id) => ({ id, title: tx(L, "ev." + id), type: "document" as const, reviewed: state.reviewed.includes(id), presented: state.presented.includes(id) })),
    available_actions: availableActions(state, L), events, finished: state.finished, legal_date: LEGAL_DATE,
  };
}

function getSession(db: Db, id: string) { const s = db.sessions[id]; if (!s) throw notFound("session"); return s; }

function levelLabel(L: Locale, score: number | null) {
  if (score === null) return tx(L, "level.none");
  return tx(L, "level." + Math.min(3, Math.floor(score / 26)));
}

/* ---------------- mentor (scripted, grounded in the session result) ---------------- */
async function* mentorStream(question: string, sessionId: string | null, L: Locale): AsyncGenerator<MentorEvent> {
  const q = question.toLowerCase();
  const db = load(); const sess = sessionId ? db.sessions[sessionId] : undefined;
  const ev = sess ? evaluate(replay(sess.log, sess.locale).state, L) : null;
  const legal = /(sud|суд|dalil|доказ|modda|статья|stat|nuqson|недостат|kafolat|гарант|ekspert|эксперт|iltimos|ходатай|yutqaz|проигр|talab|требован|xato|ошиб|boshqacha|иначе|telefon|телефон|isteʼmol|потреб)/i.test(q + question);
  await delay(350);
  if (!legal) {
    yield { event: "sources", data: [] };
    yield { event: "done", data: { insufficient_sources: true, ai_unavailable: false, message: uz(L, L === "ru" ? "В загруженной правовой базе недостаточно источников, чтобы ответить на этот вопрос." : "Yuklangan huquqiy bazada bu savolga javob beriş uçun manba yetarli emas."), disclaimer: "" } };
    return;
  }
  const sources = ["CPC.art.W", "CPC.art.Z", "CPRL.art.X"].map((id, i) => ({ source_id: "c" + (i + 1), citation: citation(id, L) }));
  yield { event: "sources", data: sources };
  const ru = L === "ru";
  const blocks: { text: string; source_ids: string[] }[] = [];
  const miss = new Set(ev?.mistakes.map((m) => m.category) ?? []);
  if (/(dalil|доказ|hisobga|учёл|учел)/i.test(q)) {
    blocks.push({ text: ru ? "Ключевые доказательства по делу: кассовый чек (факт и дата покупки) и переписка с продавцом (своевременное обращение)." : "Işdagi asosiy dalillar: kassa çeki (xarid fakti va sanasi) va sotuvçi bilan yozişma (öz vaqtida murojaat).", source_ids: ["c2"] });
    if (miss.has("evidence")) blocks.push({ text: ru ? "Вы представили не все из них, поэтому часть обстоятельств осталась неподтверждённой." : "Siz ularning hammasini taqdim etmadingiz, şuning uçun ayrim holatlar tasdiqlanmay qoldi.", source_ids: ["c2"] });
  } else if (/(modda|статья|stat|norma|норм)/i.test(q)) {
    blocks.push({ text: ru ? "Права покупателя при недостатке товара регулирует закон о защите прав потребителей, а порядок доказывания и ходатайств — Гражданский процессуальный кодекс." : "Tovar nuqsoni böyiça xaridor huquqlari isteʼmolçilar huquqlarini himoya qiliş töğrisidagi qonunda, isbotlaş va iltimosnomalar tartibi esa Fuqarolik protsessual kodeksida.", source_ids: ["c3", "c2"] });
  } else {
    blocks.push({ text: ru ? "Главным спорным вопросом была причина поломки: продавец утверждал, что телефон повредил покупатель." : "Asosiy nizoli masala nosozlik sababi edi: sotuvçi telefonni xaridor buzgan, deb taʼkidladi.", source_ids: [] });
    if (miss.has("procedure")) blocks.push({ text: ru ? "Чтобы установить причину недостатка, сторона может попросить суд назначить экспертизу. Вы не заявили это ходатайство, поэтому вопрос остался открытым." : "Nosozlik sababini aniqlaş uçun tomon suddan ekspertiza tayinlaşni söraşi mumkin. Siz bu iltimosnomani bildirmadingiz, şuning uçun masala oçiq qoldi.", source_ids: ["c1"] });
    else blocks.push({ text: ru ? "Вы заявили ходатайство об экспертизе, и заключение подтвердило заводской дефект. Это был решающий шаг." : "Siz ekspertiza haqida iltimosnoma bildirdingiz va xulosa zavod nuqsonini tasdiqladi. Bu hal qiluvçi qadam böldi.", source_ids: ["c1"] });
    if (miss.has("remedy_choice")) blocks.push({ text: ru ? "Итоговое требование не совпало с целью покупателя: он хотел вернуть деньги." : "Yakuniy talab xaridor maqsadiga mos kelmadi: u pulni qaytarişni xohlagan edi.", source_ids: ["c3"] });
    else blocks.push({ text: ru ? "Требование о возврате денег вы выбрали правильно: закон даёт покупателю такое право при недостатке товара." : "Pulni qaytariş talabini töğri tanladingiz: qonun nuqsonli tovar böyiça xaridorga şunday huquq beradi.", source_ids: ["c3"] });
  }
  for (const b of blocks) { await delay(500); yield { event: "block", data: { text: uz(L, b.text), source_ids: b.source_ids, verified: true } }; }
  await delay(150);
  yield { event: "done", data: { insufficient_sources: false, ai_unavailable: false, disclaimer: uz(L, ru ? "Образовательное объяснение, не юридическая консультация" : "Taʼlim maqsadidagi tuşuntiriş, yuridik maslahat emas") } };
}

/* ---------------- free questions to characters (scripted; the live backend classifies with an LLM) ---------------- */
const CHARACTERS = ["judge", "plaintiff_rep", "plaintiff", "defendant_rep", "expert"];
interface NpcQ { id: string; kw: RegExp; uz: string; ru: string; action?: string }
const NPC_QUESTIONS: Record<string, NpcQ[]> = {
  plaintiff: [
    { id: "q_defect", kw: /(nosoz|buz|quvvat|zaryad|nuqson|suv|nam|nima b[öo'ʻ]|слом|неисправ|заряж|недостат|случил|произош|вод|влаг|намок)/i,
      uz: "Telefonni sotib olganimdan ön kun ötib, u quvvatlanmay qoldi. Men uni tuşirmaganman, suvga ham tuşmagan.",
      ru: "Через десять дней после покупки телефон перестал заряжаться. Я его не ронял, и в воду он не попадал." },
    { id: "q_complaint", kw: /(sotuv[çc]|murojaat|talabnoma|yozdi|qa[çc]on|претенз|обрат|продав|писал|когда)/i,
      uz: "Öşa kuniyoq sotuvçiga yozdim, keyin yozma talabnoma topşirdim. Yozişma telefonimda saqlangan.",
      ru: "В тот же день написал продавцу, потом подал письменную претензию. Переписка сохранилась." },
    { id: "q_docs", kw: /([çc]ek|kafolat|hujjat|şartnoma|shartnoma|talon|чек|гарант|документ|договор|талон)/i,
      uz: "Kassa çeki va kafolat taloni menda. Oldi-sotdi şartnomasi ham bor.",
      ru: "Кассовый чек и гарантийный талон у меня. Договор купли-продажи тоже есть." },
    { id: "q_goal", kw: /(xohla|istay|pul|qaytar|almaştir|almashtir|хотит|хочет|деньг|вернуть|замен|цель)/i,
      uz: "Pulimni qaytarişsa bas. Bu dökondan boşqa telefon olmoqçi emasman.",
      ru: "Хочу вернуть деньги. Другой телефон в этом магазине брать не хочу." },
  ],
  defendant_rep: [
    { id: "q_service", kw: /(servis|mustaqil|ekspert|kim tek|tek[şs]ir|сервис|независим|эксперт|кто провер|провер)/i, action: "ask_defendant",
      uz: "Tekşiruvni dökonimizning öz servis markazi ötkazgan. Mustaqil ekspertiza ötkazilmagan.",
      ru: "Проверку проводил собственный сервисный центр магазина. Независимой экспертизы не было." },
    { id: "q_basis", kw: /(nega|nima uçun|nima uchun|sabab|rad|ayb|почему|причин|отказ|вин)/i,
      uz: "Servis markazimiz xulosasiça, nosozlik mexanik taʼsir natijasida yuzaga kelgan. Şuning uçun bu kafolat holati emas.",
      ru: "По заключению нашего сервисного центра поломка вызвана механическим воздействием. Поэтому это не гарантийный случай." },
    { id: "q_proof", kw: /(dalil|isbot|dalolatnoma|доказ|акт|подтверд)/i,
      uz: "Bizda servis markazining dalolatnomasi bor. Boşqa dalil taqdim etmaymiz.",
      ru: "У нас есть акт сервисного центра. Других доказательств мы не представляем." },
  ],
};
const NPC_UNKNOWN = { uz: "Keçirasiz, savolingizni tuşunmadim. Iltimos, boşqaça sörang.", ru: "Извините, я не понял вопрос. Спросите, пожалуйста, иначе." };

/** Mock accounts: progress made as a guest moves to the account on sign-in (the live backend does the same). */
export function mergeMockGuest(guestId: string | null, accountId: string) {
  if (!guestId || guestId === accountId) return;
  const db = load();
  for (const s of Object.values(db.sessions)) if (s.user_id === guestId) s.user_id = accountId;
  for (const a of db.attempts) if (a.user_id === guestId) a.user_id = accountId;
  save(db);
}

export const mockApi: Api = {
  async health() { await delay(); return { status: "ok", db: true, articles: 0, chunks: 0, scenarios: 1, llm_configured: false, embedder: "mock" }; },

  async createUser(display_name = null) {
    await delay(); const db = load(); const user_id = crypto.randomUUID(); const created_at = new Date().toISOString();
    db.users[user_id] = { display_name, created_at }; save(db); return { user_id, display_name, created_at };
  },

  async scenarios(L) { await delay(); return [card(L), ...soonCards(L)]; },

  async scenario(id, L): Promise<ScenarioDetail> {
    await delay(); if (id !== SCENARIO) throw notFound("scenario");
    const ch = (id: string, sprite: string) => ({ id, name: tx(L, `char.${id}.name`), role: tx(L, `char.${id}.role`), sprite });
    return {
      scenario_id: SCENARIO, title: tx(L, "title"), fictional_notice: tx(L, "fictional"), legal_date: LEGAL_DATE, story: tx(L, "story"),
      player_role: { character_id: "plaintiff_rep", title: tx(L, "role") },
      characters: [ch("judge", "judge"), ch("plaintiff_rep", "lawyer_a"), ch("plaintiff", "citizen_m"), ch("defendant_rep", "lawyer_b"), ch("expert", "expert")],
      claims: [{ side: "plaintiff", text: tx(L, "claim_plaintiff") }, { side: "defendant", text: tx(L, "claim_defendant") }],
      documents: ["contract", "receipt", "warranty", "chat", "claim_letter"].map((d) => ({ id: d, title: tx(L, "ev." + d) })),
      legal_acts: ["CPRL", "CC", "CPC"].map((k) => ({ document_key: k, title: actTitle(L, k), source_url: "https://lex.uz/" })),
    };
  },

  async quiz(scenarioId, kind, L) {
    await delay(); if (scenarioId !== SCENARIO) throw notFound("quiz");
    const questions = QUIZ.map((q) => { const [text, opts] = L === "ru" ? q.ru : q.uz;
      return { question_id: q.id, text: uz(L, text), options: opts.map((o, i) => ({ id: "abc"[i], text: uz(L, o) })) }; });
    return { scenario_id: scenarioId, kind, questions, total: questions.length };
  },

  async submitQuiz(scenarioId, body, L) {
    await delay(); const db = load();
    const review = QUIZ.map((q) => ({ question_id: q.id, chosen_option: body.answers[q.id] ?? null, correct: body.answers[q.id] === q.correct,
      correct_option: q.correct, explanation: uz(L, (L === "ru" ? q.ru : q.uz)[2]), citation_ids: [...q.cite] }));
    const score = review.filter((r) => r.correct).length; const max = QUIZ.length;
    const attempt: StoredAttempt = { id: db.attempts.length + 1, user_id: body.user_id, scenario_id: scenarioId, kind: body.kind, score, max, ts: new Date().toISOString() };
    db.attempts.push(attempt); save(db);
    let learning_gain = null;
    if (body.kind === "post") {
      const pre = [...db.attempts].reverse().find((a) => a.user_id === body.user_id && a.scenario_id === scenarioId && a.kind === "pre");
      if (pre) learning_gain = { pre: pre.score, post: score, max, delta: score - pre.score, note: tx(L, "gain_note") };
    }
    return { attempt_id: attempt.id, score, max, review, learning_gain };
  },

  async createSession({ user_id, scenario_id, locale }) {
    await delay(); if (scenario_id !== SCENARIO) throw notFound("scenario");
    const db = load(); const id = crypto.randomUUID();
    db.sessions[id] = { id, user_id, scenario_id, locale, log: [], started_at: new Date().toISOString(), finished_at: null };
    save(db); return gameState(db.sessions[id], locale);
  },

  async session(id, L) { await delay(80); const s = getSession(load(), id); return gameState(s, L ?? s.locale); },

  async setSessionLocale(id, L) {
    await delay(80); const db = load(); const s = getSession(db, id); s.locale = L; save(db); return gameState(s, L);
  },

  async act(id, actionId, params) {
    await delay(150); const db = load(); const s = getSession(db, id);
    const before = replay(s.log, s.locale).state;
    if (before.finished) throw new ApiError(409, "SESSION_FINISHED", "Session finished");
    const entry = { action_id: actionId, params: params ?? null };
    try { replay([...s.log, entry], s.locale); } catch (e) {
      if (e instanceof IllegalAction) throw new ApiError(409, "ILLEGAL_ACTION", "Action not available", { action_id: actionId, stage: e.stage });
      throw e;
    }
    s.log.push(entry);
    const next = replay(s.log, s.locale).state;
    if (next.finished) s.finished_at = new Date().toISOString();
    save(db); return gameState(s, s.locale);
  },

  async askNpc(id, character, text): Promise<NpcAnswer> {
    await delay(500); const s = getSession(load(), id);
    const { state } = replay(s.log, s.locale);
    if (state.finished) throw new ApiError(409, "SESSION_FINISHED", "Session finished");
    if (!CHARACTERS.includes(character)) throw notFound("character");
    const q0 = text.trim(); if (!q0 || q0.length > NPC_MAX_LEN) throw new ApiError(422, "VALIDATION_ERROR", "text");
    const hit = NPC_QUESTIONS[character]?.find((q) => q.kw.test(q0.toLowerCase()));
    const L = s.locale; const line = hit ?? NPC_UNKNOWN;
    const available = new Set(availableActions(state, L).map((a) => a.action_id));
    return {
      speaker: character, text: uz(L, L === "ru" ? line.ru : line.uz), question_id: hit?.id ?? "unknown",
      fact_ids: hit ? ["F_" + hit.id.toUpperCase()] : [], ai_generated: false,
      suggested_action_id: hit?.action && available.has(hit.action) ? hit.action : null,
    };
  },

  async result(id, L): Promise<SessionResult> {
    await delay(); const s = getSession(load(), id); const loc = L ?? s.locale;
    const { state } = replay(s.log, loc);
    if (!state.finished) throw new ApiError(409, "SESSION_NOT_FINISHED", "Session not finished");
    const ev = evaluate(state, loc);
    const cites = [...new Set(ev.decisions.flatMap((d) => d.citation_ids))];
    return {
      session_id: s.id, scenario_id: s.scenario_id, ...ev, score: state.score, max_score: MAX_SCORE,
      time_spent_sec: Math.max(1, Math.round((Date.parse(s.finished_at ?? s.started_at) - Date.parse(s.started_at)) / 1000)),
      citations: cites.map((c) => citation(c, loc)), disclaimer: tx(loc, "disclaimer"),
    };
  },

  async citation(id, _date, L) { await delay(80); return citation(id, L); },

  async dashboard(userId, L): Promise<DashboardOut> {
    await delay(); const db = load();
    const mine = Object.values(db.sessions).filter((s) => s.user_id === userId && s.finished_at);
    const completed = mine.map((s) => { const st = replay(s.log, L).state; const e = evaluate(st, L);
      return { session_id: s.id, scenario_id: s.scenario_id, title: tx(L, "title"), outcome: e.outcome, outcome_title: e.outcome_title, score: st.score, max_score: MAX_SCORE, finished_at: s.finished_at! }; })
      .sort((a, b) => b.finished_at.localeCompare(a.finished_at));
    const pre = [...db.attempts].reverse().find((a) => a.user_id === userId && a.kind === "pre");
    const post = [...db.attempts].reverse().find((a) => a.user_id === userId && a.kind === "post");
    const counts: Record<string, number> = {};
    for (const s of mine) for (const m of evaluate(replay(s.log, L).state, L).mistakes) counts[m.category] = (counts[m.category] ?? 0) + 1;
    const scores = [...completed.map((c) => c.score / c.max_score), ...(post ? [post.score / post.max] : [])];
    const level = scores.length ? Math.round((scores.reduce((a, b) => a + b, 0) / scores.length) * 100) : null;
    return {
      user: { user_id: userId, display_name: db.users[userId]?.display_name ?? null },
      knowledge_level: { score: level, label: levelLabel(L, level) },
      completed,
      learning_gain: pre && post ? [{ scenario_id: SCENARIO, pre: pre.score, post: post.score, max: post.max, note: tx(L, "gain_note") }] : [],
      mistake_categories: Object.entries(counts).map(([category, count]) => ({ category, title: category, count })).sort((a, b) => b.count - a.count),
      recommended: completed.length ? soonCards(L) : [card(L)],
    };
  },

  async document(scenarioId, evidenceId, L) {
    await delay(60); if (scenarioId !== SCENARIO) throw notFound("document");
    return tx(L, "doc." + evidenceId).split("\n");
  },

  mentor(body) { return mentorStream(body.question, body.session_id, body.locale); },

  async events() { /* analytics are dropped in mock mode */ },
};
