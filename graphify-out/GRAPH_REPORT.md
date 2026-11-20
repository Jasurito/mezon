# Graph Report - mezon  (2026-11-20)

## Corpus Check
- 251 files · ~194,046 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 23 file(s) not represented in the graph (top: (none) 9, .css 4, .service 4)

## Summary
- 2425 nodes · 6548 edges · 134 communities (106 shown, 28 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 549 edges (avg confidence: 0.91)
- Token cost: 273,977 input · 0 output

## Community Hubs (Navigation)
- Mentor RAG Tests
- Backend Test Fixtures
- Frontend API Contract
- i18n & Navigation
- NPC Questions
- Quiz & Results UI
- Legal Citation Service
- MongoDB History Store
- Mentor Answer Pipeline
- Auth & UI Primitives
- Frontend Dependencies
- Docker Compose Services
- API Routers & Registry
- User Profile & Stats
- LLM Settings & Clients
- Game API Schemas
- Settings & Fonts
- Court Play Screen
- Hybrid Legal Search
- Game Engine Core
- Game Session Service
- Legal Corpus Models
- Scenario Schema
- Engine Replay & Determinism
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 53
- Community 54
- Community 55
- Community 56
- Community 57
- Community 58
- Community 59
- Community 60
- Community 61
- Community 62
- Community 63
- Community 64
- Community 65
- Community 66
- Community 67
- Community 68
- Community 69
- Community 70
- Community 71
- Community 72
- Community 73
- Community 74
- Community 75
- Community 76
- Community 77
- Community 78
- Community 79
- Community 80
- Community 81
- Community 82
- Community 83
- Community 84
- Community 85
- Community 86
- Community 87
- Community 88
- Community 89
- Community 90
- Community 91
- Community 92
- Community 93
- Community 94
- Community 95
- Community 96
- Community 97
- Community 98
- Community 99
- Community 100
- Community 101
- Community 102
- Community 103
- Community 104
- Community 105
- Community 106
- Community 108
- Community 109
- Community 110
- Community 111
- Community 112
- Community 113
- Community 114
- Community 115
- Community 116
- Community 117
- Community 118
- Community 133

## God Nodes (most connected - your core abstractions)
1. `Settings` - 63 edges
2. `HistoryStore` - 44 edges
3. `apply()` - 38 edges
4. `Scenario` - 36 edges
5. `Button()` - 36 edges
6. `Event` - 35 edges
7. `LoadedScenario` - 33 edges
8. `initial_state()` - 32 edges
9. `react` - 31 edges
10. `prepare()` - 29 edges

## Surprising Connections (you probably didn't know these)
- `sanitize_text()` --implements--> `<source> tags treated as data, not instructions`  [INFERRED]
  backend/app/ai/prompts/sanitize.py → docs/BACKEND.md
- `eval_condition()` --implements--> `JSON condition DSL (all, any, not, flag, gte, always)`  [INFERRED]
  backend/app/game_engine/conditions.py → docs/BACKEND.md
- `ArticlePart` --implements--> `article_parts table`  [INFERRED]
  backend/app/models/legal.py → docs/INGESTION.md
- `rrf()` --implements--> `Reciprocal Rank Fusion (RRF)`  [INFERRED]
  backend/app/rag/fusion.py → docs/BACKEND.md
- `extract_refs()` --implements--> `Explicit article reference lookup ('st. 15', '15-modda')`  [INFERRED]
  backend/app/rag/refs.py → docs/BACKEND.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **User journey: Landing -> Cases -> Case intro -> Pretest -> Play -> Results -> Posttest / Mentor -> Dashboard** — docs_frontend_landing_screen, docs_frontend_cases_screen, docs_frontend_case_intro_screen, docs_frontend_quiz_screens, docs_frontend_court_simulator_screen, docs_frontend_results_screen, docs_frontend_mentor_screen, docs_frontend_dashboard_screen [EXTRACTED 1.00]
- **Legal ingestion pipeline: validate -> parse -> normalize -> segment -> version -> chunk -> embed -> load -> link -> check** — docs_ingestion_validate_step, docs_ingestion_parse_step, docs_ingestion_normalize_step, docs_ingestion_segment_step, docs_ingestion_version_step, docs_ingestion_chunk_step, docs_ingestion_embed_step, docs_ingestion_load_step, docs_ingestion_link_step, docs_ingestion_check_step [EXTRACTED 1.00]
- **AI mentor answer flow: detect language -> normalize -> classify -> hybrid search -> threshold refusal -> source-tagged context -> structured blocks -> validation -> SSE** — docs_backend_query_language_detection, docs_backend_query_normalization, docs_backend_query_classification, docs_backend_hybrid_search, docs_backend_insufficient_sources_refusal, docs_backend_source_tags_as_data, docs_backend_structured_answer_blocks, docs_backend_answer_block_validation, docs_backend_mentor_sse_events [EXTRACTED 1.00]

## Communities (134 total, 28 thin omitted)

### Community 0 - "Mentor RAG Tests"
Cohesion: 0.06
Nodes (78): AnthropicLLM, FakeLLM, RerankScore, RerankScores, HistoryItem, MentorAnswer, MentorBlock, QueryClassification (+70 more)

### Community 1 - "Backend Test Fixtures"
Cohesion: 0.05
Nodes (25): get_event_db_factory(), embedder_dep(), Embedder, get_embedder(), NullEmbedder, api(), Clock, clock() (+17 more)

### Community 2 - "Frontend API Contract"
Cohesion: 0.06
Nodes (29): test_events_without_session(), test_more_than_50_events_is_422(), test_attempt_404s(), Api, test_golden_path_via_api(), test_users_and_scenarios(), test_same_log_same_state(), test_uz_cyrl_falls_back() (+21 more)

### Community 3 - "i18n & Navigation"
Cohesion: 0.09
Nodes (31): AppLayout(), NotFound(), Landing(), AccountArea(), initials(), DeskHeader(), LanguageSwitcher(), LOCALE_LABELS (+23 more)

### Community 4 - "NPC Questions"
Cohesion: 0.07
Nodes (19): ask_npc(), NpcAnswer, NpcAskRequest, NpcClassification, NpcReply, NpcFakeLLM, npc_events(), test_event_recorded() (+11 more)

### Community 5 - "Quiz & Results UI"
Cohesion: 0.15
Nodes (29): Pre-test and post-test screens, CasePage(), fmt(), PretestPage(), CasesPage(), DashboardPage(), fmt(), Block (+21 more)

### Community 6 - "Legal Citation Service"
Cohesion: 0.09
Nodes (27): NotFoundError, _build(), get_article_view(), get_citation_view(), get_citation_views(), get_legal_acts(), _is_valid_on(), missing_citation_ids() (+19 more)

### Community 7 - "MongoDB History Store"
Cohesion: 0.08
Nodes (11): backfill(), BackfillResult, _ctx(), main(), build_store(), activity_key(), _canon_ts(), HistoryStore (+3 more)

### Community 8 - "Mentor Answer Pipeline"
Cohesion: 0.08
Nodes (21): SessionContext, _article_label(), _history(), MentorPlan, prepare(), select_candidates(), _sse_done(), stream_events() (+13 more)

### Community 9 - "Auth & UI Primitives"
Cohesion: 0.09
Nodes (20): SignInPage(), SignUpPage(), AuthForm(), done(), google(), submit(), validate(), GoogleG() (+12 more)

### Community 10 - "Frontend Dependencies"
Cohesion: 0.06
Nodes (43): eslintConfig, dependencies, cn@^0.5.2, lucide-react@^1.76.0, next@16.4.6, next-intl@4.15.3, next-themes@^0.4.6, phaser@4.2.1 (+35 more)

### Community 11 - "Docker Compose Services"
Cohesion: 0.05
Nodes (44): NEXT_PUBLIC_API_MODE, build, depends_on, env_file, environment, extra_hosts, ports, volumes (+36 more)

### Community 12 - "API Routers & Registry"
Cohesion: 0.17
Nodes (5): get_settings(), get_db(), get_history(), get_registry(), get_now()

### Community 13 - "User Profile & Stats"
Cohesion: 0.12
Nodes (18): create_user(), get_user(), _get_user(), get_user_sessions(), _outcome_title(), patch_user(), _profile(), UserStats (+10 more)

### Community 14 - "LLM Settings & Clients"
Cohesion: 0.10
Nodes (11): classify_question(), get_llm(), LLM, _call_mentor(), answer_question(), classify_llm(), rephrase(), OllamaLLM (+3 more)

### Community 15 - "Game API Schemas"
Cohesion: 0.10
Nodes (25): ActionParams, ActionRequest, CharacterView, ClaimView, CreateSession, CreateUser, DecisionView, DocumentView (+17 more)

### Community 16 - "Settings & Fonts"
Cohesion: 0.10
Nodes (27): FONT_VAR, SettingsPage(), LocaleLayout(), viewport, Providers(), SketchSwitcher(), RadioGroup(), RadioGroupItem() (+19 more)

### Community 17 - "Court Play Screen"
Cohesion: 0.14
Nodes (23): PlayPage(), DecisionDialog(), NAMES, PlayScreen(), fmt(), LegalPanel(), Dialog(), DialogContent() (+15 more)

### Community 18 - "Hybrid Legal Search"
Cohesion: 0.11
Nodes (24): FakeEmbedder, client(), dense_client(), factory(), make(), search(), test_dense_adds_to_sparse_score(), test_dense_branch_orders_by_vector() (+16 more)

### Community 19 - "Game Engine Core"
Cohesion: 0.14
Nodes (13): eval_condition(), HasFacts, _is_available(), IllegalAction, ScenarioError, SessionFinished, _chosen(), evaluate() (+5 more)

### Community 20 - "Game Session Service"
Cohesion: 0.21
Nodes (17): safely(), GameSession, SessionAction, create_user(), get_loaded(), get_result(), _get_session(), get_state() (+9 more)

### Community 21 - "Legal Corpus Models"
Cohesion: 0.19
Nodes (16): Article, DocumentVersion, LegalDocument, doc_title(), load_items(), main(), _article(), _cite() (+8 more)

### Community 22 - "Scenario Schema"
Cohesion: 0.12
Nodes (20): allowed_questions(), Action, Card, Character, Chose, Claim, DecisionPoint, EvaluationRule (+12 more)

### Community 23 - "Engine Replay & Determinism"
Cohesion: 0.13
Nodes (17): replay(), LoggedAction, play(), scenario(), to_log(), test_replay_100_times_identical(), test_replay_empty_log_is_initial(), test_replay_equals_sequential_apply() (+9 more)

### Community 24 - "Community 24"
Cohesion: 0.11
Nodes (11): rrf(), rrf_score(), Candidate, hybrid_search(), _ranks(), SearchOutcome, make_snippet(), _parts_label() (+3 more)

### Community 25 - "Community 25"
Cohesion: 0.08
Nodes (24): ActionView, call(), liveApi, sse(), ActionKind, ActionView, ApiError, ArticlePartView (+16 more)

### Community 26 - "Community 26"
Cohesion: 0.13
Nodes (26): tx(), action(), apply(), availableActions(), EngineState, evaluate(), IllegalAction, initial() (+18 more)

### Community 27 - "Community 27"
Cohesion: 0.11
Nodes (7): get_url(), run_migrations_offline(), run_migrations_online(), upgrade(), upgrade(), _int(), upgrade()

### Community 28 - "Community 28"
Cohesion: 0.15
Nodes (17): apply(), available_actions(), _freeze(), initial_state(), _settle(), _Work, test_random_walks_reach_results(), _at_decision() (+9 more)

### Community 29 - "Community 29"
Cohesion: 0.15
Nodes (16): _check_graph(), collect_text_keys(), _conditions(), _dump(), _dups(), _effect_lists(), iter_text_keys(), _mentioned_citations() (+8 more)

### Community 30 - "Community 30"
Cohesion: 0.17
Nodes (22): collect_citation_ids(), action(), broken(), has(), stage(), test_add_evidence_unknown(), m(), test_citation_not_listed() (+14 more)

### Community 31 - "Community 31"
Cohesion: 0.12
Nodes (10): fallback_chain(), translate(), LoadedScenario, EvidenceView, ScenarioCard, build_result(), option_label(), build_scenario_card() (+2 more)

### Community 32 - "Community 32"
Cohesion: 0.13
Nodes (20): volumes, mongodata, pgdata, ADOLAT Legal Ingestion specification (INGESTION.md), activate command (confirm an edition), check step (check.py: integrity checks, check_report.md), diff command (article changes between editions), document_versions table (+12 more)

### Community 33 - "Community 33"
Cohesion: 0.11
Nodes (18): Courtroom characters and animations (judge, player, plaintiff, defendant rep, witness/expert, secretary), Props, bubble(), CAST, CourtHandle, drawPerson(), drawRoom(), furniture() (+10 more)

### Community 34 - "Community 34"
Cohesion: 0.21
Nodes (14): build_dashboard(), _category_title(), _latest_attempts(), _level_label(), message(), ClientEvent, CompletedSession, DashboardLearningGain (+6 more)

### Community 35 - "Community 35"
Cohesion: 0.15
Nodes (15): base_normalize(), cyr_to_lat(), lat_to_cyr(), normalize(), tokenize(), matches_document(), test_matches_document_by_key_and_title(), test_normalize_apostrophes_spaces_case() (+7 more)

### Community 36 - "Community 36"
Cohesion: 0.14
Nodes (21): ADOLAT Frontend specification (FRONTEND.md), ActionMenu, Palette (navy #0F1B2D, gold #C9A227, warm white #F5F1E8, teal #1FA39A, terracotta #C8553D), Court simulator screen /[locale]/play/[sessionId], DECISION modal dialog, DialogueBox, Event queue playback, EvidenceDrawer (+13 more)

### Community 37 - "Community 37"
Cohesion: 0.17
Nodes (10): build_rerank_user(), CandidateForPrompt, get_reranker(), _llm_factory(), LLMReranker, NullReranker, order_by_scores(), Reranker (+2 more)

### Community 38 - "Community 38"
Cohesion: 0.14
Nodes (15): ArticleRef, canonical_number(), DocHint, extract_article_numbers(), extract_refs(), _hint_in(), _numbers(), strip_source_marks() (+7 more)

### Community 39 - "Community 39"
Cohesion: 0.12
Nodes (9): AppError, DbUnavailableError, IllegalActionError, SessionFinishedError, SessionNotFinishedError, SessionOutdatedError, Body, test_app_error() (+1 more)

### Community 40 - "Community 40"
Cohesion: 0.16
Nodes (13): _always(), Condition, Effect, React, Say, test_decision_action_requires_decision_id(), test_exactly_one_key(), test_gte_forms() (+5 more)

### Community 41 - "Community 41"
Cohesion: 0.13
Nodes (14): ANTHROPIC_API_KEY, anthropic SDK, LLM_MODEL_FAST (claude-haiku-5-5), LLM_MODEL_MENTOR (claude-sonnet-5-5), AI Legal Mentor RAG pipeline, Mentor SSE events (sources, block, done, error), Participant 2 (legal/, rag/, ai/ and ingestion pipeline owner), POST /api/mentor/ask (text/event-stream) (+6 more)

### Community 42 - "Community 42"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 43 - "Community 43"
Cohesion: 0.20
Nodes (11): dense(), exact(), prefix_stem(), _run(), scenario_chunks(), Scope, sparse_fts(), sparse_titles() (+3 more)

### Community 44 - "Community 44"
Cohesion: 0.19
Nodes (5): load_session_context(), Base, ArticlePart, Chunk, Citation

### Community 45 - "Community 45"
Cohesion: 0.14
Nodes (16): convertPlain(), convertWord(), fit(), IOTATED, isUpper(), latnToCyrl(), LETTERS, NEW_LETTERS (+8 more)

### Community 46 - "Community 46"
Cohesion: 0.14
Nodes (9): _choice_model(), classify_lexical(), NpcResult, _numbers(), _same_word(), _tokens(), valid_reply(), content_tokens() (+1 more)

### Community 47 - "Community 47"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 48 - "Community 48"
Cohesion: 0.20
Nodes (5): user_activity(), ActivityItem, ActivityOut, HistoryStepOut, SessionHistoryOut

### Community 49 - "Community 49"
Cohesion: 0.21
Nodes (11): get_quiz(), _quiz_questions(), submit_attempt(), User, LearningGainOut, QuizAttemptIn, QuizAttemptOut, QuizOptionOut (+3 more)

### Community 50 - "Community 50"
Cohesion: 0.18
Nodes (5): create_session(), get_result(), get_session(), patch_session(), post_action()

### Community 51 - "Community 51"
Cohesion: 0.29
Nodes (13): _add_score(), _enter(), _run_effects(), AvailableAction, EvidenceAddedEvent, _Frozen, LegalNoteEvent, MistakeEvent (+5 more)

### Community 52 - "Community 52"
Cohesion: 0.25
Nodes (10): load_all(), ScenarioValidationError, copy_fixtures(), edit_json(), test_invalid_scenario_json_collected(), test_load_all_fixtures_ok(), test_missing_cyrl_key_is_only_warning(), test_missing_quiz_key_is_error() (+2 more)

### Community 53 - "Community 53"
Cohesion: 0.16
Nodes (16): actTitle(), citation(), Db, delay(), getSession(), load(), mentorStream(), notFound() (+8 more)

### Community 54 - "Community 54"
Cohesion: 0.13
Nodes (11): /etc/mezon/frontend.build.env, API_MODE, mockApi, auth, AuthError, AuthErrorCode, liveAuth, mockAuth (+3 more)

### Community 56 - "Community 56"
Cohesion: 0.20
Nodes (9): mongo_docs(), play_everything(), _snapshot_mongo(), test_activity_has_all_types(), test_backfill_fills_gaps_next_to_live_records(), test_backfill_inmemory(), test_backfill_rebuilds_mongo(), test_inmemory_store_works_without_mongo() (+1 more)

### Community 57 - "Community 57"
Cohesion: 0.26
Nodes (4): MongoHistoryStore, run(), test_live_session_document_grows_and_finishes(), test_push_step_is_idempotent()

### Community 58 - "Community 58"
Cohesion: 0.18
Nodes (12): GET /api/quiz/{scenario_id}?kind=pre|post, locale parameter (ru | uz-Latn | uz-Cyrl), Participant 4 (legal content, localization texts, Legal QA), PATCH /api/sessions/{session_id}, next-intl (locale in URL), Next.js (App Router), Tailwind CSS, UI locale files (ru.json, uz-Latn.json, uz-Cyrl.json) (+4 more)

### Community 59 - "Community 59"
Cohesion: 0.20
Nodes (7): alembic_config(), db_engine(), db_session(), db_url(), make_alembic_config(), mongo_store(), mongo_url()

### Community 60 - "Community 60"
Cohesion: 0.29
Nodes (11): build_game_state(), _loaded(), _state(), test_decision_options_translated(), test_events_translated_and_typed(), test_evidence_visible_from_second_stage_with_flags(), test_finished_state_has_no_actions(), test_initial_state_stage_and_evidence() (+3 more)

### Community 61 - "Community 61"
Cohesion: 0.20
Nodes (11): CitationView, Edition status (current | historical | unconfirmed), GET /api/legal/citations/{citation_id}, GET /api/legal/search, GET /api/sessions/{session_id}/result, LegalPanel (shared article panel), Results screen /[locale]/results/[sessionId], citation_id (stable article identifier, e.g. CPRL.art.X) (+3 more)

### Community 62 - "Community 62"
Cohesion: 0.21
Nodes (11): POST /api/users, users table, Anonymous user_id in localStorage, Accounts and Google SSO proposal (AUTH.md), AccountUser {id, display_name, email, provider, avatar_url?}, GET /api/auth/me, Ministry of Justice (jury and track), OneID (Uzbekistan government SSO) (+3 more)

### Community 63 - "Community 63"
Cohesion: 0.20
Nodes (6): ingest(), post_events(), Event, EventsIn, EventsOut, POST /api/events (P1)

### Community 64 - "Community 64"
Cohesion: 0.18
Nodes (8): get_dashboard(), QuizAttempt, GET /api/users/{user_id}/dashboard, Legal literacy level (0-100), Learning gain (post - pre), POST /api/quiz/{scenario_id}/attempts, quiz_attempts table, Dashboard screen /[locale]/dashboard

### Community 65 - "Community 65"
Cohesion: 0.19
Nodes (6): ask(), gen(), format_sse(), open_db(), _recorder(), record()

### Community 66 - "Community 66"
Cohesion: 0.35
Nodes (11): broken(), has(), q(), test_character_does_not_know_fact(), test_duplicate_question_id(), m(), test_results_stage_not_allowed(), test_text_keys_collected() (+3 more)

### Community 67 - "Community 67"
Cohesion: 0.15
Nodes (13): ADOLAT Backend specification (BACKEND.md), ADOLAT (legal-education court simulator), Uniform error envelope {error: {code, message, details}}, events table (analytics), FastAPI, GameState, 409 ILLEGAL_ACTION, POST /api/sessions (+5 more)

### Community 68 - "Community 68"
Cohesion: 0.22
Nodes (5): export_schemas(), _Model, Question, Quiz, QuizOption

### Community 69 - "Community 69"
Cohesion: 0.23
Nodes (12): /etc/mezon/backend.env (backend secrets, chmod 600), mezon-backend.service (127.0.0.1:8000), mezon-db.service (Postgres container), mezon-frontend.service (127.0.0.1:3000), mezon.modeus.cc (production site), mezon-mongo.service (MongoDB history), mezon-mongodata docker volume, mezon-pgdata docker volume (+4 more)

### Community 70 - "Community 70"
Cohesion: 0.20
Nodes (3): round_half_up(), scenario_summary(), ScenarioSummary

### Community 71 - "Community 71"
Cohesion: 0.26
Nodes (7): CitationCheckError, _drop(), _ids(), test_all_scenario_citations_resolve(), test_invalid_scenario_stops_startup(), test_startup_fails_on_missing_citation(), test_startup_ok_when_not_strict()

### Community 72 - "Community 72"
Cohesion: 0.29
Nodes (3): bootstrap.sh script, vm1 deployment (CI/CD + systemd), GET /api/health

### Community 73 - "Community 73"
Cohesion: 0.17
Nodes (10): CI deploy job (rsync to /opt/mezon/src + ssh sudo mezon-deploy), CI frontend job (pnpm i18n check, typecheck, lint, build), VM1_KNOWN_HOSTS (GitHub Actions variable), VM1_SSH_KEY (GitHub Actions secret), concurrency, cancel-in-progress, group, name (+2 more)

### Community 74 - "Community 74"
Cohesion: 0.17
Nodes (9): commissioner, fontVariables, nunito, onest, oswald, plexMono, plexSans, serif (+1 more)

### Community 75 - "Community 75"
Cohesion: 0.17
Nodes (12): BE, EVENT, FE, HAS_KEY, INFRA, INPUT_TARGET, NEXT_TELEMETRY_DISABLED, TARGETS (+4 more)

### Community 76 - "Community 76"
Cohesion: 0.18
Nodes (4): get_summary(), GET /api/analytics/scenarios/{scenario_id}/summary (P1), Participant 3 (API, models, game engine, analytics owner), SQL views (v_session_metrics, v_learning_gain, v_mistakes)

### Community 77 - "Community 77"
Cohesion: 0.27
Nodes (6): get_article(), get_citation(), search(), GET /api/legal/articles/{article_id}, article_parts table, articles table

### Community 79 - "Community 79"
Cohesion: 0.25
Nodes (7): error_response(), install_error_handlers(), _app_error(), _db(), _http(), _validation(), _safe_error()

### Community 80 - "Community 80"
Cohesion: 0.35
Nodes (4): build_session_doc(), event_dicts(), session_doc(), step_doc()

### Community 82 - "Community 82"
Cohesion: 0.31
Nodes (8): dash(), quiz(), test_dashboard_404(), test_dashboard_after_three_games(), test_dashboard_uz_latn(), test_knowledge_level_labels(), test_new_user_dashboard(), test_recommended_reasons()

### Community 83 - "Community 83"
Cohesion: 0.24
Nodes (11): CI backend job (pytest with Postgres 16 + pgvector service, docker build), Explicit article reference lookup ('st. 15', '15-modda'), Hybrid legal search (explicit refs + vector top 30 + full-text/trigram top 30), pg_trgm, pgvector, PostgreSQL 16, Optional reranker, Reciprocal Rank Fusion (RRF) (+3 more)

### Community 84 - "Community 84"
Cohesion: 0.22
Nodes (3): SelectContent(), SelectScrollDownButton(), SelectScrollUpButton()

### Community 85 - "Community 85"
Cohesion: 0.18
Nodes (11): target, on, pull_request, push, workflow_dispatch, branches, default, description (+3 more)

### Community 86 - "Community 86"
Cohesion: 0.24
Nodes (4): get_scenario(), list_scenarios(), GET /api/scenarios, Case selection screen /[locale]/cases

### Community 88 - "Community 88"
Cohesion: 0.20
Nodes (3): NullHistoryStore, test_history_endpoint_mongo_matches_postgres(), test_null_store_history_from_postgres()

### Community 89 - "Community 89"
Cohesion: 0.20
Nodes (5): detect_language(), test_detect_language(), test_detect_language_default_is_configurable(), test_extract_article_numbers(), Query language detection (alphabet + stop words)

### Community 90 - "Community 90"
Cohesion: 0.24
Nodes (10): CC - Civil Code of Uzbekistan, consumer_dispute_001 (Faulty smartphone case), CPC - Civil Procedure Code of Uzbekistan, CPRL - Law of Uzbekistan 'On Consumer Rights Protection', GET /api/scenarios/{scenario_id}, Constitution of the Republic of Uzbekistan, legal_documents table, Minimal legal corpus for the scenario (+2 more)

### Community 91 - "Community 91"
Cohesion: 0.39
Nodes (5): authlib (Starlette integration), GET /api/auth/google/callback, GET /api/auth/google/start, Google OAuth 2.0 Authorization Code + PKCE (backend-handled), POST /api/auth/logout

### Community 92 - "Community 92"
Cohesion: 0.22
Nodes (9): defaults, run, defaults, if, name, needs, runs-on, frontend (+1 more)

### Community 93 - "Community 93"
Cohesion: 0.22
Nodes (9): services, POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, env, image, options, ports (+1 more)

### Community 94 - "Community 94"
Cohesion: 0.36
Nodes (9): steps, steps, steps, steps, id, if, name, run (+1 more)

### Community 96 - "Community 96"
Cohesion: 0.29
Nodes (5): Alembic migrations, JSON condition DSL (all, any, not, flag, gte, always), Courtroom stage FSM (INTRO -> CASE_REVIEW -> PREPARATION -> HEARING_OPENING -> PARTY_EXPLANATIONS -> EVIDENCE_EXAMINATION <-> MOTIONS -> DEBATE -> DECISION -> RESULTS), Pydantic v2, Scenario effects (set, unset, score, say, react, add_evidence, mistake, legal_note, goto)

### Community 97 - "Community 97"
Cohesion: 0.25
Nodes (8): environment, if, name, needs, runs-on, name, url, deploy

### Community 99 - "Community 99"
Cohesion: 0.38
Nodes (4): create_app(), _db_opener(), lifespan(), client()

### Community 101 - "Community 101"
Cohesion: 0.29
Nodes (7): GameEvent (say, react, stage_changed, evidence_added, score, legal_note, mistake), LoggedAction, StoredSession, GameEvent, GameState, Locale, GameStore

### Community 102 - "Community 102"
Cohesion: 0.29
Nodes (7): scripts, build, dev, i18n, lint, start, typecheck

### Community 103 - "Community 103"
Cohesion: 0.29
Nodes (6): allowBuilds, @parcel/watcher, sharp, @swc/core, unrs-resolver, minimumReleaseAgeExclude

### Community 104 - "Community 104"
Cohesion: 0.29
Nodes (7): outputs, runs-on, jobs, changes, backend, frontend, infra

### Community 105 - "Community 105"
Cohesion: 0.29
Nodes (7): with, cache, cache-dependency-path, filters, node-version, package_json_file, python-version

### Community 108 - "Community 108"
Cohesion: 0.40
Nodes (3): fallback_language_note(), language_name(), unconfirmed_note()

### Community 109 - "Community 109"
Cohesion: 0.47
Nodes (3): _check(), test_everything_translated(), _texts()

### Community 110 - "Community 110"
Cohesion: 0.33
Nodes (5): ACT_TITLES, Dict, QUIZ, RU, UZ

### Community 112 - "Community 112"
Cohesion: 0.40
Nodes (3): ActionView, OptionView, present_actions()

### Community 113 - "Community 113"
Cohesion: 0.50
Nodes (5): EMBEDDER (embedding model selection), BGE-M3 (local embedding model), embed step (embed.py), Embedder.embed(texts, kind=passage|query), multilingual-e5-large (local, passage:/query: prefixes)

### Community 114 - "Community 114"
Cohesion: 0.40
Nodes (5): if, name, needs, runs-on, backend

### Community 115 - "Community 115"
Cohesion: 0.67
Nodes (3): npx, next-devtools, shadcn

## Ambiguous Edges - Review These
- `courtroom.ts` → `Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `types.ts` → `Generated API client (openapi-typescript + openapi-fetch, make api-client)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `sessions table (game sessions)` → `Opaque revocable server sessions (30-day sliding expiry)`  [AMBIGUOUS]
  frontend/AUTH.md · relation: conceptually_related_to
- `Thin client: no game logic or scenario texts in the frontend` → `In-browser mock backend (localStorage)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `Uzbek Cyrillic -> Latin transliteration table (search only)` → `Uzbek Latin 2026 alphabet (law of 21.10.2026)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to

## Knowledge Gaps
- **18 isolated node(s):** `adolat-backend`, `COREPACK_ENABLE_DOWNLOAD_PROMPT`, `VM1_SSH_KEY (GitHub Actions secret)`, `VM1_KNOWN_HOSTS (GitHub Actions variable)`, `Pydantic v2` (+13 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 762 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `LLM Settings & Clients` to `Mentor RAG Tests`, `Community 65`, `Community 98`, `Backend Test Fixtures`, `NPC Questions`, `Community 37`, `Community 99`, `MongoDB History Store`, `Mentor Answer Pipeline`, `Community 41`, `API Routers & Registry`, `Community 77`, `Community 46`, `Community 113`, `Community 24`, `Community 59`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `Settings` (e.g. with `classify_question()` and `get_llm()`) actually correct?**
  _`Settings` has 23 INFERRED edges - model-reasoned connections that need verification._
- **What connects `adolat-backend`, `COREPACK_ENABLE_DOWNLOAD_PROMPT`, `VM1_SSH_KEY (GitHub Actions secret)` to the rest of the system?**
  _18 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Mentor RAG Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.055405212932630676 - nodes in this community are weakly interconnected._
- **Why does `Mezon frontend README` connect `Community 58` to `Community 32`, `Community 33`, `Community 67`, `Community 36`, `Community 69`, `Community 74`, `Community 45`, `Settings & Fonts`, `Community 54`, `Community 25`, `Community 90`, `Community 61`, `Community 62`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `courtroom.ts` and `Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `types.ts` and `Generated API client (openapi-typescript + openapi-fetch, make api-client)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._