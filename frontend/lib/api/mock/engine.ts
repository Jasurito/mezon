/**
 * Mock game engine for consumer_dispute_001. Same shape as the backend engine:
 * pure functions, state = fold(apply, initial, actionLog), texts localized at output time.
 */
import type { ActionView, DecisionKind, DecisionView, GameEvent, Locale, MistakeView, RecommendationView, ResultKind } from "../types";
import { tx } from "./content";

export const STAGES = ["INTRO", "CASE_REVIEW", "PREPARATION", "HEARING_OPENING", "PARTY_EXPLANATIONS", "EVIDENCE_EXAMINATION", "MOTIONS", "DEBATE", "DECISION"] as const;
export type Stage = (typeof STAGES)[number] | "RESULTS";
export const MAX_SCORE = 100;
export const LEGAL_DATE = "2026-03-01";

export interface EngineState {
  stage: Stage; score: number; reviewed: string[]; evidence: string[]; presented: string[];
  explain?: "good" | "bad"; asked?: boolean; expertise?: boolean | null; debate?: "good" | "bad"; claim?: string; finished: boolean;
}
export interface LoggedAction { action_id: string; params?: { option?: string } | null }

export class IllegalAction extends Error { constructor(public actionId: string, public stage: string) { super("ILLEGAL_ACTION"); } }

const say = (L: Locale, speaker: string, key: string, emotion = "neutral", vars?: Record<string, string>): GameEvent =>
  ({ type: "say", speaker, text: tx(L, key, vars), emotion });
const react = (character: string, reaction: "nod" | "object" | "surprised" | "think" | "gavel"): GameEvent => ({ type: "react", character, reaction });
const note = (L: Locale, citation_id: string, key: string): GameEvent => ({ type: "legal_note", citation_id, text: tx(L, key) });

export function initial(): EngineState {
  return { stage: "INTRO", score: 0, reviewed: [], evidence: ["contract", "receipt", "warranty", "chat", "claim_letter"], presented: [], finished: false };
}
export function introEvents(L: Locale): GameEvent[] {
  return [say(L, "narrator", "line.intro1"), say(L, "plaintiff", "line.intro2", "worried")];
}

function action(L: Locale, id: string, kind: ActionView["kind"], extra: Partial<ActionView> = {}): ActionView {
  return { action_id: id, kind, label: tx(L, "act." + id), target_character: null, evidence_id: null, options: null, hint_citation_ids: [], ...extra };
}

export function availableActions(s: EngineState, L: Locale): ActionView[] {
  switch (s.stage) {
    case "INTRO": return [action(L, "enter_courtroom", "continue")];
    case "CASE_REVIEW": return [action(L, "to_preparation", "continue")];
    case "PREPARATION": {
      const list = (["contract", "receipt", "chat"] as const).filter((d) => !s.reviewed.includes(d))
        .map((d) => action(L, "review_" + d, "evidence", { evidence_id: d }));
      if (s.reviewed.includes("contract") && s.reviewed.includes("receipt")) list.push(action(L, "to_hearing", "continue"));
      return list;
    }
    case "HEARING_OPENING": return [action(L, "to_explanations", "continue")];
    case "PARTY_EXPLANATIONS":
      return s.explain ? [action(L, "to_evidence", "continue")]
        : [action(L, "argue_warranty", "argument", { hint_citation_ids: ["CPRL.art.X"] }), action(L, "argue_emotion", "argument")];
    case "EVIDENCE_EXAMINATION": return [
      ...(!s.presented.includes("receipt") ? [action(L, "present_receipt", "evidence", { evidence_id: "receipt", target_character: "judge", hint_citation_ids: ["CPC.art.Z"] })] : []),
      ...(!s.presented.includes("chat") ? [action(L, "present_chat", "evidence", { evidence_id: "chat", target_character: "judge", hint_citation_ids: ["CPC.art.Z"] })] : []),
      ...(!s.asked ? [action(L, "ask_defendant", "question", { target_character: "defendant_rep" })] : []),
      action(L, "to_motions", "continue"),
    ];
    case "MOTIONS": return [action(L, "request_expertise", "motion", { hint_citation_ids: ["CPC.art.W"] }), action(L, "no_motion", "continue")];
    case "DEBATE": return [action(L, "debate_burden", "argument", { hint_citation_ids: ["CPRL.art.X"] }), action(L, "debate_sympathy", "argument")];
    case "DECISION": return [action(L, "final_claim", "decision", {
      hint_citation_ids: ["CPRL.art.X"],
      options: ["repair", "replace", "reduce", "refund"].map((id) => ({ id, label: tx(L, "opt." + id) })),
    })];
    default: return [];
  }
}

export function apply(s0: EngineState, a: LoggedAction, L: Locale): { state: EngineState; events: GameEvent[] } {
  if (s0.finished || !availableActions(s0, L).some((x) => x.action_id === a.action_id)) throw new IllegalAction(a.action_id, s0.stage);
  const s: EngineState = structuredClone(s0);
  const ev: GameEvent[] = [];
  const score = (n: number) => { s.score = Math.min(MAX_SCORE, s.score + n); ev.push({ type: "score", delta: n, total: s.score }); };
  const stage = (k: Stage) => { s.stage = k; ev.push({ type: "stage_changed", stage: k, title: tx(L, "stage." + k) }); };
  const id = a.action_id;

  if (id.startsWith("review_")) {
    const doc = id.slice(7); const first = s.reviewed.length === 0;
    s.reviewed.push(doc); score(doc === "contract" ? 4 : 3);
    if (first) ev.push(note(L, "CPC.art.Z", "note.review"));
    return { state: s, events: ev };
  }
  switch (id) {
    case "enter_courtroom": stage("CASE_REVIEW"); ev.push(say(L, "judge", "line.review1"), react("defendant_rep", "object"), say(L, "defendant_rep", "line.review2", "defensive")); break;
    case "to_preparation": stage("PREPARATION"); ev.push(say(L, "judge", "line.prep1")); break;
    case "to_hearing": stage("HEARING_OPENING"); ev.push(react("judge", "gavel"), say(L, "judge", "line.open1")); break;
    case "to_explanations": stage("PARTY_EXPLANATIONS"); ev.push(say(L, "judge", "line.open2")); break;
    case "argue_warranty": s.explain = "good"; ev.push(say(L, "plaintiff_rep", "line.argue_warranty", "confident"), react("judge", "nod"), say(L, "defendant_rep", "line.def_position", "defensive")); score(10); ev.push(note(L, "CPRL.art.X", "note.argue_warranty")); break;
    case "argue_emotion": s.explain = "bad"; ev.push(say(L, "plaintiff_rep", "line.argue_emotion", "angry"), react("judge", "think"), say(L, "judge", "line.judge_emotion"), say(L, "defendant_rep", "line.def_position", "defensive")); break;
    case "to_evidence": stage("EVIDENCE_EXAMINATION"); ev.push(say(L, "judge", "line.evidence_start")); break;
    case "present_receipt": s.presented.push("receipt"); ev.push(say(L, "plaintiff_rep", "line.present_receipt", "confident"), react("plaintiff_rep", "object"), react("judge", "nod"), say(L, "judge", "line.accept_receipt")); score(10); ev.push(note(L, "CPC.art.Z", "note.present")); break;
    case "present_chat": s.presented.push("chat"); ev.push(say(L, "plaintiff_rep", "line.present_chat", "confident"), react("judge", "nod"), say(L, "judge", "line.accept_chat")); score(10); ev.push(note(L, "CPC.art.Z", "note.present_chat")); break;
    case "ask_defendant": s.asked = true; ev.push(say(L, "plaintiff_rep", "line.ask"), react("defendant_rep", "object"), say(L, "defendant_rep", "line.def_answer", "defensive"), react("judge", "think"), say(L, "judge", "line.judge_think")); score(5); ev.push(note(L, "CPC.art.Z", "note.ask")); break;
    case "to_motions": stage("MOTIONS"); ev.push(say(L, "judge", "line.motions_start")); break;
    case "request_expertise": s.expertise = true; s.evidence.push("expert_report");
      ev.push(say(L, "plaintiff_rep", "line.request_expertise", "confident"), react("defendant_rep", "surprised"), say(L, "judge", "line.grant_expertise"), { type: "evidence_added", evidence_id: "expert_report" }, say(L, "expert", "line.expert"));
      score(20); ev.push(note(L, "CPC.art.W", "note.expertise")); stage("DEBATE"); ev.push(say(L, "judge", "line.debate_start")); break;
    case "no_motion": s.expertise = false; ev.push(say(L, "judge", "line.no_motion")); stage("DEBATE"); ev.push(say(L, "judge", "line.debate_start")); break;
    case "debate_burden": s.debate = "good"; ev.push(say(L, "plaintiff_rep", "line.debate_burden", "confident"), react("judge", "nod")); score(15); ev.push(note(L, "CPRL.art.X", "note.burden")); stage("DECISION"); ev.push(say(L, "judge", "line.decision_start")); break;
    case "debate_sympathy": s.debate = "bad"; ev.push(say(L, "plaintiff_rep", "line.debate_sympathy"), react("judge", "think"), say(L, "judge", "line.judge_sympathy")); stage("DECISION"); ev.push(say(L, "judge", "line.decision_start")); break;
    case "final_claim": {
      const opt = a.params?.option; if (!opt || !["repair", "replace", "reduce", "refund"].includes(opt)) throw new IllegalAction(id, s.stage);
      s.claim = opt;
      ev.push(say(L, "plaintiff_rep", "line.final", "confident", { label: tx(L, "opt." + opt).toLowerCase() }), say(L, "judge", "line.retire"), react("judge", "gavel"));
      score(opt === "refund" ? 20 : 5);
      s.finished = true; s.stage = "RESULTS"; ev.push({ type: "stage_changed", stage: "RESULTS", title: tx(L, "stage.RESULTS") });
      break;
    }
  }
  return { state: s, events: ev };
}

export function replay(log: LoggedAction[], L: Locale): { state: EngineState; events: GameEvent[] } {
  let state = initial(); let events = introEvents(L);
  for (const a of log) ({ state, events } = apply(state, a, L));
  return { state, events };
}

export function stageInfo(s: EngineState, L: Locale) {
  const i = STAGES.indexOf(s.stage as (typeof STAGES)[number]);
  return { index: i < 0 ? STAGES.length : i + 1, count: STAGES.length, title: tx(L, "stage." + s.stage) };
}

export function outcomeOf(s: EngineState): "claim_granted" | "claim_partially_granted" | "claim_denied" {
  const receipt = s.presented.includes("receipt");
  if (receipt && s.expertise && s.claim === "refund") return "claim_granted";
  if (receipt && (s.claim === "refund" || s.expertise)) return "claim_partially_granted";
  return "claim_denied";
}

export function evaluate(s: EngineState, L: Locale) {
  const evidenceOk = s.presented.includes("receipt") && s.presented.includes("chat");
  const d = (id: string, stage: string, ok: boolean, chosen: string | null, chosenLabel: string, bestLabel: string, cites: string[]): DecisionView =>
    ({ decision_id: id, stage, chosen, chosen_label: chosenLabel, best: "best", best_label: bestLabel, correct: ok, explanation: tx(L, "exp." + id.split("_")[0]), citation_ids: cites });
  const decisions: DecisionView[] = [
    d("explain", "PARTY_EXPLANATIONS", s.explain === "good", s.explain ?? null, tx(L, s.explain ? `dec.explain.${s.explain}` : "dec.none"), tx(L, "dec.explain.good"), ["CPRL.art.X"]),
    d("evidence", "EVIDENCE_EXAMINATION", evidenceOk, evidenceOk ? "good" : "bad", tx(L, evidenceOk ? "dec.evidence.good" : "dec.evidence.bad"), tx(L, "dec.evidence.good"), ["CPC.art.Z"]),
    d("motion", "MOTIONS", !!s.expertise, s.expertise ? "good" : "bad", tx(L, s.expertise ? "dec.motion.good" : "dec.motion.bad"), tx(L, "dec.motion.good"), ["CPC.art.W"]),
    d("debate", "DEBATE", s.debate === "good", s.debate ?? null, tx(L, s.debate ? `dec.debate.${s.debate}` : "dec.none"), tx(L, "dec.debate.good"), ["CPRL.art.X"]),
    d("final", "DECISION", s.claim === "refund", s.claim ?? null, s.claim ? tx(L, "opt." + s.claim) : tx(L, "dec.none"), tx(L, "opt.refund"), ["CPRL.art.X"]),
  ].map((x, i) => ({
    ...x,
    decision_id: ["explain_claim", "present_evidence", "motion_expertise", "debate", "final_claim"][i],
    kind: (["reasoning", "action", "action", "reasoning", "action"] as DecisionKind[])[i],
    counterfactual: x.correct ? null : tx(L, "cf." + x.decision_id.split("_")[0]),
  }));
  const cat: Record<string, string> = { explain: "substantive_law", evidence: "evidence", motion: "procedure", debate: "substantive_law", final: "remedy_choice" };
  const keyOf = ["explain", "evidence", "motion", "debate", "final"];
  const mistakes: MistakeView[] = decisions.flatMap((x, i) => x.correct ? [] : [{
    category: cat[keyOf[i]], title: tx(L, `mis.${keyOf[i]}.title`), explanation: x.explanation, correct_action: tx(L, `mis.${keyOf[i]}.fix`), citation_ids: x.citation_ids,
  }]);
  const recommendations: RecommendationView[] = [];
  if (mistakes.some((m) => m.category === "evidence" || m.category === "procedure")) recommendations.push({ topic: tx(L, "rec.evidence"), citation_ids: ["CPC.art.Z", "CPC.art.W"], scenario_id: null });
  if (mistakes.some((m) => m.category === "substantive_law" || m.category === "remedy_choice")) recommendations.push({ topic: tx(L, "rec.consumer"), citation_ids: ["CPRL.art.X"], scenario_id: null });
  const outcome = outcomeOf(s);
  const result_kind: ResultKind = outcome === "claim_granted" ? "win" : outcome === "claim_partially_granted" ? "partial" : "loss";
  return {
    outcome, result_kind, result_label: tx(L, "kind." + result_kind), outcome_title: tx(L, "outcome." + outcome), ruling_text: tx(L, "ruling." + outcome),
    decisions, mistakes, recommendations,
    correct_decision_rate: Math.round((decisions.filter((x) => x.correct).length / decisions.length) * 100) / 100,
  };
}
