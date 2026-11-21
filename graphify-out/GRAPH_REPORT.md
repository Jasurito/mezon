# Graph Report - mezon  (2026-11-21)

## Corpus Check
- 332 files · ~132,798 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3600 nodes · 9754 edges · 163 communities (136 shown, 27 thin omitted)
- Extraction: 88% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1119 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Mentor API & Scenario Registry
- Test Fixtures
- Results, Quiz & API Client
- Ingestion Runs
- Community 5
- Community 6
- Query Normalization
- Auth Form & UI Primitives
- Community 9
- Settings & Fonts
- Community 11
- Community 12
- Community 13
- Legal Data Pipeline Docs
- Errors & CSRF
- Seed Dump
- Frontend Dependencies
- NPC Tests
- Scenario Schema
- Community 20
- Google OAuth
- Community 22
- Court Play Screen
- Community 24
- Community 25
- Community 26
- Community 27
- Game API Presenter
- Community 29
- Community 30
- Community 31
- Specs & Setup Docs
- Community 33
- Community 34
- Engine Replay Tests
- Community 36
- Community 37
- Phaser Courtroom
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- User Profile & Audience
- Community 48
- Specs & Setup Docs
- Community 50
- Community 51
- Community 52
- Community 53
- Community 54
- Community 55
- Scenario Schema & Tests
- Community 57
- Community 58
- Community 59
- Community 60
- Community 61
- Community 62
- Community 63
- Community 64
- Community 65
- Auth API & Sessions
- Community 67
- Community 68
- Scenario Loader
- Community 70
- Community 71
- Community 72
- Community 73
- Community 74
- Community 75
- Legal Citation Service
- Life Situation Screen
- Community 78
- Community 79
- Community 80
- Community 81
- Game Engine Core
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
- Live API Client & Scripts
- Community 96
- Community 97
- Analytics & Dashboard
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
- CI/CD Workflow
- Community 118
- Community 119
- Community 120
- Community 121
- Community 122
- Community 123
- Community 124
- Community 125
- Community 126
- Community 127
- Community 128
- Community 129
- Community 130
- Community 131
- Community 132
- Community 133
- Community 134
- Community 135
- Community 136
- Community 137
- Community 138
- CI/CD Workflow
- Community 140
- Community 141
- Community 142
- Community 143
- Community 144
- Community 146

## God Nodes (most connected - your core abstractions)
1. `Settings` - 121 edges
2. `run()` - 52 edges
3. `User` - 45 edges
4. `IngestionError` - 43 edges
5. `react` - 39 edges
6. `HistoryStore` - 38 edges
7. `apply()` - 37 edges
8. `Scenario` - 37 edges
9. `next-intl` - 36 edges
10. `Event` - 35 edges

## Surprising Connections (you probably didn't know these)
- `GoogleOAuth` --conceptually_related_to--> `authlib (Starlette integration)`  [AMBIGUOUS]
  backend/app/auth/google.py → frontend/AUTH.md
- `EmbeddingCache` --implements--> `legal_data/processed/embeddings_cache/ (vector cache)`  [INFERRED]
  ingestion/legal_ingestion/embed.py → docs/DATA.md
- `ArticlePart` --implements--> `article_parts table`  [INFERRED]
  backend/app/models/legal.py → docs/INGESTION.md
- `Settings` --implements--> `CORS_ORIGINS (frontend address)`  [INFERRED]
  backend/app/config.py → docs/BACKEND.md
- `Settings` --implements--> `RAG_MIN_SCORE (relevance threshold)`  [INFERRED]
  backend/app/config.py → docs/BACKEND.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **AI mentor answer flow: detect language -> normalize -> classify -> hybrid search -> threshold refusal -> source-tagged context -> structured blocks -> validation -> SSE** — docs_backend_query_language_detection, docs_backend_query_normalization, docs_backend_query_classification, docs_backend_hybrid_search, docs_backend_insufficient_sources_refusal, docs_backend_source_tags_as_data, docs_backend_structured_answer_blocks, docs_backend_answer_block_validation, docs_backend_mentor_sse_events [EXTRACTED 1.00]
- **Edition verification flow: run (pending_review) -> human review of check_report.md -> fill verified_by in sources.yaml -> activate -> seed-dump** — docs_data_run_command, docs_data_check_report, docs_data_human_review_fields, docs_ingestion_activate_command, docs_data_make_seed_dump [EXTRACTED 1.00]
- **Legal ingestion pipeline: validate -> parse -> normalize -> segment -> version -> chunk -> embed -> load -> link -> check** — docs_ingestion_validate_step, docs_ingestion_parse_step, docs_ingestion_normalize_step, docs_ingestion_segment_step, docs_ingestion_version_step, docs_ingestion_chunk_step, docs_ingestion_embed_step, docs_ingestion_load_step, docs_ingestion_link_step, docs_ingestion_check_step [EXTRACTED 1.00]
- **First local run: backend/.venv -> .env from .env.example -> Docker Desktop -> make demo-laws -> make dev-all** — docs_setup_backend_venv, docs_setup_env_file, docs_setup_docker_desktop, docs_setup_make_demo_laws, docs_setup_make_dev_all [EXTRACTED 1.00]
- **Case materials document flow: CaseFile panel -> api.document -> GET /api/sessions/{session_id}/evidence/{evidence_id} -> get_evidence_document -> build_evidence_document -> EvidenceDocument lines** — docs_frontend_case_file, frontend_components_play_case_file_casefile, frontend_lib_api_types_api_document, docs_backend_get_api_sessions_session_id_evidence_evidence_id, backend_app_api_sessions_get_evidence_document, backend_app_services_presenter_build_evidence_document, docs_backend_evidence_document [INFERRED 0.85]
- **Audience capture flow: 'Who Mezon is for' -> sign-up form choice -> sessionStorage across Google redirect -> PATCH /api/users/{id} -> users.audience (migration 0007)** — docs_frontend_who_is_mezon_for, frontend_components_common_auth_form_authform, frontend_auth_pending_audience_storage, frontend_auth_patch_api_users_id, backend_app_api_users_patch_user, backend_migrations_versions_0007_user_audience [INFERRED 0.85]
- **User journey: Landing -> Cases -> Case intro -> Pretest -> Play -> Results -> Posttest / Mentor -> Dashboard** — docs_frontend_landing_screen, docs_frontend_cases_screen, docs_frontend_case_intro_screen, docs_frontend_quiz_screens, docs_frontend_court_simulator_screen, docs_frontend_results_screen, docs_frontend_mentor_screen, docs_frontend_dashboard_screen [EXTRACTED 1.00]
- **LLM access path: backend (OLLAMA_URL=http://host.docker.internal:11435) -> mezon-llm-tunnel.service -> Ollama on the vast.ai GPU server** — deploy_vm1_readme_mezon_backend_service, deploy_vm1_readme_backend_llm_settings, deploy_vm1_readme_mezon_llm_tunnel_service, deploy_vm1_readme_llm_tunnel_key, deploy_vm1_readme_llm_tunnel_env, deploy_vm1_readme_gpu_ollama_server [EXTRACTED 1.00]
- **Life situation flow: 'Life situations' track -> SituationScreen on the play route -> claim letter to the seller** — scenarios_readme_life_situations, docs_frontend_case_tracks, docs_frontend_situation_screen, docs_frontend_claim_letter, frontend_components_play_situation_screen_situationscreen, frontend_components_common_claim_letter_claimletter [INFERRED 0.85]

## Communities (163 total, 27 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (75): AnthropicLLM, FakeLLM, RerankScore, RerankScores, MentorAnswer, MentorBlock, QueryClassification, first() (+67 more)

### Community 1 - "Mentor API & Scenario Registry"
Cohesion: 0.09
Nodes (7): get_settings(), get_db(), get_history(), HistoryStore, _db_opener(), lifespan(), get_registry()

### Community 2 - "Test Fixtures"
Cohesion: 0.06
Nodes (24): get_event_db_factory(), create_app(), NullEmbedder, get_now(), api(), Clock, clock(), game_client() (+16 more)

### Community 3 - "Results, Quiz & API Client"
Cohesion: 0.09
Nodes (31): CasePage(), fmt(), DashboardPage(), fmt(), Block, label(), MentorPage(), Msg (+23 more)

### Community 4 - "Ingestion Runs"
Cohesion: 0.08
Nodes (36): main(), assert_no_drafts(), can_embed(), embed_texts(), EmbeddingCache, EditionOutcome, run(), statuses() (+28 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (21): classify_question(), load_session_context(), SessionContext, _article_label(), _history(), MentorPlan, prepare(), select_candidates() (+13 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (27): get_llm(), LLM, _call_mentor(), OllamaLLM, health(), HealthResponse, get_google(), Settings (+19 more)

### Community 7 - "Query Normalization"
Cohesion: 0.07
Nodes (30): detect_language(), base_normalize(), cyr_to_lat(), lat_to_cyr(), normalize(), tokenize(), canonical_number(), DocHint (+22 more)

### Community 8 - "Auth Form & UI Primitives"
Cohesion: 0.06
Nodes (23): Demand, DEMANDS, Field, FIELDS, Badge(), badgeVariants, Checkbox(), Input() (+15 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (26): Api, test_same_log_same_state(), _check(), test_everything_translated(), test_uz_cyrl_falls_back(), _texts(), _err(), session() (+18 more)

### Community 10 - "Settings & Fonts"
Cohesion: 0.07
Nodes (34): commissioner, fontVariables, nunito, onest, oswald, plexMono, plexSans, serif (+26 more)

### Community 11 - "Community 11"
Cohesion: 0.11
Nodes (26): Guest home page Pitch (components/site/pitch.tsx, case-folder design), HomeGate (signed-in user's case desk on the home page), AppLayout(), CaseDesk(), Landing(), DeskHeader(), HomeGate(), LanguageSwitcher() (+18 more)

### Community 12 - "Community 12"
Cohesion: 0.10
Nodes (29): _ids(), loaded(), mistake_titles(), _opt(), path(), play(), run(), sc() (+21 more)

### Community 13 - "Community 13"
Cohesion: 0.10
Nodes (30): _ids(), loaded(), mistake_titles(), _opt(), path(), play(), _reach_motions(), run() (+22 more)

### Community 14 - "Legal Data Pipeline Docs"
Cohesion: 0.09
Nodes (35): Add a new law or edition (save lex.uz HTML -> name and place in raw/ -> update sources.yaml -> run --doc -> human review + activate -> citations.yaml, ingest-check, seed-dump), legal_data/processed/check_report.md (integrity report, prints edition version ids), citations.yaml entry (citation_id, document_key, article_number, part, topic, verified_by; template legal_data/citations.example.yaml), Stable citation id <document_key>.art.<number> (e.g. CPRL.art.14), Debug step commands without DB (parse / segment / chunk --doc), Legal data kept in git (legal_data/raw/ as source of truth, sources.yaml, citations.yaml, processed/check_report.md, article_counts.json), make ingest ARGS="..." (legal_ingestion CLI, run from repo root with databases up), make ingest-check (integrity checks only) (+27 more)

### Community 15 - "Errors & CSRF"
Cohesion: 0.07
Nodes (25): AppError, AuthProviderDisabledError, DbUnavailableError, EmailExistsError, error_response(), IllegalActionError, install_error_handlers(), _app_error() (+17 more)

### Community 16 - "Seed Dump"
Cohesion: 0.08
Nodes (14): log(), main(), dump_seed(), pg_dump_command(), sequence_fixups(), alembic_config(), create_migrated_database(), ing_db_url() (+6 more)

### Community 17 - "Frontend Dependencies"
Cohesion: 0.07
Nodes (39): Toaster(), eslintConfig, dependencies, lucide-react@^1.76.0, next@16.4.6, next-intl@4.15.3, next-themes@^0.4.6, phaser@4.2.1 (+31 more)

### Community 18 - "NPC Tests"
Cohesion: 0.09
Nodes (18): NpcAnswer, NpcAskRequest, NpcClassification, NpcReply, NpcFakeLLM, npc_events(), test_event_recorded(), test_llm_bad_or_failed_reply_falls_back() (+10 more)

### Community 19 - "Scenario Schema"
Cohesion: 0.09
Nodes (21): Action, Card, Character, Chose, Claim, DecisionPoint, EvaluationRule, Evidence (+13 more)

### Community 20 - "Community 20"
Cohesion: 0.10
Nodes (18): rrf(), rrf_score(), Candidate, hybrid_search(), _ranks(), SearchOutcome, ArticleRef, dense() (+10 more)

### Community 21 - "Google OAuth"
Cohesion: 0.12
Nodes (24): pkce_challenge(), safe_next(), OAuthState, sha(), assert_failed(), callback(), start(), test_bad_id_token_rejected() (+16 more)

### Community 22 - "Community 22"
Cohesion: 0.09
Nodes (26): /etc/mezon/frontend.build.env (NEXT_PUBLIC_API_MODE=mock|live, NEXT_PUBLIC_GOOGLE_AUTH; missing keys are appended), Frontend -> real backend (NEXT_PUBLIC_API_MODE=live in frontend.build.env, baked in at build time), SignInPage(), SignUpPage(), Auth form error messages (429 rate limit, 422 validation, network errors), AuthForm(), done(), google() (+18 more)

### Community 23 - "Court Play Screen"
Cohesion: 0.09
Nodes (22): CaseFile(), Askable, EXAMPLES, Msg, NpcPanel(), NAMES, Dialog(), DialogContent() (+14 more)

### Community 24 - "Community 24"
Cohesion: 0.11
Nodes (22): check_version_file(), load_sources(), _loc(), SourcesFile, _Strict, TermsOfUse, blocks(), document_entry() (+14 more)

### Community 25 - "Community 25"
Cohesion: 0.15
Nodes (22): merge_guest(), _stats_row(), Event, GameSession, QuizAttempt, SessionAction, UserStats, test_events_without_session() (+14 more)

### Community 26 - "Community 26"
Cohesion: 0.11
Nodes (17): Edition, _load(), load_edition(), LoadResult, lookup_existing(), _set_if_changed(), _update_existing(), upsert_document() (+9 more)

### Community 27 - "Community 27"
Cohesion: 0.11
Nodes (26): login(), signup(), account_out(), _flags(), test_auth_posts_require_origin(), test_cookie_flags_secure_on(), test_cookie_secure_off_for_local(), test_csrf_not_applied_to_get() (+18 more)

### Community 28 - "Game API Presenter"
Cohesion: 0.11
Nodes (30): ActionParams, ActionRequest, ActionView, CharacterView, ClaimView, CreateSession, CreateUser, DecisionView (+22 more)

### Community 29 - "Community 29"
Cohesion: 0.13
Nodes (16): _check_citations(), _check_counts(), _check_db(), CheckResult, _clip(), find_gaps(), Issue, _label() (+8 more)

### Community 30 - "Community 30"
Cohesion: 0.10
Nodes (26): _tsquery(), FakeEmbedder, client(), dense_client(), factory(), make(), search(), test_dense_adds_to_sparse_score() (+18 more)

### Community 31 - "Community 31"
Cohesion: 0.10
Nodes (30): test_document_locale_and_unknown(), test_documents_follow_the_case_file(), Monorepo layout (frontend/ Next.js 16 + Phaser 4, backend/ FastAPI + Postgres/pgvector + MongoDB history, deploy/vm1/ systemd + CI/CD, docs/ specs), FastAPI, GET /api/sessions/{session_id}/evidence/{evidence_id}, review_<evidence_id> game action, ADOLAT Frontend specification (FRONTEND.md), ActionMenu (+22 more)

### Community 32 - "Specs & Setup Docs"
Cohesion: 0.10
Nodes (32): gemma3:27b (production language model served by Ollama on the GPU server), ADOLAT Backend specification (BACKEND.md), ADOLAT (legal-education court simulator), CORS_ORIGINS (frontend address), LLM_MODEL_MENTOR (claude-sonnet-5-5), SQLAlchemy 2 (sync, psycopg 3), How legal data and cases are assembled (DATA.md), ADOLAT Legal Ingestion specification (INGESTION.md) (+24 more)

### Community 33 - "Community 33"
Cohesion: 0.12
Nodes (16): search(), embedder_dep(), Embedder, get_embedder(), doc_title(), load_items(), make_snippet(), _parts_label() (+8 more)

### Community 34 - "Community 34"
Cohesion: 0.11
Nodes (16): allowed_questions(), answer_question(), _choice_model(), classify_lexical(), classify_llm(), NpcResult, _numbers(), rephrase() (+8 more)

### Community 35 - "Engine Replay Tests"
Cohesion: 0.15
Nodes (22): apply(), available_actions(), initial_state(), _is_available(), play(), test_state_is_json_serializable(), test_random_walks_reach_results(), _at_decision() (+14 more)

### Community 36 - "Community 36"
Cohesion: 0.18
Nodes (17): Base, Article, ArticlePart, Chunk, Citation, DocumentVersion, LegalDocument, _article() (+9 more)

### Community 37 - "Community 37"
Cohesion: 0.19
Nodes (15): create_user(), get_evidence_document(), get_loaded(), get_result(), _get_session(), get_state(), load_replayed(), _log() (+7 more)

### Community 38 - "Phaser Courtroom"
Cohesion: 0.09
Nodes (20): Court(), Props, bubble(), CourtHandle, drawPerson(), drawRoom(), furniture(), hex() (+12 more)

### Community 39 - "Community 39"
Cohesion: 0.10
Nodes (7): upgrade(), upgrade(), _int(), upgrade(), upgrade(), upgrade(), main()

### Community 40 - "Community 40"
Cohesion: 0.16
Nodes (20): _add_score(), _award_forecasts(), _enter(), _freeze(), _run_effects(), _settle(), _Work, AvailableAction (+12 more)

### Community 41 - "Community 41"
Cohesion: 0.13
Nodes (22): loaded(), mistake_titles(), run(), sc(), test_best_path_is_granted_and_gives_max_score(), test_best_path_is_the_maximum_and_max_score_is_117(), test_committee_complaint_is_optional_and_changes_nothing(), test_constitution_and_new_citations_in_scenario() (+14 more)

### Community 42 - "Community 42"
Cohesion: 0.11
Nodes (23): CitationView, Edition status (current | historical | unconfirmed), GET /api/legal/citations/{citation_id}, GET /api/sessions/{session_id}/result, AI Legal Mentor RAG pipeline, Mentor SSE events (sources, block, done, error), Participant 2 (legal/, rag/, ai/ and ingestion pipeline owner), POST /api/mentor/ask (text/event-stream) (+15 more)

### Community 43 - "Community 43"
Cohesion: 0.17
Nodes (22): action(), broken(), has(), stage(), test_add_evidence_unknown(), m(), test_citation_not_listed(), test_dead_end_stage() (+14 more)

### Community 44 - "Community 44"
Cohesion: 0.11
Nodes (19): _opt(), path(), play(), loaded(), _result(), test_counterfactual_only_when_not_best_and_kind_is_exposed(), test_result_kind_and_label(), loaded() (+11 more)

### Community 45 - "Community 45"
Cohesion: 0.08
Nodes (29): NEXT_PUBLIC_API_MODE, args, context, environment, healthcheck, image, ports, volumes (+21 more)

### Community 46 - "Community 46"
Cohesion: 0.15
Nodes (12): _activate(), build_parser(), add(), _common(), _debug_steps(), _dispatch(), _paths(), _session_factory() (+4 more)

### Community 47 - "User Profile & Audience"
Cohesion: 0.16
Nodes (12): create_user(), get_user(), _get_user(), get_user_sessions(), _outcome_title(), patch_user(), _profile(), PatchUser (+4 more)

### Community 48 - "Community 48"
Cohesion: 0.08
Nodes (26): ActionView, GameEvent (say, react, stage_changed, evidence_added, score, legal_note, mistake), GameState, ActionKind, ActionView, ArticlePartView, CharacterView, DashboardOut (+18 more)

### Community 49 - "Specs & Setup Docs"
Cohesion: 0.10
Nodes (21): GET /api/health, GET /api/scenarios, Case selection screen /[locale]/cases, Palette (navy #0F1B2D, gold #C9A227, warm white #F5F1E8, teal #1FA39A, terracotta #C8553D), Landing screen /[locale], next-intl (locale in URL), cache, CaseCaption() (+13 more)

### Community 50 - "Community 50"
Cohesion: 0.15
Nodes (10): post_events(), get_current_user(), get_optional_user(), get_viewer(), require_path_session(), require_path_user(), Viewer, ForbiddenError (+2 more)

### Community 51 - "Community 51"
Cohesion: 0.09
Nodes (11): get_dashboard(), get_quiz(), post_attempt(), GET /api/quiz/{scenario_id}?kind=pre|post, GET /api/users/{user_id}/dashboard, Legal literacy level (0-100), Learning gain (post - pre), POST /api/quiz/{scenario_id}/attempts (+3 more)

### Community 52 - "Community 52"
Cohesion: 0.13
Nodes (25): tx(), action(), apply(), availableActions(), EngineState, evaluate(), IllegalAction, initial() (+17 more)

### Community 53 - "Community 53"
Cohesion: 0.10
Nodes (22): CHARACTERS, citation(), Db, delay(), getSession(), load(), mentorStream(), mergeMockGuest() (+14 more)

### Community 54 - "Community 54"
Cohesion: 0.11
Nodes (9): IngestionError, _article_exists(), CitationEntry, link_citations(), LinkError, load_citations(), _to_str(), RunResult (+1 more)

### Community 55 - "Community 55"
Cohesion: 0.12
Nodes (16): NotFoundError, get_citation_view(), get_citation_views(), _is_valid_on(), _pick(), seeded(), test_all_scenario_citations_resolve(), test_article_view() (+8 more)

### Community 56 - "Scenario Schema & Tests"
Cohesion: 0.13
Nodes (16): _always(), Condition, Effect, React, Say, test_decision_action_requires_decision_id(), test_exactly_one_key(), test_fixture_loads_and_is_valid() (+8 more)

### Community 57 - "Community 57"
Cohesion: 0.13
Nodes (17): NEXT_PUBLIC_GOOGLE_AUTH (build-time flag; the Google button is hidden until true), POST /api/users, users table, Anonymous user_id in localStorage, Accounts and Google SSO (AUTH.md), AccountUser {id, display_name, email, provider, avatar_url?, audience?}, audience field (professional | public | null; added 2026-11-21, migration 0007), GET /api/auth/google/start (+9 more)

### Community 58 - "Community 58"
Cohesion: 0.13
Nodes (10): AccountArea(), initials(), Avatar(), AvatarFallback(), DropdownMenu(), DropdownMenuContent(), DropdownMenuItem(), DropdownMenuLabel() (+2 more)

### Community 59 - "Community 59"
Cohesion: 0.15
Nodes (16): build_draft(), _d(), _empty(), merge_existing(), merge(), _note(), PageInfo, _q() (+8 more)

### Community 60 - "Community 60"
Cohesion: 0.14
Nodes (12): find_missing_citations(), load_from_roots(), load_registry(), scenario_roots(), _copy_as(), _no_db(), test_duplicate_scenario_id_across_roots_is_error(), test_load_registry_uses_all_roots() (+4 more)

### Community 61 - "Community 61"
Cohesion: 0.13
Nodes (18): clear_cookie(), set_cookie(), AUTH_IP_MAX_REQUESTS=120 per 15 min (code default 30), /etc/mezon/backend.env (backend secrets, chmod 600), Backend-owned sign-in (/api/auth/*, cookie mezon_session), COOKIE_SECURE=true (session cookie only over https), mezon-backend.service (127.0.0.1:8000), mezon-db.service (Postgres container) (+10 more)

### Community 62 - "Community 62"
Cohesion: 0.15
Nodes (16): _check_graph(), collect_citation_ids(), collect_text_keys(), _conditions(), _dump(), _dups(), _effect_lists(), iter_text_keys() (+8 more)

### Community 63 - "Community 63"
Cohesion: 0.09
Nodes (25): outputs, runs-on, steps, environment, if, name, needs, runs-on (+17 more)

### Community 64 - "Community 64"
Cohesion: 0.13
Nodes (6): build_evidence_document(), build_result(), build_scenario_card(), present_actions(), present_evidence(), stage_index()

### Community 65 - "Community 65"
Cohesion: 0.21
Nodes (15): build_dashboard(), _category_title(), _latest_attempts(), _level_label(), ClientEvent, CompletedSession, DashboardLearningGain, DashboardOut (+7 more)

### Community 66 - "Auth API & Sessions"
Cohesion: 0.20
Nodes (9): _base(), _clear_bind(), _fail(), google_callback(), google_start(), logout(), me(), _open_session() (+1 more)

### Community 67 - "Community 67"
Cohesion: 0.17
Nodes (6): MongoHistoryStore, run(), mongo_store(), test_live_session_document_grows_and_finishes(), test_push_step_is_idempotent(), test_unreachable_mongo_does_not_break_game()

### Community 68 - "Community 68"
Cohesion: 0.18
Nodes (9): EmbedderError, OllamaEmbedder, test_connection_error_is_embedder_error(), test_embed_batches_and_request_shape(), test_embed_empty_makes_no_request(), test_embed_query_returns_vector(), test_errors_raise_in_embed_and_skip_in_query(), test_wrong_vector_count_is_error() (+1 more)

### Community 69 - "Scenario Loader"
Cohesion: 0.14
Nodes (9): load_scenario_dir(), LoadedScenario, _read_json(), export_schemas(), _Model, Question, Quiz, QuizOption (+1 more)

### Community 70 - "Community 70"
Cohesion: 0.17
Nodes (11): _classes(), _Collector, _inline_text(), iter_lexuz(), parse_docx(), parse_file(), parse_html(), _parse_lexuz() (+3 more)

### Community 71 - "Community 71"
Cohesion: 0.16
Nodes (12): clean_text(), normalize_blocks(), segment(), test_normalize_keeps_lex_id(), test_segment_lexuz(), _blocks(), test_chunks(), test_clean_text_only_junk() (+4 more)

### Community 72 - "Community 72"
Cohesion: 0.16
Nodes (6): create_session(), get_evidence_document(), get_result(), get_session(), patch_session(), post_action()

### Community 73 - "Community 73"
Cohesion: 0.16
Nodes (10): bootstrap.sh script, vm1 deployment (CI/CD + systemd), CI deploy job (main only: rsync to /opt/mezon/src + ssh sudo mezon-deploy --sha <sha> <backend|frontend|all>), Manual deploy (Actions -> CI/CD -> Run workflow: all, frontend or backend), concurrency, cancel-in-progress, group, name (+2 more)

### Community 74 - "Community 74"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 75 - "Community 75"
Cohesion: 0.14
Nodes (6): round_half_up(), scenario_summary(), message(), fallback_chain(), translate(), ScenarioSummary

### Community 76 - "Legal Citation Service"
Cohesion: 0.17
Nodes (11): _build(), get_article_view(), get_legal_acts(), missing_citation_ids(), _title(), ArticlePartView, CitationView, EditionView (+3 more)

### Community 77 - "Life Situation Screen"
Cohesion: 0.16
Nodes (16): test_audience_defaults_to_professional(), Case list tracks 'Life situations' and 'Court cases' (non-lawyers and guests see life situations first, lawyers court cases), Claim letter builder to the seller with a stamp (components/common/claim-letter.tsx), SituationScreen (life-situation layout on the play route for audience: "public" cases), 'Who Mezon is for' section (non-lawyer vs lawyer or law student; buttons open sign-up with the selected role), CasesPage(), PlayPage(), addedKey() (+8 more)

### Community 78 - "Community 78"
Cohesion: 0.11
Nodes (19): entrypoint.sh script, build, depends_on, environment, extra_hosts, ports, volumes, condition (+11 more)

### Community 79 - "Community 79"
Cohesion: 0.13
Nodes (15): GPU server: Ollama (gemma3:27b + bge-m3) on a vast.ai RTX 3090, listening only on 127.0.0.1:11434, /etc/mezon/llm-tunnel.env (GPU_HOST, GPU_PORT, GPU_USER, TUNNEL_BIND, TUNNEL_PORT; template env/llm-tunnel.env.example), /etc/mezon/llm-tunnel.key (tunnel-only key; restricted on the GPU server to port-forwarding 127.0.0.1:11434, no shell), /etc/mezon/llm-tunnel.known_hosts (pinned ED25519 host key of the GPU server), mezon-llm-tunnel.service (SSH tunnel to the GPU server's Ollama, exposed on vm1 docker0 172.17.0.1:11435), Re-pointing the tunnel after vast.ai recreates the instance (update llm-tunnel.env, rescan and verify host key, authorize llm-tunnel.key.pub, restart mezon-llm-tunnel), env_file, path (+7 more)

### Community 80 - "Community 80"
Cohesion: 0.14
Nodes (18): ACT_TITLES, actTitle(), Dict, QUIZ, RU, UZ, convertPlain(), convertWord() (+10 more)

### Community 81 - "Community 81"
Cohesion: 0.20
Nodes (7): check(), clear_failures(), client_ip(), record_failure(), record_request(), _retry_after(), AuthAttempt

### Community 82 - "Game Engine Core"
Cohesion: 0.15
Nodes (7): eval_condition(), HasFacts, IllegalAction, ScenarioError, SessionFinished, JSON condition DSL (all, any, not, flag, gte, always), 409 ILLEGAL_ACTION

### Community 83 - "Community 83"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 84 - "Community 84"
Cohesion: 0.16
Nodes (7): email_hash(), text_hash(), to_search(), activate_version(), content_hash(), find_existing(), link_neighbors()

### Community 85 - "Community 85"
Cohesion: 0.16
Nodes (8): test_no_state_duty_amounts_are_named(), normalize_number(), _ord_alt(), _ord_alt_ru(), to_roman(), _Draft, _finish(), _structural()

### Community 86 - "Community 86"
Cohesion: 0.18
Nodes (5): _article_keys(), _chunk_keys(), _dedupe(), load_gold(), rank_all()

### Community 87 - "Community 87"
Cohesion: 0.15
Nodes (6): ask(), gen(), format_sse(), open_db(), _recorder(), record()

### Community 88 - "Community 88"
Cohesion: 0.13
Nodes (13): Local pre-push checks (frontend: pnpm i18n && pnpm typecheck && pnpm build; backend: make test), scripts, build, dev, i18n, lint, start, typecheck (+5 more)

### Community 90 - "Community 90"
Cohesion: 0.14
Nodes (3): session_history(), _usable(), user_activity()

### Community 91 - "Community 91"
Cohesion: 0.28
Nodes (10): load_all(), ScenarioValidationError, copy_fixtures(), edit_json(), test_invalid_scenario_json_collected(), test_load_all_fixtures_ok(), test_missing_cyrl_key_is_only_warning(), test_missing_quiz_key_is_error() (+2 more)

### Community 92 - "Community 92"
Cohesion: 0.26
Nodes (11): build_game_state(), _loaded(), _state(), test_decision_options_translated(), test_events_translated_and_typed(), test_evidence_visible_from_second_stage_with_flags(), test_finished_state_has_no_actions(), test_initial_state_stage_and_evidence() (+3 more)

### Community 93 - "Community 93"
Cohesion: 0.18
Nodes (14): CC - Civil Code of Uzbekistan, consumer_dispute_001 (Faulty smartphone case), CPC - Civil Procedure Code of Uzbekistan, CPRL - Law of Uzbekistan 'On Consumer Rights Protection', GET /api/scenarios/{scenario_id}, All current corpus editions are drafts (verified_by empty, check_report.md reports errors), Current corpus (CONST, CC1, CC2, CPC, CPRL; ru and uz-Latn pages https://lex.uz/docs/<number>), Case intro screen /[locale]/cases/[id] (+6 more)

### Community 94 - "Community 94"
Cohesion: 0.18
Nodes (12): EMBEDDER (embedding model selection), --draft-activate flag (drafts loaded as active only into demo DB adolat_demo), BGE-M3 (local embedding model), Embedder.embed(texts, kind=passage|query), multilingual-e5-large (local, passage:/query: prefixes), bge-m3 via Ollama (EMBEDDER=ollama-bge-m3, ~1.2 GB), Embedding model role (articles and questions -> vectors for semantic search), adolat_demo demo database (draft loading allowed only for DB names ending in _demo) (+4 more)

### Community 95 - "Live API Client & Scripts"
Cohesion: 0.18
Nodes (11): Evidence document response {id, title, type, lines[]}, call(), convertTexts(), LEGAL_KEYS, localizeTexts(), sse(), TEXT_KEYS, uiLang() (+3 more)

### Community 96 - "Community 96"
Cohesion: 0.22
Nodes (9): mongo_docs(), play_everything(), _snapshot_mongo(), test_activity_has_all_types(), test_backfill_fills_gaps_next_to_live_records(), test_backfill_inmemory(), test_backfill_rebuilds_mongo(), test_history_endpoint_mongo_matches_postgres() (+1 more)

### Community 97 - "Community 97"
Cohesion: 0.20
Nodes (5): backfill(), BackfillResult, _ctx(), main(), build_store()

### Community 98 - "Analytics & Dashboard"
Cohesion: 0.25
Nodes (8): get_quiz(), _quiz_questions(), submit_attempt(), LearningGainOut, QuizAttemptOut, QuizOptionOut, QuizOut, QuizQuestionOut

### Community 99 - "Community 99"
Cohesion: 0.30
Nodes (6): create_session(), hash_token(), resolve(), revoke_all(), revoke_token(), AuthSession

### Community 100 - "Community 100"
Cohesion: 0.23
Nodes (9): _chosen(), evaluate(), Outcome, Mistake, Recommendation, test_best_path_gives_max_score(), test_events_use_keys_not_text(), test_loss_path() (+1 more)

### Community 101 - "Community 101"
Cohesion: 0.18
Nodes (3): activity_key(), _canon_ts(), make_activity()

### Community 102 - "Community 102"
Cohesion: 0.24
Nodes (11): as_token(), calls(), do(), test_account_session_may_use_guest_ids(), test_expired_session_loses_access(), test_guests_work_without_login(), test_no_session_gets_401(), test_other_account_gets_403() (+3 more)

### Community 103 - "Community 103"
Cohesion: 0.23
Nodes (7): app(), app_and_client(), app_factory(), client(), make_account(), make(), make_guest()

### Community 104 - "Community 104"
Cohesion: 0.15
Nodes (5): _dummy_hash(), hash_password(), loose_email(), normalize_email(), verify_password()

### Community 105 - "Community 105"
Cohesion: 0.21
Nodes (3): GoogleError, GoogleOAuth, GoogleProfile

### Community 106 - "Community 106"
Cohesion: 0.21
Nodes (4): create_email_user(), find_by_email(), GoogleLinkError, upsert_google_user()

### Community 107 - "Community 107"
Cohesion: 0.35
Nodes (11): broken(), has(), q(), test_character_does_not_know_fact(), test_duplicate_question_id(), m(), test_fixture_is_valid(), test_results_stage_not_allowed() (+3 more)

### Community 108 - "Community 108"
Cohesion: 0.30
Nodes (8): article_label(), build_chunks(), _clean(), doc_title_for(), estimate_tokens(), make_header(), _text(), _tokens()

### Community 109 - "Community 109"
Cohesion: 0.16
Nodes (6): blocks(), html(), test_chapter_patterns(), test_section_patterns(), test_segment_lexuz_preamble_and_unknown_heading(), test_segment_skips_part_subsection_paragraph_headings()

### Community 110 - "Community 110"
Cohesion: 0.26
Nodes (9): replay(), to_log(), test_replay_100_times_identical(), test_replay_empty_log_is_initial(), test_replay_equals_sequential_apply(), GET /api/sessions/{session_id}, POST /api/sessions/{session_id}/actions, Scenario effects (set, unset, score, say, react, add_evidence, mistake, legal_note, goto) (+1 more)

### Community 111 - "Community 111"
Cohesion: 0.26
Nodes (4): AccountUser, _lenient_uuid(), LoginIn, SignupIn

### Community 112 - "Community 112"
Cohesion: 0.23
Nodes (10): Add a new case (copy test_consumer -> change scenario_id and texts -> citations in citations.yaml + make demo-laws -> make demo starts cleanly), scenarios/consumer_moisture_001/ (example case folder), quiz.json (case questions), scenario.json (case flow, roles, citations list), backend/app/schemas/scenario.schema.json and quiz.schema.json (case JSON schemas), Cases in scenarios/ (one folder per case with scenario.json, quiz.json, texts.ru.json, texts.uz-Latn.json; not stored in git), backend/tests/fixtures/scenarios/test_consumer/ (case template to copy), texts.ru.json and texts.uz-Latn.json (case texts, both languages required) (+2 more)

### Community 113 - "Community 113"
Cohesion: 0.17
Nodes (4): get_summary(), GET /api/analytics/scenarios/{scenario_id}/summary (P1), Participant 3 (API, models, game engine, analytics owner), SQL views (v_session_metrics, v_learning_gain, v_mistakes)

### Community 114 - "Community 114"
Cohesion: 0.26
Nodes (7): CitationCheckError, _drop(), _ids(), test_all_scenario_citations_resolve(), test_invalid_scenario_stops_startup(), test_startup_fails_on_missing_citation(), test_startup_ok_when_not_strict()

### Community 115 - "Community 115"
Cohesion: 0.42
Nodes (5): on_quiz_attempt(), on_session_finished(), on_session_started(), _row(), _touch()

### Community 116 - "Community 116"
Cohesion: 0.27
Nodes (8): build(), alembic_config(), client(), db_engine(), db_session(), db_url(), make_alembic_config(), mongo_url()

### Community 117 - "CI/CD Workflow"
Cohesion: 0.17
Nodes (12): VM1_KNOWN_HOSTS (GitHub Actions variable), VM1_SSH_KEY (GitHub Actions secret), BE, EVENT, FE, HAS_KEY, INFRA, INPUT_TARGET (+4 more)

### Community 118 - "Community 118"
Cohesion: 0.18
Nodes (10): volumes, mongodata, pgdata, legal_data/processed/*.articles.jsonl (parsed articles, source of article numbers), legal_data/processed/embeddings_cache/ (vector cache), Legal data not in git (processed/*.jsonl, processed/embeddings_cache/, seed.sql.gz via Git LFS), Seed stored in Git LFS (.gitattributes; git pull fetches it when git-lfs is installed), ingest docker compose service (tools profile) (+2 more)

### Community 119 - "Community 119"
Cohesion: 0.27
Nodes (8): Turning on Google sign-in (Web OAuth client, redirect URI https://mezon.modeus.cc/api/auth/google/callback, restart mezon-backend, NEXT_PUBLIC_GOOGLE_AUTH=true, mezon-deploy frontend), GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET (empty on vm1: Google sign-in off, 503), mezon.modeus.cc (production site), PUBLIC_BASE_URL (https://mezon.modeus.cc on vm1), GET /api/auth/google/callback, Failed Google sign-in returns to /?auth_error=google (explained by components/site/auth-error-notice.tsx), Google Cloud OAuth client setup (consent screen, origins, redirect URIs), GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET / SESSION_SECRET

### Community 120 - "Community 120"
Cohesion: 0.35
Nodes (4): build_session_doc(), event_dicts(), session_doc(), step_doc()

### Community 122 - "Community 122"
Cohesion: 0.22
Nodes (7): test_golden_path_via_api(), test_result_label_is_localized(), test_users_and_scenarios(), events table (analytics), POST /api/events (P1), POST /api/sessions, sessions table (game sessions)

### Community 123 - "Community 123"
Cohesion: 0.31
Nodes (10): Mezon: notes for Claude Code (CLAUDE.md), graphify-out/graph.html (interactive graph view), graphify-out/graph.json (graph data used by graphify query), graphify-out/GRAPH_REPORT.md (communities, god nodes, surprising connections, open questions), graphify CLI (graphify query / path / explain), Committed graphify knowledge graph (graphify-out/), Graphify local state in graphify-out/ (cache, manifest), git-ignored, /graphify skill (.claude/skills/graphify, installs graphifyy on first use) (+2 more)

### Community 124 - "Community 124"
Cohesion: 0.24
Nodes (11): DATABASE_URL (Postgres), Explicit article reference lookup ('st. 15', '15-modda'), GET /api/legal/search, Hybrid legal search (explicit refs + vector top 30 + full-text/trigram top 30), pg_trgm, pgvector, PostgreSQL 16, Reciprocal Rank Fusion (RRF) (+3 more)

### Community 125 - "Community 125"
Cohesion: 0.33
Nodes (8): dash(), quiz(), test_dashboard_404(), test_dashboard_after_three_games(), test_dashboard_uz_latn(), test_knowledge_level_labels(), test_new_user_dashboard(), test_recommended_reasons()

### Community 126 - "Community 126"
Cohesion: 0.24
Nodes (5): _signup(), test_audience_is_optional_and_validated(), test_patch_audience_owner_only(), test_signup_stores_audience(), PATCH /api/users/{id} {audience}

### Community 127 - "Community 127"
Cohesion: 0.22
Nodes (3): fake(), FakeGoogle, gapp()

### Community 128 - "Community 128"
Cohesion: 0.20
Nodes (10): target, on, push, workflow_dispatch, branches, default, description, options (+2 more)

### Community 129 - "Community 129"
Cohesion: 0.33
Nodes (4): ingest(), safely(), EventsIn, EventsOut

### Community 135 - "Community 135"
Cohesion: 0.46
Nodes (5): allowed_origins(), csrf_guard(), origin_of(), CsrfError, CSRF Origin check (POSTs from any other Origin get 403 CSRF_FAILED)

### Community 137 - "Community 137"
Cohesion: 0.38
Nodes (3): get_article(), get_citation(), GET /api/legal/articles/{article_id}

### Community 138 - "Community 138"
Cohesion: 0.43
Nodes (4): ActivityItem, ActivityOut, HistoryStepOut, SessionHistoryOut

### Community 139 - "CI/CD Workflow"
Cohesion: 0.38
Nodes (4): get_url(), run_migrations_offline(), run_migrations_online(), Alembic migrations

### Community 140 - "Community 140"
Cohesion: 0.43
Nodes (5): locale parameter (ru | uz-Latn | uz-Cyrl), Participant 4 (legal content, localization texts, Legal QA), PATCH /api/sessions/{session_id}, UI locale files (ru.json, uz-Latn.json, uz-Cyrl.json), eval/gold.jsonl (~40 questions, 20 ru + 20 uz-Latn)

### Community 141 - "Community 141"
Cohesion: 0.29
Nodes (6): allowBuilds, @parcel/watcher, sharp, @swc/core, unrs-resolver, minimumReleaseAgeExclude

### Community 142 - "Community 142"
Cohesion: 0.40
Nodes (3): fallback_language_note(), language_name(), unconfirmed_note()

### Community 146 - "Community 146"
Cohesion: 0.67
Nodes (3): npx, next-devtools, shadcn

## Ambiguous Edges - Review These
- `GoogleOAuth` → `authlib (Starlette integration)`  [AMBIGUOUS]
  frontend/AUTH.md · relation: conceptually_related_to
- `courtroom.ts` → `Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `Uzbek Cyrillic -> Latin transliteration table (search only)` → `Uzbek Latin 2026 alphabet (law of 21.10.2026)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `sessions table (game sessions)` → `Opaque revocable server sessions (30-day sliding expiry)`  [AMBIGUOUS]
  frontend/AUTH.md · relation: conceptually_related_to
- `In-browser mock backend (localStorage)` → `Thin client: no game logic or scenario texts in the frontend`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `types.ts` → `Generated API client (openapi-typescript + openapi-fetch, make api-client)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to

## Knowledge Gaps
- **13 isolated node(s):** `adolat-ingestion`, `graphify-out/graph.html (interactive graph view)`, `graphify-out/GRAPH_REPORT.md (communities, god nodes, surprising connections, open questions)`, `make demo-reset (drop the demo DB to recreate it)`, `Pydantic v2` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1019 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Community 6` to `Community 0`, `Mentor API & Scenario Registry`, `Community 130`, `Test Fixtures`, `Ingestion Runs`, `Community 5`, `Community 135`, `NPC Tests`, `Community 20`, `Google OAuth`, `Specs & Setup Docs`, `Community 33`, `Community 34`, `Community 42`, `Community 46`, `Scenario Schema & Tests`, `Community 60`, `Community 61`, `Community 68`, `Community 79`, `Community 81`, `Community 86`, `Community 87`, `Community 94`, `Community 97`, `Community 99`, `Community 103`, `Community 105`, `Community 112`, `Community 116`, `Community 119`, `Community 124`, `Community 127`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 64 inferred relationships involving `Settings` (e.g. with `classify_question()` and `get_llm()`) actually correct?**
  _`Settings` has 64 INFERRED edges - model-reasoned connections that need verification._
- **What connects `adolat-ingestion`, `graphify-out/graph.html (interactive graph view)`, `graphify-out/GRAPH_REPORT.md (communities, god nodes, surprising connections, open questions)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.058786346396965866 - nodes in this community are weakly interconnected._
- **Why does `Mezon frontend README` connect `Specs & Setup Docs` to `Specs & Setup Docs`, `Results, Quiz & API Client`, `Phaser Courtroom`, `Settings & Fonts`, `Community 11`, `Community 48`, `Community 80`, `Frontend Dependencies`, `Community 118`, `Community 119`, `Community 22`, `Community 57`, `Community 88`, `Community 93`, `Live API Client & Scripts`, `Community 31`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `GoogleOAuth` and `authlib (Starlette integration)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `courtroom.ts` and `Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._