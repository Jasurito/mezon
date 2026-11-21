# Graph Report - mezon  (2026-11-21)

## Corpus Check
- 339 files · ~137,326 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 26 file(s) not represented in the graph (top: (none) 11, .service 5, .example 4)

## Summary
- 3598 nodes · 10510 edges · 151 communities (127 shown, 24 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1263 edges (avg confidence: 0.91)
- Token cost: 1,090,603 input · 0 output

## Graph Freshness
- Built from commit: `122366d2`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_mentor_flow.py
- situation-screen.tsx
- scenario.py
- HistoryStore
- test_registry_paths.py
- api/mentor.py
- account-menu.tsx
- analytics/quiz.py
- evaluate
- react
- load.py
- ai/mentor.py
- package.json
- search.py
- search
- game/conftest.py
- vm1 deployment (CI/CD + systemd)
- test_consumer_moisture.py
- test_rent_deposit.py
- game.ts
- cli.py
- app/errors.py
- test_wedding_photo.py
- game_engine/__init__.py
- test_npc_flow.py
- run
- test_google.py
- Scenario
- next-intl
- ai/npc.py
- Auth security basics (state/PKCE check, next-path validation, CSRF, rate limiting)
- Legal ingestion pipeline (10 steps)
- check.py
- Court simulator screen /[locale]/play/[sessionId] (main screen; SituationScreen for kind: "situation" cases)
- legal_ingestion/pipeline.py
- test_email_auth.py
- api.py
- play-screen.tsx
- User
- game.py
- lib/settings.ts
- test_search.py
- presenter.py
- sqlalchemy
- test_ollama_adapter.py
- .start
- CI deploy job (main only: rsync to /opt/mezon/src + ssh sudo mezon-deploy --sha <sha> <backend|frontend|all>)
- rag/rerank.py
- builder.py
- engine/test_validate.py
- retrieve.py
- api/users.py
- load_sources
- get_dashboard
- test_history_store.py
- service.py
- DocumentVersion
- db
- types.ts
- test_lexuz.py
- engine.ts
- make demo-laws (load real laws from legal_data/ into adolat_demo as drafts)
- Settings
- Claude Haiku 5.5 via Anthropic API key (claude-haiku-5-5 for LLM_MODEL_MENTOR and LLM_MODEL_FAST)
- mock/index.ts
- courtroom.ts
- schemas/quiz.py
- OllamaEmbedder
- apply
- re
- create_session
- load_seed.py
- GoogleOAuth
- uuid
- components.json
- translit.ts
- sqlalchemy_orm
- ratelimit.py
- Cases in scenarios/ (one folder per case with scenario.json, quiz.json, texts.ru.json, texts.uz-Latn.json; not stored in git)
- ask_npc
- compilerOptions
- test_embed_db.py
- test_parse_segment.py
- AI Legal Mentor RAG pipeline
- auth-form.tsx
- Api
- ingestion/tests/conftest.py
- Viewer
- Api
- test_phone_life.py
- Mezon frontend README
- sanitize_text
- QueryClassification
- translate
- pytest
- test_access.py
- POST /api/sessions
- live.ts
- typing
- api/history.py
- auth/conftest.py
- passwords.py
- auth/sessions.py
- legal_data/seed.sql.gz (demo seed)
- results/[sessionId]/page.tsx
- test_rerank.py
- test_mentor_rerank.py
- load_all
- get_summary
- build_game_state
- .play
- InMemoryHistoryStore
- stats.py
- Committed graphify knowledge graph (graphify-out/)
- npc/test_schema.py
- FakeGoogle
- test_quiz.py
- content.ts
- get_scenario
- target
- test_health.py
- history/conftest.py
- scripts
- test_dashboard.py
- steps
- csrf.py
- Accounts and Google SSO (AUTH.md)
- changes
- ci-cd.yml
- allowBuilds
- deploy
- vm1 (vm1.modeus.cc)
- .mcp.json

## God Nodes (most connected - your core abstractions)
1. `Settings` - 131 edges
2. `apply()` - 60 edges
3. `initial_state()` - 53 edges
4. `run()` - 52 edges
5. `HistoryStore` - 51 edges
6. `User` - 47 edges
7. `IngestionError` - 43 edges
8. `LoadedScenario` - 42 edges
9. `Button()` - 42 edges
10. `LegalDocument` - 41 edges

## Surprising Connections (you probably didn't know these)
- `GoogleOAuth` --conceptually_related_to--> `authlib (Starlette integration)`  [AMBIGUOUS]
  backend/app/auth/google.py → frontend/AUTH.md
- `sanitize_text()` --implements--> `<source> tags treated as data, not instructions`  [INFERRED]
  backend/app/ai/prompts/sanitize.py → docs/BACKEND.md
- `Settings` --implements--> `CORS_ORIGINS (frontend address)`  [INFERRED]
  backend/app/config.py → docs/BACKEND.md
- `Settings` --implements--> `RAG_MIN_SCORE (relevance threshold)`  [INFERRED]
  backend/app/config.py → docs/BACKEND.md
- `Settings` --implements--> `Claude timeouts (LLM_MENTOR_TIMEOUT 20 s, LLM_FAST_TIMEOUT 4 s)`  [INFERRED]
  backend/app/config.py → docs/MODELS.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **LLM access path: backend (OLLAMA_URL=http://host.docker.internal:11435) -> mezon-llm-tunnel.service -> Ollama on the vast.ai GPU server** — deploy_vm1_readme_mezon_backend_service, deploy_vm1_readme_backend_llm_settings, deploy_vm1_readme_mezon_llm_tunnel_service, deploy_vm1_readme_llm_tunnel_key, deploy_vm1_readme_llm_tunnel_env, deploy_vm1_readme_gpu_ollama_server [EXTRACTED 1.00]
- **AI mentor answer flow: detect language -> normalize -> classify -> hybrid search -> threshold refusal -> source-tagged context -> structured blocks -> validation -> SSE** — docs_backend_query_language_detection, docs_backend_query_normalization, docs_backend_query_classification, docs_backend_hybrid_search, docs_backend_insufficient_sources_refusal, docs_backend_source_tags_as_data, docs_backend_structured_answer_blocks, docs_backend_answer_block_validation, docs_backend_mentor_sse_events [EXTRACTED 1.00]
- **Edition verification flow: run (pending_review) -> human review of check_report.md -> fill verified_by in sources.yaml -> activate -> seed-dump** — docs_data_run_command, docs_data_check_report, docs_data_human_review_fields, docs_ingestion_activate_command, docs_data_make_seed_dump [EXTRACTED 1.00]
- **User journey: Landing -> Cases -> Case intro -> Pretest -> Play -> Results -> Posttest / Mentor -> Dashboard** — docs_frontend_landing_screen, docs_frontend_cases_screen, docs_frontend_case_intro_screen, docs_frontend_quiz_screens, docs_frontend_court_simulator_screen, docs_frontend_results_screen, docs_frontend_mentor_screen, docs_frontend_dashboard_screen [EXTRACTED 1.00]
- **Legal ingestion pipeline: validate -> parse -> normalize -> segment -> version -> chunk -> embed -> load -> link -> check** — docs_ingestion_validate_step, docs_ingestion_parse_step, docs_ingestion_normalize_step, docs_ingestion_segment_step, docs_ingestion_version_step, docs_ingestion_chunk_step, docs_ingestion_embed_step, docs_ingestion_load_step, docs_ingestion_link_step, docs_ingestion_check_step [EXTRACTED 1.00]
- **First local run: backend/.venv -> .env from .env.example -> Docker Desktop -> make demo-laws -> make dev-all** — docs_setup_backend_venv, docs_setup_env_file, docs_setup_docker_desktop, docs_setup_make_demo_laws, docs_setup_make_dev_all [EXTRACTED 1.00]
- **Case materials document flow: CaseFile panel -> api.document -> GET /api/sessions/{session_id}/evidence/{evidence_id} -> get_evidence_document -> build_evidence_document -> EvidenceDocument lines** — docs_frontend_case_file, frontend_components_play_case_file_casefile, frontend_lib_api_types_api_document, docs_backend_get_api_sessions_session_id_evidence_evidence_id, backend_app_api_sessions_get_evidence_document, backend_app_services_presenter_build_evidence_document, docs_backend_evidence_document [INFERRED 0.85]
- **Two case categories for everyone: card kind court | situation -> CaseKind -> /cases#track-situation and #track-court sections, linked from 'What's inside Mezon'** — docs_frontend_whats_inside_mezon, docs_frontend_case_tracks, scenarios_readme_life_situations, frontend_components_site_pitch_pitch, frontend_app_locale_app_cases_page_casespage, frontend_lib_api_types_casekind, backend_app_schemas_scenario_card [INFERRED 0.85]
- **Life situation flow: 'Life situations' category -> SituationScreen on the play route -> claim letter to the seller** — scenarios_readme_life_situations, docs_frontend_case_tracks, docs_frontend_situation_screen, docs_frontend_claim_letter, frontend_components_play_situation_screen_situationscreen, frontend_components_common_claim_letter_claimletter [INFERRED 0.85]

## Communities (151 total, 24 thin omitted)

### Community 0 - "test_mentor_flow.py"
Cohesion: 0.17
Nodes (24): AnthropicLLM, FakeLLM, MentorAnswer, names(), call(), cls(), FakeAnthropic, good_answer() (+16 more)

### Community 1 - "situation-screen.tsx"
Cohesion: 0.09
Nodes (42): GET /api/scenarios, Case list categories 'Life situations' and 'Court cases' (the same for everyone), Case selection screen /[locale]/cases, Claim letter builder to the seller with a stamp (components/common/claim-letter.tsx), SituationScreen (life-situation layout on the play route for kind: "situation" cases), 'What's inside Mezon' section (two categories for everyone: life situations and court cases; buttons open their section of the case list), CasePage(), fmt() (+34 more)

### Community 2 - "scenario.py"
Cohesion: 0.10
Nodes (21): Action, Card, Character, Chose, Claim, DecisionPoint, EvaluationRule, Evidence (+13 more)

### Community 3 - "HistoryStore"
Cohesion: 0.09
Nodes (9): backfill(), BackfillResult, _ctx(), main(), build_store(), activity_key(), _canon_ts(), HistoryStore (+1 more)

### Community 4 - "test_registry_paths.py"
Cohesion: 0.11
Nodes (13): CitationCheckError, find_missing_citations(), load_from_roots(), load_registry(), scenario_roots(), _copy_as(), _no_db(), test_duplicate_scenario_id_across_roots_is_error() (+5 more)

### Community 5 - "api/mentor.py"
Cohesion: 0.11
Nodes (12): get_viewer(), get_settings(), get_db(), get_history(), create_app(), _db_opener(), lifespan(), embedder_dep() (+4 more)

### Community 6 - "account-menu.tsx"
Cohesion: 0.11
Nodes (19): AppLayout(), ThemeMenu(), AccountArea(), initials(), LanguageSwitcher(), LOCALE_LABELS, SiteFooter(), SiteHeader() (+11 more)

### Community 7 - "analytics/quiz.py"
Cohesion: 0.08
Nodes (31): build_dashboard(), _category_title(), _latest_attempts(), _level_label(), ingest(), get_quiz(), _quiz_questions(), submit_attempt() (+23 more)

### Community 8 - "evaluate"
Cohesion: 0.11
Nodes (19): replay(), evaluate(), play(), scenario(), to_log(), test_replay_100_times_identical(), test_replay_empty_log_is_initial(), test_replay_equals_sequential_apply() (+11 more)

### Community 9 - "react"
Cohesion: 0.07
Nodes (22): FONT_VAR, SettingsPage(), ClaimLetter(), Demand, DEMANDS, Field, FIELDS, Input() (+14 more)

### Community 10 - "load.py"
Cohesion: 0.18
Nodes (11): Chunk, _load(), LoadResult, lookup_existing(), _set_if_changed(), _update_existing(), upsert_document(), _version_meta() (+3 more)

### Community 11 - "ai/mentor.py"
Cohesion: 0.10
Nodes (12): load_session_context(), SessionContext, _article_label(), _call_mentor(), _history(), MentorPlan, prepare(), select_candidates() (+4 more)

### Community 12 - "package.json"
Cohesion: 0.07
Nodes (39): Node 24 (used in frontend/Dockerfile; not pinned in frontend/package.json), eslintConfig, dependencies, class-variance-authority@^0.7.1, cn@^0.5.2, lucide-react@^1.76.0, next-intl@4.15.3, next-themes@^0.4.6 (+31 more)

### Community 13 - "search.py"
Cohesion: 0.04
Nodes (52): rrf(), rrf_score(), detect_language(), base_normalize(), cyr_to_lat(), lat_to_cyr(), normalize(), tokenize() (+44 more)

### Community 14 - "search"
Cohesion: 0.16
Nodes (14): get_article(), get_citation(), search(), DATABASE_URL (Postgres), Explicit article reference lookup ('st. 15', '15-modda'), GET /api/legal/articles/{article_id}, GET /api/legal/search, Hybrid legal search (explicit refs + vector top 30 + full-text/trigram top 30) (+6 more)

### Community 15 - "game/conftest.py"
Cohesion: 0.12
Nodes (12): api(), Clock, clock(), game_client(), make_client(), _make(), seeded_db(), Mentor (+4 more)

### Community 16 - "vm1 deployment (CI/CD + systemd)"
Cohesion: 0.21
Nodes (7): bootstrap.sh script, vm1 deployment (CI/CD + systemd), /etc/mezon/frontend.build.env (NEXT_PUBLIC_API_MODE=mock|live, NEXT_PUBLIC_GOOGLE_AUTH; missing keys are appended), Frontend -> real backend (NEXT_PUBLIC_API_MODE=live in frontend.build.env, baked in at build time), mockApi, In-browser mock backend (localStorage), NEXT_PUBLIC_API_MODE (mock | live)

### Community 17 - "test_consumer_moisture.py"
Cohesion: 0.09
Nodes (29): loaded(), mistake_titles(), _opt(), path(), play(), loaded(), _result(), test_counterfactual_only_when_not_best_and_kind_is_exposed() (+21 more)

### Community 18 - "test_rent_deposit.py"
Cohesion: 0.11
Nodes (25): loaded(), mistake_titles(), _opt(), path(), play(), run(), sc(), test_accepting_the_photo_print_is_a_trap() (+17 more)

### Community 19 - "game.ts"
Cohesion: 0.15
Nodes (12): ApiError, GameEvent, GameState, Locale, zustand@5.1.0, CourtApi, GameStore, later() (+4 more)

### Community 20 - "cli.py"
Cohesion: 0.11
Nodes (12): _activate(), build_parser(), add(), _common(), _dispatch(), _paths(), _session_factory(), diff_document() (+4 more)

### Community 21 - "app/errors.py"
Cohesion: 0.07
Nodes (26): get_current_user(), AppError, DbUnavailableError, EmailExistsError, error_response(), ForbiddenError, IllegalActionError, install_error_handlers() (+18 more)

### Community 22 - "test_wedding_photo.py"
Cohesion: 0.10
Nodes (29): _ids(), loaded(), mistake_titles(), _opt(), path(), play(), _reach_motions(), run() (+21 more)

### Community 23 - "game_engine/__init__.py"
Cohesion: 0.09
Nodes (30): eval_condition(), HasFacts, _add_score(), _award_forecasts(), _enter(), _freeze(), _is_available(), _run_effects() (+22 more)

### Community 24 - "test_npc_flow.py"
Cohesion: 0.09
Nodes (16): NpcClassification, NpcReply, NpcFakeLLM, npc_events(), test_event_recorded(), test_llm_bad_or_failed_reply_falls_back(), test_llm_classifier_exception_uses_lexical(), test_llm_classifier_failure_uses_lexical() (+8 more)

### Community 25 - "run"
Cohesion: 0.11
Nodes (28): main(), assert_no_drafts(), IngestionError, assert_demo_database(), run(), statuses(), test_cli_draft_activate_refused_outside_demo_database(), test_draft_activate_in_demo_database_is_idempotent_and_check_still_fails() (+20 more)

### Community 26 - "test_google.py"
Cohesion: 0.11
Nodes (23): get_google(), pkce_challenge(), OAuthState, assert_failed(), callback(), start(), test_bad_id_token_rejected(), test_email_of_other_google_identity_is_refused() (+15 more)

### Community 27 - "Scenario"
Cohesion: 0.15
Nodes (16): _check_graph(), collect_text_keys(), _conditions(), _dump(), _dups(), _effect_lists(), iter_text_keys(), _mentioned_citations() (+8 more)

### Community 28 - "next-intl"
Cohesion: 0.09
Nodes (33): GET /api/health, Guest home page Pitch (components/site/pitch.tsx, case-folder design), HomeGate (signed-in user's case desk on the home page), Landing screen /[locale], Smooth page transitions (route template.tsx + .page-in CSS), PosttestPage(), Template(), Template() (+25 more)

### Community 29 - "ai/npc.py"
Cohesion: 0.11
Nodes (19): classify_question(), LLM, allowed_questions(), answer_question(), _choice_model(), classify_lexical(), classify_llm(), NpcResult (+11 more)

### Community 30 - "Auth security basics (state/PKCE check, next-path validation, CSRF, rate limiting)"
Cohesion: 0.15
Nodes (22): AUTH_IP_MAX_REQUESTS=120 per 15 min (code default 30), /etc/mezon/backend.env (backend secrets, chmod 600), Backend-owned sign-in (/api/auth/*, cookie mezon_session), Turning on Google sign-in (Web OAuth client, redirect URI https://mezon.modeus.cc/api/auth/google/callback, restart mezon-backend, NEXT_PUBLIC_GOOGLE_AUTH=true, mezon-deploy frontend), GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET (empty on vm1: Google sign-in off, 503), mezon-backend.service (127.0.0.1:8000), mezon.modeus.cc (production site), NEXT_PUBLIC_GOOGLE_AUTH (build-time flag; the Google button is hidden until true) (+14 more)

### Community 31 - "Legal ingestion pipeline (10 steps)"
Cohesion: 0.10
Nodes (31): Add a new law or edition (save lex.uz HTML -> name and place in raw/ -> update sources.yaml -> run --doc -> human review + activate -> citations.yaml, ingest-check, seed-dump), legal_data/processed/check_report.md (integrity report, prints edition version ids), citations.yaml entry (citation_id, document_key, article_number, part, topic, verified_by; template legal_data/citations.example.yaml), Stable citation id <document_key>.art.<number> (e.g. CPRL.art.14), Debug step commands without DB (parse / segment / chunk --doc), Legal data kept in git (legal_data/raw/ as source of truth, sources.yaml, citations.yaml, processed/check_report.md, article_counts.json), make ingest ARGS="..." (legal_ingestion CLI, run from repo root with databases up), make ingest-check (integrity checks only) (+23 more)

### Community 32 - "check.py"
Cohesion: 0.12
Nodes (19): _check_citations(), _check_counts(), _check_db(), CheckResult, _clip(), find_gaps(), Issue, _label() (+11 more)

### Community 33 - "Court simulator screen /[locale]/play/[sessionId] (main screen; SituationScreen for kind: "situation" cases)"
Cohesion: 0.17
Nodes (19): ActionView, GameEvent (say, react, stage_changed, evidence_added, score, legal_note, mistake), GameState, GET /api/sessions/{session_id}/evidence/{evidence_id}, 404 NOT_FOUND (no scenario, session or citation), review_<evidence_id> game action, ActionMenu, Case materials panel (CaseFile, components/play/case-file.tsx) (+11 more)

### Community 34 - "legal_ingestion/pipeline.py"
Cohesion: 0.10
Nodes (20): Raw file naming <document_key>_<language>_<date>.html (e.g. CPRL_ru_2026-11-20.html; ru, uz-Latn or uz-Cyrl), _debug_steps(), Edition, load_edition(), Paths, chunk_edition(), EditionOutcome, parse_edition() (+12 more)

### Community 35 - "test_email_auth.py"
Cohesion: 0.11
Nodes (29): login(), sha(), signup(), _flags(), test_auth_posts_require_origin(), test_cookie_flags_secure_on(), test_cookie_secure_off_for_local(), test_csrf_not_applied_to_get() (+21 more)

### Community 36 - "api.py"
Cohesion: 0.09
Nodes (30): ActionParams, ActionRequest, ActionView, CharacterView, ClaimView, CreateSession, CreateUser, DecisionView (+22 more)

### Community 37 - "play-screen.tsx"
Cohesion: 0.13
Nodes (26): Askable, EXAMPLES, Msg, NpcPanel(), DecisionDialog(), NAMES, fmt(), LegalPanel() (+18 more)

### Community 38 - "User"
Cohesion: 0.09
Nodes (13): me(), account_out(), create_email_user(), find_by_email(), GoogleLinkError, upsert_google_user(), GoogleProfile, loose_email() (+5 more)

### Community 39 - "game.py"
Cohesion: 0.21
Nodes (17): NotFoundError, SessionAction, create_user(), get_evidence_document(), get_loaded(), get_result(), _get_session(), get_state() (+9 more)

### Community 40 - "lib/settings.ts"
Cohesion: 0.06
Nodes (42): commissioner, fontVariables, nunito, onest, oswald, plexMono, plexSans, serif (+34 more)

### Community 41 - "test_search.py"
Cohesion: 0.10
Nodes (27): prefix_stem(), _tsquery(), FakeEmbedder, client(), dense_client(), factory(), make(), search() (+19 more)

### Community 42 - "presenter.py"
Cohesion: 0.15
Nodes (6): build_evidence_document(), build_result(), build_scenario_card(), present_actions(), present_evidence(), stage_index()

### Community 43 - "sqlalchemy"
Cohesion: 0.08
Nodes (11): get_url(), run_migrations_offline(), run_migrations_online(), upgrade(), upgrade(), _int(), upgrade(), upgrade() (+3 more)

### Community 44 - "test_ollama_adapter.py"
Cohesion: 0.09
Nodes (16): get_llm(), OllamaLLM, health(), HealthResponse, test_no_key_means_no_llm(), call(), make(), reply() (+8 more)

### Community 45 - ".start"
Cohesion: 0.11
Nodes (11): test_golden_path_via_api(), test_result_label_is_localized(), test_users_and_scenarios(), test_same_log_same_state(), test_document_locale_and_unknown(), test_documents_follow_the_case_file(), _check(), test_everything_translated() (+3 more)

### Community 46 - "CI deploy job (main only: rsync to /opt/mezon/src + ssh sudo mezon-deploy --sha <sha> <backend|frontend|all>)"
Cohesion: 0.17
Nodes (13): CI deploy job (main only: rsync to /opt/mezon/src + ssh sudo mezon-deploy --sha <sha> <backend|frontend|all>), VM1_KNOWN_HOSTS (GitHub Actions variable), VM1_SSH_KEY (GitHub Actions secret), BE, EVENT, FE, HAS_KEY, INFRA (+5 more)

### Community 47 - "rag/rerank.py"
Cohesion: 0.14
Nodes (13): CandidateForPrompt, get_reranker(), _llm_factory(), LLMReranker, NullReranker, order_by_scores(), Reranker, RerankItem (+5 more)

### Community 48 - "builder.py"
Cohesion: 0.35
Nodes (4): build_session_doc(), event_dicts(), session_doc(), step_doc()

### Community 49 - "engine/test_validate.py"
Cohesion: 0.17
Nodes (22): action(), broken(), has(), stage(), test_add_evidence_unknown(), m(), test_citation_not_listed(), test_dead_end_stage() (+14 more)

### Community 50 - "retrieve.py"
Cohesion: 0.29
Nodes (8): dense(), exact(), _run(), scenario_chunks(), Scope, sparse_fts(), sparse_titles(), _where()

### Community 51 - "api/users.py"
Cohesion: 0.16
Nodes (12): create_user(), get_user(), _get_user(), get_user_sessions(), _outcome_title(), patch_user(), _profile(), PatchUser (+4 more)

### Community 52 - "load_sources"
Cohesion: 0.16
Nodes (17): load_sources(), blocks(), document_entry(), html_doc(), version_entry(), write_docx(), write_source(), write_sources_yaml() (+9 more)

### Community 53 - "get_dashboard"
Cohesion: 0.19
Nodes (8): get_dashboard(), GET /api/users/{user_id}/dashboard, Legal literacy level (0-100), Learning gain (post - pre), POST /api/quiz/{scenario_id}/attempts, quiz_attempts table, Dashboard screen /[locale]/dashboard, Pre-test and post-test screens

### Community 54 - "test_history_store.py"
Cohesion: 0.06
Nodes (25): MongoHistoryStore, run(), NullHistoryStore, build(), alembic_config(), client(), db_engine(), db_session() (+17 more)

### Community 55 - "service.py"
Cohesion: 0.08
Nodes (28): fallback_language_note(), language_name(), unconfirmed_note(), _build(), get_article_view(), get_citation_view(), get_citation_views(), get_legal_acts() (+20 more)

### Community 56 - "DocumentVersion"
Cohesion: 0.17
Nodes (16): Article, ArticlePart, DocumentVersion, LegalDocument, main(), _article(), _cite(), _doc() (+8 more)

### Community 57 - "db"
Cohesion: 0.08
Nodes (28): NEXT_PUBLIC_API_MODE, args, context, environment, healthcheck, image, ports, volumes (+20 more)

### Community 58 - "types.ts"
Cohesion: 0.09
Nodes (23): Featured, ActionKind, ArticlePartView, CharacterView, DashboardOut, Difficulty, EditionStatus, EditionView (+15 more)

### Community 59 - "test_lexuz.py"
Cohesion: 0.09
Nodes (23): sources-draft command (draft sources.yaml from downloaded pages, no DB or network; --force keeps filled fields), build_draft(), _d(), _empty(), merge_existing(), merge(), _note(), PageInfo (+15 more)

### Community 60 - "engine.ts"
Cohesion: 0.11
Nodes (25): tx(), action(), apply(), availableActions(), EngineState, evaluate(), IllegalAction, initial() (+17 more)

### Community 61 - "make demo-laws (load real laws from legal_data/ into adolat_demo as drafts)"
Cohesion: 0.19
Nodes (15): EMBEDDER (embedding model selection), --draft-activate flag (drafts loaded as active only into demo DB adolat_demo), run command (full pipeline; --doc <key> for one document), embed step (embed.py), Embedder.embed(texts, kind=passage|query), multilingual-e5-large (local, passage:/query: prefixes), Embedding model role (articles and questions -> vectors for semantic search), adolat_demo demo database (draft loading allowed only for DB names ending in _demo) (+7 more)

### Community 62 - "Settings"
Cohesion: 0.11
Nodes (17): _base(), _clear_bind(), _fail(), google_callback(), google_start(), login(), logout(), _open_session() (+9 more)

### Community 63 - "Claude Haiku 5.5 via Anthropic API key (claude-haiku-5-5 for LLM_MODEL_MENTOR and LLM_MODEL_FAST)"
Cohesion: 0.09
Nodes (26): gemma3:27b (production language model served by Ollama on the GPU server), GPU server: Ollama (gemma3:27b + bge-m3) on a vast.ai RTX 3090, listening only on 127.0.0.1:11434, /etc/mezon/llm-tunnel.env (GPU_HOST, GPU_PORT, GPU_USER, TUNNEL_BIND, TUNNEL_PORT; template env/llm-tunnel.env.example), /etc/mezon/llm-tunnel.key (tunnel-only key; restricted on the GPU server to port-forwarding 127.0.0.1:11434, no shell), /etc/mezon/llm-tunnel.known_hosts (pinned ED25519 host key of the GPU server), mezon-llm-tunnel.service (SSH tunnel to the GPU server's Ollama, exposed on vm1 docker0 172.17.0.1:11435), Re-pointing the tunnel after vast.ai recreates the instance (update llm-tunnel.env, rescan and verify host key, authorize llm-tunnel.key.pub, restart mezon-llm-tunnel), ANTHROPIC_API_KEY (+18 more)

### Community 64 - "mock/index.ts"
Cohesion: 0.13
Nodes (23): actTitle(), LoggedAction, replay(), stageInfo(), CHARACTERS, citation(), Db, delay() (+15 more)

### Community 65 - "courtroom.ts"
Cohesion: 0.14
Nodes (26): Courtroom characters and animations (judge, player, plaintiff, defendant rep, witness/expert, secretary), ALIASES, archShape(), bubble(), CAST, COURT_THEMES, CourtHandle, CourtThemeId (+18 more)

### Community 66 - "schemas/quiz.py"
Cohesion: 0.24
Nodes (5): export_schemas(), _Model, Question, Quiz, QuizOption

### Community 67 - "OllamaEmbedder"
Cohesion: 0.17
Nodes (10): EmbedderError, OllamaEmbedder, test_connection_error_is_embedder_error(), test_embed_batches_and_request_shape(), test_embed_empty_makes_no_request(), test_embed_query_returns_vector(), test_errors_raise_in_embed_and_skip_in_query(), test_registry() (+2 more)

### Community 68 - "apply"
Cohesion: 0.14
Nodes (26): apply(), available_actions(), initial_state(), _settle(), test_random_walks_reach_results(), _at_decision(), test_after_finish_session_finished(), test_apply_does_not_mutate_old_state() (+18 more)

### Community 69 - "re"
Cohesion: 0.13
Nodes (15): _classes(), _Collector, _inline_text(), iter_lexuz(), parse_docx(), parse_file(), parse_html(), _parse_lexuz() (+7 more)

### Community 70 - "create_session"
Cohesion: 0.18
Nodes (6): create_session(), get_evidence_document(), get_result(), get_session(), patch_session(), post_action()

### Community 71 - "load_seed.py"
Cohesion: 0.08
Nodes (23): entrypoint.sh script, log(), main(), build, depends_on, env_file, environment, extra_hosts (+15 more)

### Community 73 - "uuid"
Cohesion: 0.22
Nodes (15): merge_guest(), _stats_row(), Event, GameSession, QuizAttempt, UserStats, test_events_without_session(), test_more_than_50_events_is_422() (+7 more)

### Community 74 - "components.json"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 75 - "translit.ts"
Cohesion: 0.16
Nodes (14): convertPlain(), convertWord(), fit(), IOTATED, isUpper(), latnToCyrl(), LETTERS, NEW_LETTERS (+6 more)

### Community 76 - "sqlalchemy_orm"
Cohesion: 0.09
Nodes (17): collect_citation_ids(), missing_citation_ids(), Base, Citation, load_scenario_dir(), _read_json(), _drop(), _ids() (+9 more)

### Community 77 - "ratelimit.py"
Cohesion: 0.26
Nodes (8): check(), clear_failures(), email_hash(), record_failure(), record_request(), _retry_after(), RateLimitedError, AuthAttempt

### Community 78 - "Cases in scenarios/ (one folder per case with scenario.json, quiz.json, texts.ru.json, texts.uz-Latn.json; not stored in git)"
Cohesion: 0.23
Nodes (10): Add a new case (copy test_consumer -> change scenario_id and texts -> citations in citations.yaml + make demo-laws -> make demo starts cleanly), scenarios/consumer_moisture_001/ (example case folder), quiz.json (case questions), scenario.json (case flow, roles, citations list), backend/app/schemas/scenario.schema.json and quiz.schema.json (case JSON schemas), Cases in scenarios/ (one folder per case with scenario.json, quiz.json, texts.ru.json, texts.uz-Latn.json; not stored in git), backend/tests/fixtures/scenarios/test_consumer/ (case template to copy), texts.ru.json and texts.uz-Latn.json (case texts, both languages required) (+2 more)

### Community 79 - "ask_npc"
Cohesion: 0.10
Nodes (10): ask(), gen(), format_sse(), open_db(), _recorder(), record(), ask_npc(), safely() (+2 more)

### Community 80 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 81 - "test_embed_db.py"
Cohesion: 0.11
Nodes (13): can_embed(), embed_texts(), EmbeddingCache, load_gold(), run_eval(), Calls, test_backend_search_skips_dense_branch_when_ollama_fails(), test_embed_texts_batches_and_cache() (+5 more)

### Community 82 - "test_parse_segment.py"
Cohesion: 0.09
Nodes (25): article_label(), build_chunks(), _clean(), doc_title_for(), estimate_tokens(), make_header(), _text(), _tokens() (+17 more)

### Community 83 - "AI Legal Mentor RAG pipeline"
Cohesion: 0.10
Nodes (24): CitationView, Edition status (current | historical | unconfirmed), GET /api/legal/citations/{citation_id}, GET /api/sessions/{session_id}/result, AI Legal Mentor RAG pipeline, Mentor SSE events (sources, block, done, error), Participant 2 (legal/, rag/, ai/ and ingestion pipeline owner), POST /api/mentor/ask (text/event-stream) (+16 more)

### Community 84 - "auth-form.tsx"
Cohesion: 0.11
Nodes (20): SignInPage(), SignUpPage(), Auth form error messages (429 rate limit, 422 validation, network errors), AuthForm(), done(), google(), submit(), validate() (+12 more)

### Community 86 - "ingestion/tests/conftest.py"
Cohesion: 0.16
Nodes (8): alembic_config(), create_migrated_database(), ing_db_url(), ing_engine(), session_factory(), Workspace, ws(), demo_factory()

### Community 87 - "Viewer"
Cohesion: 0.09
Nodes (8): post_events(), get_quiz(), post_attempt(), get_optional_user(), require_path_session(), require_path_user(), Viewer, POST /api/events (P1)

### Community 88 - "Api"
Cohesion: 0.21
Nodes (11): Api, post_quiz(), stats(), test_profile_404_and_validation(), test_profile_get_patch(), test_stats_after_three_playthroughs_and_quiz(), test_stats_unfinished_session_counts_only_started(), test_streak_by_utc_days() (+3 more)

### Community 89 - "test_phone_life.py"
Cohesion: 0.22
Nodes (10): loaded(), _opt(), path(), run(), sc(), test_best_path_is_a_win_with_max_score(), test_loss_and_mistakes(), test_partial_when_core_steps_done() (+2 more)

### Community 90 - "Mezon frontend README"
Cohesion: 0.10
Nodes (29): Monorepo layout (frontend/ Next.js 16 + Phaser 4, backend/ FastAPI + Postgres/pgvector + MongoDB history, deploy/vm1/ systemd + CI/CD, docs/ specs), ADOLAT Backend specification (BACKEND.md), ADOLAT (legal-education court simulator), CORS_ORIGINS (frontend address), FastAPI, GET /api/quiz/{scenario_id}?kind=pre|post, locale parameter (ru | uz-Latn | uz-Cyrl), Participant 4 (legal content, localization texts, Legal QA) (+21 more)

### Community 91 - "sanitize_text"
Cohesion: 0.17
Nodes (8): build_mentor_system(), build_mentor_user(), render_sources(), SourceForPrompt, build_rerank_user(), escape_attr(), sanitize_text(), test_sanitize_neutralizes_control_constructs()

### Community 92 - "QueryClassification"
Cohesion: 0.21
Nodes (14): MentorBlock, QueryClassification, first(), test_no_key_message_follows_question_language(), test_no_key_returns_sources_and_ai_unavailable(), test_no_key_still_applies_threshold(), concept(), mentor_events() (+6 more)

### Community 93 - "translate"
Cohesion: 0.18
Nodes (7): fallback_chain(), translate(), _case(), lat_to_cyr_display(), test_lat_to_cyr_display(), test_translate_uz_cyrl_falls_back_to_transliterated_latin(), test_translate_uz_cyrl_prefers_own_text_then_ru()

### Community 94 - "pytest"
Cohesion: 0.14
Nodes (15): _always(), Condition, Effect, _OneOf, React, Say, test_decision_action_requires_decision_id(), test_exactly_one_key() (+7 more)

### Community 95 - "test_access.py"
Cohesion: 0.24
Nodes (11): as_token(), calls(), do(), test_account_session_may_use_guest_ids(), test_expired_session_loses_access(), test_guests_work_without_login(), test_no_session_gets_401(), test_other_account_gets_403() (+3 more)

### Community 96 - "POST /api/sessions"
Cohesion: 0.15
Nodes (17): CC - Civil Code of Uzbekistan, consumer_dispute_001 (Faulty smartphone case), CPC - Civil Procedure Code of Uzbekistan, CPRL - Law of Uzbekistan 'On Consumer Rights Protection', events table (analytics), GET /api/scenarios/{scenario_id}, POST /api/sessions, sessions table (game sessions) (+9 more)

### Community 97 - "live.ts"
Cohesion: 0.17
Nodes (13): Evidence document response {id, title, type, lines[]}, call(), convertTexts(), LEGAL_KEYS, liveApi, localizeTexts(), sse(), TEXT_KEYS (+5 more)

### Community 98 - "typing"
Cohesion: 0.08
Nodes (10): _articles(), _section(), _article_keys(), _chunk_keys(), _dedupe(), rank_all(), CitationEntry, link_citations() (+2 more)

### Community 99 - "api/history.py"
Cohesion: 0.18
Nodes (7): session_history(), _usable(), user_activity(), ActivityItem, ActivityOut, HistoryStepOut, SessionHistoryOut

### Community 100 - "auth/conftest.py"
Cohesion: 0.23
Nodes (7): app(), app_and_client(), app_factory(), client(), make_account(), make(), make_guest()

### Community 101 - "passwords.py"
Cohesion: 0.18
Nodes (3): _dummy_hash(), normalize_email(), verify_password()

### Community 102 - "auth/sessions.py"
Cohesion: 0.25
Nodes (7): create_session(), hash_token(), resolve(), revoke_all(), revoke_token(), AuthSession, text_hash()

### Community 103 - "legal_data/seed.sql.gz (demo seed)"
Cohesion: 0.09
Nodes (20): volumes, mongodata, pgdata, legal_data/processed/*.articles.jsonl (parsed articles, source of article numbers), legal_data/processed/embeddings_cache/ (vector cache), Legal data not in git (processed/*.jsonl, processed/embeddings_cache/, seed.sql.gz via Git LFS), Seed stored in Git LFS (.gitattributes; git pull fetches it when git-lfs is installed), ingest docker compose service (tools profile) (+12 more)

### Community 104 - "results/[sessionId]/page.tsx"
Cohesion: 0.16
Nodes (14): Block, label(), MentorPage(), DKINDS, KINDS, short(), STAMP, CitationChip() (+6 more)

### Community 105 - "test_rerank.py"
Cohesion: 0.40
Nodes (16): ids(), items(), rerank(), scores(), test_equal_scores_keep_rrf_order(), test_exact_stays_first_despite_low_score(), test_explicit_timeout_is_used(), test_failures_keep_original_order() (+8 more)

### Community 106 - "test_mentor_rerank.py"
Cohesion: 0.31
Nodes (13): RerankScore, RerankScores, article_numbers(), baseline(), last_first(), make_llm(), mentor_event(), set_settings() (+5 more)

### Community 107 - "load_all"
Cohesion: 0.28
Nodes (10): load_all(), ScenarioValidationError, copy_fixtures(), edit_json(), test_invalid_scenario_json_collected(), test_load_all_fixtures_ok(), test_missing_cyrl_key_is_only_warning(), test_missing_quiz_key_is_error() (+2 more)

### Community 108 - "get_summary"
Cohesion: 0.17
Nodes (4): get_summary(), GET /api/analytics/scenarios/{scenario_id}/summary (P1), Participant 3 (API, models, game engine, analytics owner), SQL views (v_session_metrics, v_learning_gain, v_mistakes)

### Community 109 - "build_game_state"
Cohesion: 0.32
Nodes (11): build_game_state(), _loaded(), _state(), test_decision_options_translated(), test_events_translated_and_typed(), test_evidence_visible_from_second_stage_with_flags(), test_finished_state_has_no_actions(), test_initial_state_stage_and_evidence() (+3 more)

### Community 110 - ".play"
Cohesion: 0.35
Nodes (9): _err(), test_decision_without_valid_option_is_illegal(), test_illegal_action(), test_not_found(), test_outdated_session_after_scenario_change(), test_patch_locale_keeps_game_state(), test_reload_returns_same_state_and_last_step_events(), test_session_finished_and_not_finished() (+1 more)

### Community 112 - "stats.py"
Cohesion: 0.49
Nodes (5): on_quiz_attempt(), on_session_finished(), on_session_started(), _row(), _touch()

### Community 113 - "Committed graphify knowledge graph (graphify-out/)"
Cohesion: 0.31
Nodes (10): Mezon: notes for Claude Code (CLAUDE.md), graphify-out/graph.html (interactive graph view), graphify-out/graph.json (graph data used by graphify query), graphify-out/GRAPH_REPORT.md (communities, god nodes, surprising connections, open questions), graphify CLI (graphify query / path / explain), Committed graphify knowledge graph (graphify-out/), Graphify local state in graphify-out/ (cache, manifest), git-ignored, /graphify skill (.claude/skills/graphify, installs graphifyy on first use) (+2 more)

### Community 114 - "npc/test_schema.py"
Cohesion: 0.40
Nodes (10): broken(), has(), q(), test_character_does_not_know_fact(), test_duplicate_question_id(), m(), test_results_stage_not_allowed(), test_unknown_character() (+2 more)

### Community 115 - "FakeGoogle"
Cohesion: 0.22
Nodes (3): fake(), FakeGoogle, gapp()

### Community 117 - "content.ts"
Cohesion: 0.33
Nodes (5): ACT_TITLES, Dict, QUIZ, RU, UZ

### Community 119 - "target"
Cohesion: 0.20
Nodes (11): Manual deploy (Actions -> CI/CD -> Run workflow: all, frontend or backend), target, on, push, workflow_dispatch, branches, default, description (+3 more)

### Community 121 - "history/conftest.py"
Cohesion: 0.10
Nodes (10): get_event_db_factory(), NullEmbedder, hclient(), _make(), settable_clock(), SettableClock, mentor_client(), _make() (+2 more)

### Community 122 - "scripts"
Cohesion: 0.32
Nodes (8): Local pre-push checks (frontend: pnpm i18n && pnpm typecheck && pnpm build; backend: make test), scripts, build, dev, i18n, lint, start, typecheck

### Community 123 - "test_dashboard.py"
Cohesion: 0.33
Nodes (8): dash(), quiz(), test_dashboard_404(), test_dashboard_after_three_games(), test_dashboard_uz_latn(), test_knowledge_level_labels(), test_new_user_dashboard(), test_recommended_reasons()

### Community 124 - "steps"
Cohesion: 0.24
Nodes (10): steps, steps, id, if, name, run, uses, with (+2 more)

### Community 125 - "csrf.py"
Cohesion: 0.46
Nodes (5): allowed_origins(), csrf_guard(), origin_of(), CsrfError, CSRF Origin check (POSTs from any other Origin get 403 CSRF_FAILED)

### Community 126 - "Accounts and Google SSO (AUTH.md)"
Cohesion: 0.13
Nodes (14): hash_password(), test_me_without_session_is_401(), POST /api/users, users table, Anonymous user_id in localStorage, Accounts and Google SSO (AUTH.md), AccountUser {id, display_name, email, provider: google | email, avatar_url?}, GET /api/auth/me (+6 more)

### Community 127 - "changes"
Cohesion: 0.25
Nodes (7): outputs, runs-on, jobs, changes, backend, frontend, infra

### Community 128 - "ci-cd.yml"
Cohesion: 0.25
Nodes (6): concurrency, cancel-in-progress, group, name, permissions, contents

### Community 129 - "allowBuilds"
Cohesion: 0.29
Nodes (6): allowBuilds, @parcel/watcher, sharp, @swc/core, unrs-resolver, minimumReleaseAgeExclude

### Community 130 - "deploy"
Cohesion: 0.25
Nodes (8): environment, if, name, needs, runs-on, name, url, deploy

### Community 132 - "vm1 (vm1.modeus.cc)"
Cohesion: 0.33
Nodes (6): mezon-db.service (Postgres container), mezon-frontend.service (127.0.0.1:3000), mezon-mongo.service (MongoDB history), mezon-mongodata docker volume, mezon-pgdata docker volume, vm1 (vm1.modeus.cc)

### Community 135 - ".mcp.json"
Cohesion: 0.67
Nodes (3): npx, next-devtools, shadcn

## Ambiguous Edges - Review These
- `GoogleOAuth` → `authlib (Starlette integration)`  [AMBIGUOUS]
  frontend/AUTH.md · relation: conceptually_related_to
- `courtroom.ts` → `Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `types.ts` → `Generated API client (openapi-typescript + openapi-fetch, make api-client)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `Uzbek Cyrillic -> Latin transliteration table (search only)` → `Uzbek Latin 2026 alphabet (law of 21.10.2026)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `In-browser mock backend (localStorage)` → `Thin client: no game logic or scenario texts in the frontend`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to

## Knowledge Gaps
- **13 isolated node(s):** `adolat-ingestion`, `Palette (navy #0F1B2D, gold #C9A227, warm white #F5F1E8, teal #1FA39A, terracotta #C8553D)`, `graphify-out/graph.html (interactive graph view)`, `graphify-out/GRAPH_REPORT.md (communities, god nodes, surprising connections, open questions)`, `multilingual-e5-large (local, passage:/query: prefixes)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 989 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Settings` to `test_mentor_flow.py`, `HistoryStore`, `test_registry_paths.py`, `api/mentor.py`, `ai/mentor.py`, `search.py`, `search`, `game/conftest.py`, `cli.py`, `test_npc_flow.py`, `run`, `test_google.py`, `ai/npc.py`, `Auth security basics (state/PKCE check, next-path validation, CSRF, rate limiting)`, `test_ollama_adapter.py`, `rag/rerank.py`, `test_history_store.py`, `make demo-laws (load real laws from legal_data/ into adolat_demo as drafts)`, `Claude Haiku 5.5 via Anthropic API key (claude-haiku-5-5 for LLM_MODEL_MENTOR and LLM_MODEL_FAST)`, `OllamaEmbedder`, `GoogleOAuth`, `ratelimit.py`, `Cases in scenarios/ (one folder per case with scenario.json, quiz.json, texts.ru.json, texts.uz-Latn.json; not stored in git)`, `ask_npc`, `test_embed_db.py`, `AI Legal Mentor RAG pipeline`, `Mezon frontend README`, `sanitize_text`, `QueryClassification`, `typing`, `auth/conftest.py`, `auth/sessions.py`, `test_rerank.py`, `test_mentor_rerank.py`, `FakeGoogle`, `csrf.py`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Are the 73 inferred relationships involving `Settings` (e.g. with `classify_question()` and `get_llm()`) actually correct?**
  _`Settings` has 73 INFERRED edges - model-reasoned connections that need verification._
- **What connects `adolat-ingestion`, `Palette (navy #0F1B2D, gold #C9A227, warm white #F5F1E8, teal #1FA39A, terracotta #C8553D)`, `graphify-out/graph.html (interactive graph view)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `situation-screen.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.08961038961038961 - nodes in this community are weakly interconnected._
- **Why does `Mezon frontend README` connect `Mezon frontend README` to `POST /api/sessions`, `Court simulator screen /[locale]/play/[sessionId] (main screen; SituationScreen for kind: "situation" cases)`, `live.ts`, `situation-screen.tsx`, `legal_data/seed.sql.gz (demo seed)`, `lib/settings.ts`, `vm1 deployment (CI/CD + systemd)`, `game.ts`, `auth-form.tsx`, `Auth security basics (state/PKCE check, next-path validation, CSRF, rate limiting)`, `types.ts`, `next-intl`, `Accounts and Google SSO (AUTH.md)`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `GoogleOAuth` and `authlib (Starlette integration)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `courtroom.ts` and `Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._