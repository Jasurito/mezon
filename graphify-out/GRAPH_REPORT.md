# Graph Report - mezon  (2026-11-21)

## Corpus Check
- 321 files · ~136,026 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3450 nodes · 9372 edges · 142 communities (118 shown, 24 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1024 edges (avg confidence: 0.91)
- Token cost: 215,447 input · 0 output

## Community Hubs (Navigation)
- History Store & NPC Asking
- Mentor API & Scenario Registry
- Scenario Schema & Tests
- Results, Quiz & API Client
- Analytics & Dashboard
- Legal Data Pipeline Docs
- Game Engine Core
- Auth Form & UI Primitives
- Engine Replay Tests
- Frontend Dependencies
- Scenario Loader
- Legal Citation Service
- CI/CD Workflow
- Specs & Setup Docs
- Ingestion Runs
- Test Fixtures
- Email Auth Tests
- Google OAuth
- Community 18
- Seed Dump
- Settings & Fonts
- Game API Presenter
- NPC Tests
- Mentor Reranking
- Auth API & Sessions
- Errors & CSRF
- Query Normalization
- Community 27
- Config & LLM
- Phaser Courtroom
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
- Specs & Setup Docs
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
- Court Play Screen
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
- Community 107
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
- Community 120
- Community 121
- Community 122
- CI/CD Workflow
- Community 124
- Community 125

## God Nodes (most connected - your core abstractions)
1. `Settings` - 130 edges
2. `run()` - 52 edges
3. `User` - 44 edges
4. `HistoryStore` - 43 edges
5. `IngestionError` - 43 edges
6. `Scenario` - 37 edges
7. `apply()` - 37 edges
8. `Event` - 35 edges
9. `initial_state()` - 35 edges
10. `react` - 35 edges

## Surprising Connections (you probably didn't know these)
- `GoogleOAuth` --conceptually_related_to--> `authlib (Starlette integration)`  [AMBIGUOUS]
  backend/app/auth/google.py → frontend/AUTH.md
- `ArticlePart` --implements--> `article_parts table`  [INFERRED]
  backend/app/models/legal.py → docs/INGESTION.md
- `EmbeddingCache` --implements--> `legal_data/processed/embeddings_cache/ (vector cache)`  [INFERRED]
  ingestion/legal_ingestion/embed.py → docs/DATA.md
- `Settings` --implements--> `CORS_ORIGINS (frontend address)`  [INFERRED]
  backend/app/config.py → docs/BACKEND.md
- `Settings` --implements--> `RAG_MIN_SCORE (relevance threshold)`  [INFERRED]
  backend/app/config.py → docs/BACKEND.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **AI mentor answer flow: detect language -> normalize -> classify -> hybrid search -> threshold refusal -> source-tagged context -> structured blocks -> validation -> SSE** — docs_backend_query_language_detection, docs_backend_query_normalization, docs_backend_query_classification, docs_backend_hybrid_search, docs_backend_insufficient_sources_refusal, docs_backend_source_tags_as_data, docs_backend_structured_answer_blocks, docs_backend_answer_block_validation, docs_backend_mentor_sse_events [EXTRACTED 1.00]
- **Edition verification flow: run (pending_review) -> human review of check_report.md -> fill verified_by in sources.yaml -> activate -> seed-dump** — docs_data_run_command, docs_data_check_report, docs_data_human_review_fields, docs_ingestion_activate_command, docs_data_make_seed_dump [EXTRACTED 1.00]
- **User journey: Landing -> Cases -> Case intro -> Pretest -> Play -> Results -> Posttest / Mentor -> Dashboard** — docs_frontend_landing_screen, docs_frontend_cases_screen, docs_frontend_case_intro_screen, docs_frontend_quiz_screens, docs_frontend_court_simulator_screen, docs_frontend_results_screen, docs_frontend_mentor_screen, docs_frontend_dashboard_screen [EXTRACTED 1.00]
- **Legal ingestion pipeline: validate -> parse -> normalize -> segment -> version -> chunk -> embed -> load -> link -> check** — docs_ingestion_validate_step, docs_ingestion_parse_step, docs_ingestion_normalize_step, docs_ingestion_segment_step, docs_ingestion_version_step, docs_ingestion_chunk_step, docs_ingestion_embed_step, docs_ingestion_load_step, docs_ingestion_link_step, docs_ingestion_check_step [EXTRACTED 1.00]
- **First local run: backend/.venv -> .env from .env.example -> Docker Desktop -> make demo-laws -> make dev-all** — docs_setup_backend_venv, docs_setup_env_file, docs_setup_docker_desktop, docs_setup_make_demo_laws, docs_setup_make_dev_all [EXTRACTED 1.00]
- **Case materials document flow: CaseFile panel -> api.document -> GET /api/sessions/{session_id}/evidence/{evidence_id} -> get_evidence_document -> build_evidence_document -> EvidenceDocument lines** — docs_frontend_case_file, frontend_components_play_case_file_casefile, frontend_lib_api_types_api_document, docs_backend_get_api_sessions_session_id_evidence_evidence_id, backend_app_api_sessions_get_evidence_document, backend_app_services_presenter_build_evidence_document, docs_backend_evidence_document [INFERRED 0.85]
- **Ingestion pipeline run by make ingest ARGS="run": parse -> segment -> chunk -> embed -> load -> link -> check** — docs_data_pipeline_overview, ingestion_legal_ingestion_parse, ingestion_legal_ingestion_segment, ingestion_legal_ingestion_chunk, ingestion_legal_ingestion_embed, ingestion_legal_ingestion_load, ingestion_legal_ingestion_link, ingestion_legal_ingestion_check [INFERRED 0.85]

## Communities (142 total, 24 thin omitted)

### Community 0 - "History Store & NPC Asking"
Cohesion: 0.05
Nodes (16): ingest(), ask(), gen(), format_sse(), get_event_db_factory(), open_db(), _recorder(), record() (+8 more)

### Community 1 - "Mentor API & Scenario Registry"
Cohesion: 0.09
Nodes (13): post_events(), get_current_user(), get_optional_user(), get_viewer(), require_path_session(), require_path_user(), Viewer, get_settings() (+5 more)

### Community 2 - "Scenario Schema & Tests"
Cohesion: 0.06
Nodes (35): Action, _always(), Card, Character, Chose, Claim, Condition, DecisionPoint (+27 more)

### Community 3 - "Results, Quiz & API Client"
Cohesion: 0.09
Nodes (33): CasePage(), fmt(), PretestPage(), CasesPage(), DashboardPage(), fmt(), Block, label() (+25 more)

### Community 4 - "Analytics & Dashboard"
Cohesion: 0.08
Nodes (30): build_dashboard(), _category_title(), _latest_attempts(), _level_label(), get_quiz(), _quiz_questions(), submit_attempt(), round_half_up() (+22 more)

### Community 5 - "Legal Data Pipeline Docs"
Cohesion: 0.07
Nodes (50): CC - Civil Code of Uzbekistan, consumer_dispute_001 (Faulty smartphone case), CPC - Civil Procedure Code of Uzbekistan, CPRL - Law of Uzbekistan 'On Consumer Rights Protection', EMBEDDER (embedding model selection), GET /api/scenarios/{scenario_id}, Add a new law or edition (save lex.uz HTML -> name and place in raw/ -> update sources.yaml -> run --doc -> human review + activate -> citations.yaml, ingest-check, seed-dump), legal_data/processed/check_report.md (integrity report, prints edition version ids) (+42 more)

### Community 6 - "Game Engine Core"
Cohesion: 0.09
Nodes (30): eval_condition(), HasFacts, _add_score(), _award_forecasts(), _enter(), _freeze(), _run_effects(), _settle() (+22 more)

### Community 7 - "Auth Form & UI Primitives"
Cohesion: 0.07
Nodes (26): SignInPage(), SignUpPage(), Auth form error messages (429 rate limit, 422 validation, network errors), AuthForm(), done(), google(), submit(), validate() (+18 more)

### Community 8 - "Engine Replay Tests"
Cohesion: 0.09
Nodes (34): apply(), available_actions(), initial_state(), _is_available(), replay(), LoggedAction, play(), scenario() (+26 more)

### Community 9 - "Frontend Dependencies"
Cohesion: 0.05
Nodes (49): Node 24 (used in frontend/Dockerfile; not pinned in frontend/package.json), Toaster(), eslintConfig, dependencies, cn@^0.5.2, lucide-react@^1.76.0, next@16.4.6, next-intl@4.15.3 (+41 more)

### Community 10 - "Scenario Loader"
Cohesion: 0.08
Nodes (27): collect_text_keys(), iter_text_keys(), load_all(), load_scenario_dir(), LoadedScenario, _read_json(), ScenarioValidationError, export_schemas() (+19 more)

### Community 11 - "Legal Citation Service"
Cohesion: 0.08
Nodes (27): fallback_language_note(), language_name(), unconfirmed_note(), _build(), get_article_view(), get_citation_view(), get_citation_views(), get_legal_acts() (+19 more)

### Community 12 - "CI/CD Workflow"
Cohesion: 0.05
Nodes (46): VM1_SSH_KEY (GitHub Actions secret), defaults, if, name, needs, runs-on, services, steps (+38 more)

### Community 13 - "Specs & Setup Docs"
Cohesion: 0.08
Nodes (41): env_file, path, required, ADOLAT Backend specification (BACKEND.md), ADOLAT (legal-education court simulator), ANTHROPIC_API_KEY, anthropic SDK, CORS_ORIGINS (frontend address) (+33 more)

### Community 14 - "Ingestion Runs"
Cohesion: 0.11
Nodes (31): main(), run(), statuses(), test_cli_draft_activate_refused_outside_demo_database(), test_draft_activate_in_demo_database_is_idempotent_and_check_still_fails(), test_draft_activate_promotes_already_loaded_pending(), test_draft_activate_refused_outside_demo_database(), test_dump_guard_passes_for_verified() (+23 more)

### Community 15 - "Test Fixtures"
Cohesion: 0.08
Nodes (18): create_app(), get_now(), api(), Clock, clock(), game_client(), make_client(), _make() (+10 more)

### Community 16 - "Email Auth Tests"
Cohesion: 0.08
Nodes (35): app(), app_and_client(), app_factory(), client(), login(), make_account(), make(), make_guest() (+27 more)

### Community 17 - "Google OAuth"
Cohesion: 0.11
Nodes (25): GoogleProfile, pkce_challenge(), safe_next(), OAuthState, assert_failed(), callback(), start(), test_bad_id_token_rejected() (+17 more)

### Community 18 - "Community 18"
Cohesion: 0.09
Nodes (29): loaded(), mistake_titles(), _opt(), path(), play(), loaded(), _result(), test_counterfactual_only_when_not_best_and_kind_is_exposed() (+21 more)

### Community 19 - "Seed Dump"
Cohesion: 0.08
Nodes (15): log(), main(), make seed-dump (build legal_data/seed.sql.gz: legal-table data with vectors, no schema; needs the db container), dump_seed(), pg_dump_command(), sequence_fixups(), alembic_config(), create_migrated_database() (+7 more)

### Community 20 - "Settings & Fonts"
Cohesion: 0.08
Nodes (33): commissioner, fontVariables, nunito, onest, oswald, plexMono, plexSans, serif (+25 more)

### Community 21 - "Game API Presenter"
Cohesion: 0.09
Nodes (28): create_user(), ActionParams, ActionRequest, ActionView, CharacterView, ClaimView, CreateSession, CreateUser (+20 more)

### Community 22 - "NPC Tests"
Cohesion: 0.08
Nodes (19): NpcAnswer, NpcAskRequest, NpcClassification, NpcReply, NpcFakeLLM, npc_events(), test_event_recorded(), test_llm_bad_or_failed_reply_falls_back() (+11 more)

### Community 23 - "Mentor Reranking"
Cohesion: 0.13
Nodes (27): LLM, get_reranker(), _llm_factory(), LLMReranker, NullReranker, order_by_scores(), Reranker, RerankItem (+19 more)

### Community 24 - "Auth API & Sessions"
Cohesion: 0.10
Nodes (13): me(), account_out(), create_email_user(), find_by_email(), GoogleLinkError, upsert_google_user(), email_hash(), create_session() (+5 more)

### Community 25 - "Errors & CSRF"
Cohesion: 0.08
Nodes (21): AppError, CsrfError, DbUnavailableError, EmailExistsError, error_response(), ForbiddenError, IllegalActionError, install_error_handlers() (+13 more)

### Community 26 - "Query Normalization"
Cohesion: 0.09
Nodes (21): rrf(), rrf_score(), cyr_to_lat(), lat_to_cyr(), normalize(), tokenize(), _ranks(), SearchOutcome (+13 more)

### Community 27 - "Community 27"
Cohesion: 0.12
Nodes (15): Paths, chunk_edition(), EditionOutcome, parse_edition(), prepare_edition(), RunResult, segment_edition(), validate() (+7 more)

### Community 28 - "Config & LLM"
Cohesion: 0.10
Nodes (8): get_article(), get_citation(), search(), embedder_dep(), Embedder, get_embedder(), NullEmbedder, GET /api/legal/articles/{article_id}

### Community 29 - "Phaser Courtroom"
Cohesion: 0.08
Nodes (24): Courtroom characters and animations (judge, player, plaintiff, defendant rep, witness/expert, secretary), Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses), Phaser court scene (640x360, pixelArt, Scale.FIT), Court(), Props, bubble(), CAST, CourtHandle (+16 more)

### Community 30 - "Community 30"
Cohesion: 0.12
Nodes (17): _check_citations(), _check_counts(), _check_db(), CheckResult, _clip(), find_gaps(), Issue, _label() (+9 more)

### Community 31 - "Community 31"
Cohesion: 0.10
Nodes (16): _activate(), build_parser(), add(), _common(), _debug_steps(), _dispatch(), _paths(), _session_factory() (+8 more)

### Community 32 - "Community 32"
Cohesion: 0.10
Nodes (14): _base(), _clear_bind(), _fail(), google_callback(), get_google(), GoogleError, GoogleOAuth, clear_cookie() (+6 more)

### Community 33 - "Community 33"
Cohesion: 0.13
Nodes (22): AppLayout(), NotFound(), Failed Google sign-in returns to /?auth_error=google (explained by components/site/auth-error-notice.tsx), AuthErrorNotice(), DeskHeader(), LanguageSwitcher(), LOCALE_LABELS, SiteFooter() (+14 more)

### Community 34 - "Community 34"
Cohesion: 0.06
Nodes (9): get_summary(), upgrade(), upgrade(), _int(), upgrade(), upgrade(), GET /api/analytics/scenarios/{scenario_id}/summary (P1), Participant 3 (API, models, game engine, analytics owner) (+1 more)

### Community 35 - "Community 35"
Cohesion: 0.10
Nodes (15): EmbedderError, OllamaEmbedder, test_connection_error_is_embedder_error(), test_embed_batches_and_request_shape(), test_embed_empty_makes_no_request(), test_embed_query_returns_vector(), test_errors_raise_in_embed_and_skip_in_query(), test_registry() (+7 more)

### Community 36 - "Community 36"
Cohesion: 0.17
Nodes (16): merge_guest(), _stats_row(), Event, GameSession, QuizAttempt, User, UserStats, test_events_without_session() (+8 more)

### Community 37 - "Community 37"
Cohesion: 0.18
Nodes (22): AnthropicLLM, MentorAnswer, names(), call(), cls(), FakeAnthropic, good_answer(), mentor_events() (+14 more)

### Community 38 - "Community 38"
Cohesion: 0.11
Nodes (13): google_start(), login(), logout(), _open_session(), signup(), _ua(), check(), clear_failures() (+5 more)

### Community 39 - "Community 39"
Cohesion: 0.12
Nodes (27): allowed_origins(), csrf_guard(), origin_of(), AuthProviderDisabledError, AUTH_IP_MAX_REQUESTS=120 per 15 min (code default 30), /etc/mezon/backend.env (backend secrets, chmod 600), Backend-owned sign-in (/api/auth/*, cookie mezon_session), CSRF Origin check (POSTs from any other Origin get 403 CSRF_FAILED) (+19 more)

### Community 40 - "Community 40"
Cohesion: 0.19
Nodes (15): create_user(), get_evidence_document(), get_loaded(), get_result(), _get_session(), get_state(), load_replayed(), _log() (+7 more)

### Community 41 - "Community 41"
Cohesion: 0.14
Nodes (24): _check_graph(), collect_citation_ids(), _conditions(), _dump(), _dups(), _effect_lists(), _mentioned_citations(), validate_scenario() (+16 more)

### Community 42 - "Community 42"
Cohesion: 0.19
Nodes (17): Base, Article, ArticlePart, Chunk, Citation, DocumentVersion, LegalDocument, _article() (+9 more)

### Community 43 - "Community 43"
Cohesion: 0.11
Nodes (24): FakeEmbedder, client(), dense_client(), factory(), make(), search(), test_dense_adds_to_sparse_score(), test_dense_branch_orders_by_vector() (+16 more)

### Community 44 - "Community 44"
Cohesion: 0.06
Nodes (31): CI frontend job (pnpm i18n check, typecheck, build), outputs, runs-on, concurrency, cancel-in-progress, group, environment, if (+23 more)

### Community 45 - "Community 45"
Cohesion: 0.11
Nodes (14): Edition, _load(), load_edition(), LoadResult, lookup_existing(), _set_if_changed(), _update_existing(), upsert_document() (+6 more)

### Community 46 - "Community 46"
Cohesion: 0.11
Nodes (28): test_document_locale_and_unknown(), test_documents_follow_the_case_file(), 503 DB_UNAVAILABLE (no database connection), Uniform error envelope {error: {code, message, details}}, GET /api/sessions/{session_id}/evidence/{evidence_id}, 409 ILLEGAL_ACTION, 404 NOT_FOUND (no scenario, session or citation), POST /api/sessions/{session_id}/actions (+20 more)

### Community 47 - "Community 47"
Cohesion: 0.11
Nodes (13): classify_question(), load_session_context(), SessionContext, _article_label(), _call_mentor(), _history(), MentorPlan, prepare() (+5 more)

### Community 48 - "Community 48"
Cohesion: 0.12
Nodes (15): allowed_questions(), answer_question(), _choice_model(), classify_lexical(), classify_llm(), NpcResult, _numbers(), rephrase() (+7 more)

### Community 49 - "Community 49"
Cohesion: 0.08
Nodes (14): get_dashboard(), get_quiz(), post_attempt(), GET /api/quiz/{scenario_id}?kind=pre|post, GET /api/users/{user_id}/dashboard, Legal literacy level (0-100), Learning gain (post - pre), POST /api/quiz/{scenario_id}/attempts (+6 more)

### Community 50 - "Community 50"
Cohesion: 0.16
Nodes (23): action(), broken(), has(), stage(), test_add_evidence_unknown(), m(), test_citation_not_listed(), test_collectors() (+15 more)

### Community 51 - "Community 51"
Cohesion: 0.12
Nodes (14): detect_language(), base_normalize(), Candidate, doc_title(), load_items(), make_snippet(), _parts_label(), search_legal() (+6 more)

### Community 52 - "Community 52"
Cohesion: 0.08
Nodes (29): NEXT_PUBLIC_API_MODE, args, context, environment, healthcheck, image, ports, volumes (+21 more)

### Community 53 - "Community 53"
Cohesion: 0.11
Nodes (8): _dummy_hash(), loose_email(), normalize_email(), verify_password(), AccountUser, _lenient_uuid(), LoginIn, SignupIn

### Community 54 - "Community 54"
Cohesion: 0.08
Nodes (26): ActionView, GameEvent (say, react, stage_changed, evidence_added, score, legal_note, mistake), GameState, ActionKind, ActionView, ArticlePartView, CharacterView, Difficulty (+18 more)

### Community 55 - "Community 55"
Cohesion: 0.16
Nodes (14): hybrid_search(), matches_document(), dense(), exact(), prefix_stem(), _run(), scenario_chunks(), Scope (+6 more)

### Community 56 - "Community 56"
Cohesion: 0.15
Nodes (14): test_same_log_same_state(), test_everything_translated(), test_uz_cyrl_falls_back(), _err(), session(), test_decision_without_valid_option_is_illegal(), test_illegal_action(), test_not_found() (+6 more)

### Community 57 - "Community 57"
Cohesion: 0.12
Nodes (17): bootstrap.sh script, vm1 deployment (CI/CD + systemd), CI deploy job (rsync to /opt/mezon/src + ssh sudo mezon-deploy), /etc/mezon/frontend.build.env (NEXT_PUBLIC_API_MODE=mock|live, NEXT_PUBLIC_GOOGLE_AUTH; missing keys are appended), Frontend -> real backend (NEXT_PUBLIC_API_MODE=live in frontend.build.env, baked in at build time), Manual deploy (Actions -> CI/CD -> Run workflow: all, frontend or backend), VM1_KNOWN_HOSTS (GitHub Actions variable), API_MODE (+9 more)

### Community 58 - "Community 58"
Cohesion: 0.13
Nodes (25): tx(), action(), apply(), availableActions(), EngineState, evaluate(), IllegalAction, initial() (+17 more)

### Community 59 - "Community 59"
Cohesion: 0.16
Nodes (17): load_sources(), blocks(), document_entry(), html_doc(), version_entry(), write_docx(), write_source(), write_sources_yaml() (+9 more)

### Community 60 - "Community 60"
Cohesion: 0.12
Nodes (13): find_missing_citations(), load_from_roots(), load_registry(), scenario_roots(), _copy_as(), _no_db(), test_duplicate_scenario_id_across_roots_is_error(), test_load_registry_uses_all_roots() (+5 more)

### Community 61 - "Community 61"
Cohesion: 0.14
Nodes (13): get_user(), _get_user(), get_user_sessions(), _outcome_title(), patch_user(), _profile(), SessionAction, events table (analytics) (+5 more)

### Community 62 - "Community 62"
Cohesion: 0.13
Nodes (19): CitationView, Edition status (current | historical | unconfirmed), GET /api/legal/citations/{citation_id}, GET /api/sessions/{session_id}/result, AI Legal Mentor RAG pipeline, Mentor SSE events (sources, block, done, error), Participant 2 (legal/, rag/, ai/ and ingestion pipeline owner), POST /api/mentor/ask (text/event-stream) (+11 more)

### Community 63 - "Community 63"
Cohesion: 0.13
Nodes (10): AccountArea(), initials(), Avatar(), AvatarFallback(), DropdownMenu(), DropdownMenuContent(), DropdownMenuItem(), DropdownMenuLabel() (+2 more)

### Community 64 - "Community 64"
Cohesion: 0.10
Nodes (21): CHARACTERS, citation(), Db, delay(), getSession(), load(), mentorStream(), mergeMockGuest() (+13 more)

### Community 65 - "Community 65"
Cohesion: 0.12
Nodes (10): EvidenceDocument, EvidenceView, OptionView, ScenarioCard, build_evidence_document(), build_scenario_card(), present_actions(), present_evidence() (+2 more)

### Community 66 - "Community 66"
Cohesion: 0.12
Nodes (14): hash_password(), NEXT_PUBLIC_GOOGLE_AUTH (build-time flag; the Google button is hidden until true), Accounts and Google SSO (AUTH.md), AccountUser {id, display_name, email, provider, avatar_url?}, GET /api/auth/google/start, GET /api/auth/me, 'Continue with Google' shown only with NEXT_PUBLIC_GOOGLE_AUTH=true, Ministry of Justice (jury and track) (+6 more)

### Community 67 - "Specs & Setup Docs"
Cohesion: 0.13
Nodes (18): Monorepo layout (frontend/ Next.js 16 + Phaser 4, backend/ FastAPI + Postgres/pgvector + MongoDB history, deploy/vm1/ systemd + CI/CD, docs/ specs), FastAPI, locale parameter (ru | uz-Latn | uz-Cyrl), Participant 4 (legal content, localization texts, Legal QA), PATCH /api/sessions/{session_id}, ADOLAT Frontend specification (FRONTEND.md), Palette (navy #0F1B2D, gold #C9A227, warm white #F5F1E8, teal #1FA39A, terracotta #C8553D), Generated API client (openapi-typescript + openapi-fetch, make api-client) (+10 more)

### Community 68 - "Community 68"
Cohesion: 0.15
Nodes (15): build_draft(), _d(), _empty(), merge_existing(), merge(), _note(), PageInfo, _q() (+7 more)

### Community 69 - "Community 69"
Cohesion: 0.13
Nodes (15): ArticleRef, canonical_number(), DocHint, extract_article_numbers(), extract_refs(), _hint_in(), _numbers(), strip_source_marks() (+7 more)

### Community 70 - "Community 70"
Cohesion: 0.19
Nodes (13): EXAMPLES, Msg, NpcPanel(), fmt(), LegalPanel(), Sheet(), SheetContent(), SheetDescription() (+5 more)

### Community 71 - "Community 71"
Cohesion: 0.18
Nodes (9): build_mentor_system(), build_mentor_user(), render_sources(), SourceForPrompt, build_rerank_user(), CandidateForPrompt, escape_attr(), sanitize_text() (+1 more)

### Community 72 - "Community 72"
Cohesion: 0.16
Nodes (6): create_session(), get_evidence_document(), get_result(), get_session(), patch_session(), post_action()

### Community 73 - "Community 73"
Cohesion: 0.13
Nodes (18): GET /api/health, GET /api/scenarios, Case selection screen /[locale]/cases, Landing screen /[locale], Landing(), cache, CaseCaption(), CaseCover() (+10 more)

### Community 74 - "Community 74"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 75 - "Community 75"
Cohesion: 0.15
Nodes (7): _article_keys(), _chunk_keys(), _dedupe(), load_gold(), rank_all(), run_eval(), test_eval_without_gold_file_gives_clear_message()

### Community 76 - "Community 76"
Cohesion: 0.18
Nodes (7): MongoHistoryStore, run(), mongo_store(), mongo_docs(), _snapshot_mongo(), test_live_session_document_grows_and_finishes(), test_push_step_is_idempotent()

### Community 77 - "Community 77"
Cohesion: 0.19
Nodes (10): _classes(), _Collector, _inline_text(), iter_lexuz(), parse_docx(), parse_file(), parse_html(), _parse_lexuz() (+2 more)

### Community 78 - "Community 78"
Cohesion: 0.12
Nodes (10): normalize_number(), _ord_alt(), _ord_alt_ru(), to_roman(), blocks(), html(), test_chapter_patterns(), test_section_patterns() (+2 more)

### Community 79 - "Community 79"
Cohesion: 0.16
Nodes (11): backfill(), BackfillResult, post_quiz(), play_everything(), test_activity_has_all_types(), test_backfill_fills_gaps_next_to_live_records(), test_backfill_inmemory(), test_backfill_rebuilds_mongo() (+3 more)

### Community 80 - "Community 80"
Cohesion: 0.18
Nodes (11): OllamaLLM, call(), make(), reply(), test_bad_json_and_schema_mismatch(), test_http_500(), test_mentor_ask_end_to_end_with_ollama(), handler() (+3 more)

### Community 81 - "Community 81"
Cohesion: 0.11
Nodes (19): entrypoint.sh script, build, depends_on, environment, extra_hosts, ports, volumes, condition (+11 more)

### Community 82 - "Community 82"
Cohesion: 0.14
Nodes (16): convertPlain(), convertWord(), fit(), IOTATED, isUpper(), latnToCyrl(), LETTERS, NEW_LETTERS (+8 more)

### Community 83 - "Community 83"
Cohesion: 0.15
Nodes (9): main(), build(), alembic_config(), client(), db_engine(), db_session(), db_url(), make_alembic_config() (+1 more)

### Community 84 - "Community 84"
Cohesion: 0.18
Nodes (10): clean_text(), normalize_blocks(), test_normalize_keeps_lex_id(), test_segment_lexuz(), _blocks(), test_chunks(), test_clean_text_only_junk(), test_parse_html_fallback_to_body_when_no_selector() (+2 more)

### Community 85 - "Community 85"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 87 - "Community 87"
Cohesion: 0.21
Nodes (7): _ctx(), main(), build_session_doc(), event_dicts(), session_doc(), step_doc(), build_store()

### Community 88 - "Community 88"
Cohesion: 0.31
Nodes (13): RerankScore, RerankScores, article_numbers(), baseline(), last_first(), make_llm(), mentor_event(), set_settings() (+5 more)

### Community 89 - "Community 89"
Cohesion: 0.16
Nodes (5): _article_exists(), CitationEntry, link_citations(), LinkError, _to_str()

### Community 90 - "Community 90"
Cohesion: 0.20
Nodes (9): missing_citation_ids(), CitationCheckError, _drop(), _ids(), test_all_scenario_citations_resolve(), test_invalid_scenario_stops_startup(), test_startup_fails_on_missing_citation(), test_startup_ok_when_not_strict() (+1 more)

### Community 91 - "Community 91"
Cohesion: 0.29
Nodes (11): build_game_state(), _loaded(), _state(), test_decision_options_translated(), test_events_translated_and_typed(), test_evidence_visible_from_second_stage_with_flags(), test_finished_state_has_no_actions(), test_initial_state_stage_and_evidence() (+3 more)

### Community 92 - "Community 92"
Cohesion: 0.24
Nodes (11): as_token(), calls(), do(), test_account_session_may_use_guest_ids(), test_expired_session_loses_access(), test_guests_work_without_login(), test_no_session_gets_401(), test_other_account_gets_403() (+3 more)

### Community 93 - "Community 93"
Cohesion: 0.22
Nodes (10): Api, stats(), test_profile_404_and_validation(), test_profile_get_patch(), test_stats_after_three_playthroughs_and_quiz(), test_stats_unfinished_session_counts_only_started(), test_streak_by_utc_days(), touch() (+2 more)

### Community 94 - "Community 94"
Cohesion: 0.14
Nodes (11): volumes, mongodata, pgdata, legal_data/processed/*.articles.jsonl (parsed articles, source of article numbers), legal_data/processed/embeddings_cache/ (vector cache), Legal data not in git (processed/*.jsonl, processed/embeddings_cache/, seed.sql.gz via Git LFS), Seed stored in Git LFS (.gitattributes; git pull fetches it when git-lfs is installed), ingest docker compose service (tools profile) (+3 more)

### Community 95 - "Court Play Screen"
Cohesion: 0.21
Nodes (10): Askable, NAMES, Dialog(), DialogContent(), DialogDescription(), DialogFooter(), DialogHeader(), DialogOverlay() (+2 more)

### Community 96 - "Community 96"
Cohesion: 0.16
Nodes (3): session_history(), _usable(), user_activity()

### Community 97 - "Community 97"
Cohesion: 0.30
Nodes (8): article_label(), build_chunks(), _clean(), doc_title_for(), estimate_tokens(), make_header(), _text(), _tokens()

### Community 98 - "Community 98"
Cohesion: 0.22
Nodes (10): Add a new case (copy test_consumer -> change scenario_id and texts -> citations in citations.yaml + make demo-laws -> make demo starts cleanly), --draft-activate flag (drafts loaded as active only into demo DB adolat_demo), backend/tests/fixtures/scenarios/test_consumer/ (case template to copy), texts.ru.json and texts.uz-Latn.json (case texts, both languages required), Embedding model role (articles and questions -> vectors for semantic search), adolat_demo demo database (draft loading allowed only for DB names ending in _demo), make demo (backend only, with demo data), make demo-laws (load real laws from legal_data/ into adolat_demo as drafts) (+2 more)

### Community 99 - "Community 99"
Cohesion: 0.26
Nodes (9): call(), LEGAL_KEYS, newLatinTexts(), sse(), TEXT_KEYS, uzLatnUi(), ApiError, EvidenceDocument (+1 more)

### Community 100 - "Community 100"
Cohesion: 0.17
Nodes (7): AccountUser, auth, AuthError, liveAuth, mockAuth, req(), UserStore

### Community 101 - "Community 101"
Cohesion: 0.23
Nodes (6): _Draft, _finish(), segment(), _structural(), test_segment_chapter_title_on_next_line(), test_segment_dash_number_kept_and_duplicates_reported()

### Community 102 - "Community 102"
Cohesion: 0.44
Nodes (9): FakeLLM, MentorBlock, QueryClassification, concept(), mentor_events(), test_all_blocks_dropped_means_insufficient(), test_general_block_without_sources_is_allowed(), test_model_may_declare_insufficient_sources() (+1 more)

### Community 103 - "Community 103"
Cohesion: 0.17
Nodes (3): get_history(), NullHistoryStore, test_null_store_history_from_postgres()

### Community 105 - "Community 105"
Cohesion: 0.18
Nodes (4): hclient(), _make(), settable_clock(), SettableClock

### Community 106 - "Community 106"
Cohesion: 0.23
Nodes (12): CI backend job (critical pytest with a Postgres 16 + pgvector service), DATABASE_URL (Postgres), Explicit article reference lookup ('st. 15', '15-modda'), GET /api/legal/search, Hybrid legal search (explicit refs + vector top 30 + full-text/trigram top 30), pg_trgm, pgvector, PostgreSQL 16 (+4 more)

### Community 107 - "Community 107"
Cohesion: 0.27
Nodes (6): get_llm(), first(), test_no_key_means_no_llm(), test_no_key_message_follows_question_language(), test_no_key_returns_sources_and_ai_unavailable(), test_no_key_still_applies_threshold()

### Community 108 - "Community 108"
Cohesion: 0.49
Nodes (5): on_quiz_attempt(), on_session_finished(), on_session_started(), _row(), _touch()

### Community 109 - "Community 109"
Cohesion: 0.31
Nodes (10): Mezon: notes for Claude Code (CLAUDE.md), graphify-out/graph.html (interactive graph view), graphify-out/graph.json (graph data used by graphify query), graphify-out/GRAPH_REPORT.md (communities, god nodes, surprising connections, open questions), graphify CLI (graphify query / path / explain), Committed graphify knowledge graph (graphify-out/), Graphify local state in graphify-out/ (cache, manifest), git-ignored, /graphify skill (.claude/skills/graphify, installs graphifyy on first use) (+2 more)

### Community 110 - "Community 110"
Cohesion: 0.33
Nodes (8): dash(), quiz(), test_dashboard_404(), test_dashboard_after_three_games(), test_dashboard_uz_latn(), test_knowledge_level_labels(), test_new_user_dashboard(), test_recommended_reasons()

### Community 111 - "Community 111"
Cohesion: 0.22
Nodes (3): fake(), FakeGoogle, gapp()

### Community 114 - "Community 114"
Cohesion: 0.22
Nodes (8): ACT_TITLES, actTitle(), Dict, QUIZ, RU, UZ, StoredSession, Locale

### Community 116 - "Community 116"
Cohesion: 0.36
Nodes (4): ActivityItem, ActivityOut, HistoryStepOut, SessionHistoryOut

### Community 117 - "Community 117"
Cohesion: 0.39
Nodes (5): PatchUser, UserProfileOut, UserSessionItem, UserSessionsOut, UserStatsOut

### Community 121 - "Community 121"
Cohesion: 0.33
Nodes (3): test_golden_path_via_api(), test_result_label_is_localized(), test_users_and_scenarios()

### Community 122 - "Community 122"
Cohesion: 0.29
Nodes (6): allowBuilds, @parcel/watcher, sharp, @swc/core, unrs-resolver, minimumReleaseAgeExclude

### Community 123 - "CI/CD Workflow"
Cohesion: 0.47
Nodes (3): get_url(), run_migrations_offline(), run_migrations_online()

### Community 124 - "Community 124"
Cohesion: 0.33
Nodes (4): pnpm via corepack (corepack pnpm ..., pnpm@11.25.0 in package.json), packageManager, COREPACK_ENABLE_DOWNLOAD_PROMPT, dev-all.sh script

### Community 125 - "Community 125"
Cohesion: 0.67
Nodes (3): npx, next-devtools, shadcn

## Ambiguous Edges - Review These
- `GoogleOAuth` → `authlib (Starlette integration)`  [AMBIGUOUS]
  frontend/AUTH.md · relation: conceptually_related_to
- `courtroom.ts` → `Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `types.ts` → `Generated API client (openapi-typescript + openapi-fetch, make api-client)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `sessions table (game sessions)` → `Opaque revocable server sessions (30-day sliding expiry)`  [AMBIGUOUS]
  frontend/AUTH.md · relation: conceptually_related_to
- `In-browser mock backend (localStorage)` → `Thin client: no game logic or scenario texts in the frontend`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `Uzbek Cyrillic -> Latin transliteration table (search only)` → `Uzbek Latin 2026 alphabet (law of 21.10.2026)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to

## Knowledge Gaps
- **13 isolated node(s):** `adolat-ingestion`, `multilingual-e5-large (local, passage:/query: prefixes)`, `Palette (navy #0F1B2D, gold #C9A227, warm white #F5F1E8, teal #1FA39A, terracotta #C8553D)`, `Participant 1 (frontend owner)`, `Next.js agent rules (AGENTS.md)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1010 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Community 32` to `History Store & NPC Asking`, `Mentor API & Scenario Registry`, `Legal Data Pipeline Docs`, `Scenario Loader`, `Specs & Setup Docs`, `Ingestion Runs`, `Test Fixtures`, `Email Auth Tests`, `Google OAuth`, `NPC Tests`, `Mentor Reranking`, `Auth API & Sessions`, `Errors & CSRF`, `Query Normalization`, `Config & LLM`, `Community 31`, `Community 35`, `Community 36`, `Community 37`, `Community 38`, `Community 39`, `Community 47`, `Community 48`, `Community 51`, `Community 55`, `Community 60`, `Community 62`, `Community 75`, `Community 80`, `Community 83`, `Community 87`, `Community 88`, `Community 106`, `Community 107`, `Community 111`, `Community 112`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Are the 72 inferred relationships involving `Settings` (e.g. with `classify_question()` and `get_llm()`) actually correct?**
  _`Settings` has 72 INFERRED edges - model-reasoned connections that need verification._
- **What connects `adolat-ingestion`, `multilingual-e5-large (local, passage:/query: prefixes)`, `Palette (navy #0F1B2D, gold #C9A227, warm white #F5F1E8, teal #1FA39A, terracotta #C8553D)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `History Store & NPC Asking` be split into smaller, more focused modules?**
  _Cohesion score 0.048484848484848485 - nodes in this community are weakly interconnected._
- **Why does `Accounts and Google SSO (AUTH.md)` connect `Community 66` to `Community 33`, `Results, Quiz & API Client`, `Community 100`, `Specs & Setup Docs`, `Community 39`, `Auth Form & UI Primitives`, `Auth API & Sessions`, `Community 57`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `GoogleOAuth` and `authlib (Starlette integration)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `courtroom.ts` and `Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._