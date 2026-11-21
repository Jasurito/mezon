# Graph Report - mezon  (2026-11-21)

## Corpus Check
- 327 files · ~128,684 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3582 nodes · 9616 edges · 157 communities (135 shown, 22 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 1064 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Analytics & Dashboard
- Mentor API & Scenario Registry
- Query Normalization
- Community 4
- Seed Dump
- Errors & CSRF
- Court Play Screen
- Results, Quiz & API Client
- Community 9
- Community 10
- Ingestion Runs
- Community 12
- CI/CD Workflow
- Specs & Setup Docs
- Settings & Fonts
- Community 16
- Community 17
- Community 18
- NPC Tests
- Google OAuth
- Community 21
- Community 22
- Community 23
- Legal Data Pipeline Docs
- Scenario Schema
- Game API Presenter
- Community 27
- Frontend Dependencies
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- History Store & NPC Asking
- Community 38
- Community 39
- Test Fixtures
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- User Profile & Audience
- Community 47
- Community 48
- Community 49
- Community 50
- Auth Form & UI Primitives
- Community 52
- Community 53
- Community 54
- Community 55
- Engine Replay Tests
- Community 57
- Community 58
- Auth API & Sessions
- Community 60
- Community 61
- Scenario Loader
- Community 63
- Community 64
- Community 65
- Community 66
- Scenario Schema & Tests
- Community 68
- Community 69
- Community 70
- Community 71
- Community 72
- Community 73
- Community 74
- Community 75
- Community 76
- Specs & Setup Docs
- Community 78
- Community 79
- Community 80
- Legal Citation Service
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
- Game Engine Core
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
- Community 139
- Community 140

## God Nodes (most connected - your core abstractions)
1. `Settings` - 120 edges
2. `run()` - 52 edges
3. `User` - 45 edges
4. `IngestionError` - 43 edges
5. `HistoryStore` - 38 edges
6. `Scenario` - 37 edges
7. `apply()` - 37 edges
8. `react` - 37 edges
9. `initial_state()` - 35 edges
10. `signup()` - 35 edges

## Surprising Connections (you probably didn't know these)
- `GoogleOAuth` --conceptually_related_to--> `authlib (Starlette integration)`  [AMBIGUOUS]
  backend/app/auth/google.py → frontend/AUTH.md
- `Settings` --implements--> `CORS_ORIGINS (frontend address)`  [INFERRED]
  backend/app/config.py → docs/BACKEND.md
- `Settings` --implements--> `RAG_MIN_SCORE (relevance threshold)`  [INFERRED]
  backend/app/config.py → docs/BACKEND.md
- `Settings` --implements--> `Claude timeouts (LLM_MENTOR_TIMEOUT 20 s, LLM_FAST_TIMEOUT 4 s)`  [INFERRED]
  backend/app/config.py → docs/MODELS.md
- `Settings` --implements--> `LLM_MENTOR_EFFORT (mentor effort level, default medium)`  [INFERRED]
  backend/app/config.py → docs/MODELS.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **AI mentor answer flow: detect language -> normalize -> classify -> hybrid search -> threshold refusal -> source-tagged context -> structured blocks -> validation -> SSE** — docs_backend_query_language_detection, docs_backend_query_normalization, docs_backend_query_classification, docs_backend_hybrid_search, docs_backend_insufficient_sources_refusal, docs_backend_source_tags_as_data, docs_backend_structured_answer_blocks, docs_backend_answer_block_validation, docs_backend_mentor_sse_events [EXTRACTED 1.00]
- **Legal ingestion pipeline: validate -> parse -> normalize -> segment -> version -> chunk -> embed -> load -> link -> check** — docs_ingestion_validate_step, docs_ingestion_parse_step, docs_ingestion_normalize_step, docs_ingestion_segment_step, docs_ingestion_version_step, docs_ingestion_chunk_step, docs_ingestion_embed_step, docs_ingestion_load_step, docs_ingestion_link_step, docs_ingestion_check_step [EXTRACTED 1.00]
- **First local run: backend/.venv -> .env from .env.example -> Docker Desktop -> make demo-laws -> make dev-all** — docs_setup_backend_venv, docs_setup_env_file, docs_setup_docker_desktop, docs_setup_make_demo_laws, docs_setup_make_dev_all [EXTRACTED 1.00]
- **Case materials document flow: CaseFile panel -> api.document -> GET /api/sessions/{session_id}/evidence/{evidence_id} -> get_evidence_document -> build_evidence_document -> EvidenceDocument lines** — docs_frontend_case_file, frontend_components_play_case_file_casefile, frontend_lib_api_types_api_document, docs_backend_get_api_sessions_session_id_evidence_evidence_id, backend_app_api_sessions_get_evidence_document, backend_app_services_presenter_build_evidence_document, docs_backend_evidence_document [INFERRED 0.85]
- **Edition verification flow: run (pending_review) -> human review of check_report.md -> fill verified_by in sources.yaml -> activate -> seed-dump** — docs_data_run_command, docs_data_check_report, docs_data_human_review_fields, docs_ingestion_activate_command, docs_data_make_seed_dump [EXTRACTED 1.00]
- **User journey: Landing -> Cases -> Case intro -> Pretest -> Play -> Results -> Posttest / Mentor -> Dashboard** — docs_frontend_landing_screen, docs_frontend_cases_screen, docs_frontend_case_intro_screen, docs_frontend_quiz_screens, docs_frontend_court_simulator_screen, docs_frontend_results_screen, docs_frontend_mentor_screen, docs_frontend_dashboard_screen [EXTRACTED 1.00]
- **Audience capture flow: 'Who Mezon is for' -> sign-up form choice -> sessionStorage across Google redirect -> PATCH /api/users/{id} -> users.audience (migration 0007)** — docs_frontend_who_is_mezon_for, frontend_components_common_auth_form_authform, frontend_auth_pending_audience_storage, frontend_auth_patch_api_users_id, backend_app_api_users_patch_user, backend_migrations_versions_0007_user_audience [INFERRED 0.85]

## Communities (157 total, 22 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (78): AnthropicLLM, FakeLLM, OllamaLLM, RerankScore, RerankScores, MentorAnswer, MentorBlock, QueryClassification (+70 more)

### Community 1 - "Analytics & Dashboard"
Cohesion: 0.07
Nodes (32): build_dashboard(), _category_title(), _latest_attempts(), _level_label(), ingest(), get_quiz(), _quiz_questions(), submit_attempt() (+24 more)

### Community 2 - "Mentor API & Scenario Registry"
Cohesion: 0.10
Nodes (12): post_events(), get_current_user(), get_viewer(), require_path_session(), require_path_user(), Viewer, get_settings(), get_db() (+4 more)

### Community 3 - "Query Normalization"
Cohesion: 0.06
Nodes (34): detect_language(), base_normalize(), cyr_to_lat(), lat_to_cyr(), normalize(), tokenize(), ArticleRef, canonical_number() (+26 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (28): AppLayout(), AccountArea(), initials(), DeskHeader(), LanguageSwitcher(), LOCALE_LABELS, SiteFooter(), SiteHeader() (+20 more)

### Community 5 - "Seed Dump"
Cohesion: 0.06
Nodes (17): log(), main(), test_all_citations_resolve_on_legal_date(), test_all_citations_resolve_on_legal_date(), test_all_citations_resolve_on_legal_date(), dump_seed(), pg_dump_command(), sequence_fixups() (+9 more)

### Community 6 - "Errors & CSRF"
Cohesion: 0.06
Nodes (30): allowed_origins(), csrf_guard(), origin_of(), AppError, CsrfError, DbUnavailableError, EmailExistsError, error_response() (+22 more)

### Community 7 - "Court Play Screen"
Cohesion: 0.07
Nodes (31): CaseFile(), Askable, EXAMPLES, Msg, NpcPanel(), NAMES, fmt(), LegalPanel() (+23 more)

### Community 8 - "Results, Quiz & API Client"
Cohesion: 0.10
Nodes (29): CasePage(), fmt(), CasesPage(), DashboardPage(), fmt(), Block, label(), MentorPage() (+21 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (22): Raw file naming <document_key>_<language>_<date>.html (e.g. CPRL_ru_2026-11-20.html; ru, uz-Latn or uz-Cyrl), _activate(), _debug_steps(), _dispatch(), _paths(), _session_factory(), IngestionError, LinkError (+14 more)

### Community 10 - "Community 10"
Cohesion: 0.09
Nodes (20): search(), embedder_dep(), Embedder, get_embedder(), rrf(), rrf_score(), Candidate, hybrid_search() (+12 more)

### Community 11 - "Ingestion Runs"
Cohesion: 0.10
Nodes (33): main(), assert_no_drafts(), EditionOutcome, run(), statuses(), test_cli_draft_activate_refused_outside_demo_database(), test_draft_activate_in_demo_database_is_idempotent_and_check_still_fails(), test_draft_activate_promotes_already_loaded_pending() (+25 more)

### Community 12 - "Community 12"
Cohesion: 0.10
Nodes (19): _check_citations(), _check_counts(), _check_db(), CheckResult, _clip(), find_gaps(), Issue, _label() (+11 more)

### Community 13 - "CI/CD Workflow"
Cohesion: 0.05
Nodes (46): VM1_SSH_KEY (GitHub Actions secret), defaults, if, name, needs, runs-on, services, steps (+38 more)

### Community 14 - "Specs & Setup Docs"
Cohesion: 0.08
Nodes (43): main(), ADOLAT Backend specification (BACKEND.md), ADOLAT (legal-education court simulator), CORS_ORIGINS (frontend address), LLM_MODEL_MENTOR (claude-sonnet-5-5), SQLAlchemy 2 (sync, psycopg 3), How legal data and cases are assembled (DATA.md), ADOLAT Legal Ingestion specification (INGESTION.md) (+35 more)

### Community 15 - "Settings & Fonts"
Cohesion: 0.08
Nodes (31): FONT_VAR, SettingsPage(), Badge(), badgeVariants, Label(), Progress(), RadioGroup(), RadioGroupItem() (+23 more)

### Community 16 - "Community 16"
Cohesion: 0.07
Nodes (24): _db_opener(), lifespan(), find_missing_citations(), load_from_roots(), load_registry(), scenario_roots(), _copy_as(), _no_db() (+16 more)

### Community 17 - "Community 17"
Cohesion: 0.09
Nodes (30): _ids(), loaded(), mistake_titles(), _opt(), path(), play(), run(), sc() (+22 more)

### Community 18 - "Community 18"
Cohesion: 0.10
Nodes (30): _ids(), loaded(), mistake_titles(), _opt(), path(), play(), _reach_motions(), run() (+22 more)

### Community 19 - "NPC Tests"
Cohesion: 0.08
Nodes (19): NpcAnswer, NpcAskRequest, NpcClassification, NpcReply, NpcFakeLLM, npc_events(), test_event_recorded(), test_llm_bad_or_failed_reply_falls_back() (+11 more)

### Community 20 - "Google OAuth"
Cohesion: 0.11
Nodes (25): pkce_challenge(), safe_next(), OAuthState, sha(), assert_failed(), callback(), start(), test_bad_id_token_rejected() (+17 more)

### Community 21 - "Community 21"
Cohesion: 0.09
Nodes (17): classify_question(), LLM, allowed_questions(), answer_question(), _choice_model(), classify_lexical(), classify_llm(), NpcResult (+9 more)

### Community 22 - "Community 22"
Cohesion: 0.10
Nodes (15): build_mentor_system(), build_mentor_user(), render_sources(), SourceForPrompt, build_rerank_user(), CandidateForPrompt, escape_attr(), sanitize_text() (+7 more)

### Community 23 - "Community 23"
Cohesion: 0.05
Nodes (38): CI frontend job (pnpm i18n check, typecheck, build), outputs, runs-on, concurrency, cancel-in-progress, group, environment, if (+30 more)

### Community 24 - "Legal Data Pipeline Docs"
Cohesion: 0.10
Nodes (31): EMBEDDER (embedding model selection), GET /api/quiz/{scenario_id}?kind=pre|post, Participant 4 (legal content, localization texts, Legal QA), legal_data/processed/check_report.md (integrity report, prints edition version ids), citations.yaml entry (citation_id, document_key, article_number, part, topic, verified_by; template legal_data/citations.example.yaml), Stable citation id <document_key>.art.<number> (e.g. CPRL.art.14), Legal data kept in git (legal_data/raw/ as source of truth, sources.yaml, citations.yaml, processed/check_report.md, article_counts.json), Uzbek text is legally binding; Russian lex.uz texts are unofficial translations (+23 more)

### Community 25 - "Scenario Schema"
Cohesion: 0.09
Nodes (20): Action, Card, Character, Chose, Claim, DecisionPoint, EvaluationRule, Evidence (+12 more)

### Community 26 - "Game API Presenter"
Cohesion: 0.12
Nodes (30): ActionParams, ActionRequest, ActionView, CharacterView, ClaimView, CreateSession, CreateUser, DecisionView (+22 more)

### Community 27 - "Community 27"
Cohesion: 0.10
Nodes (27): prefix_stem(), _tsquery(), FakeEmbedder, client(), dense_client(), factory(), make(), search() (+19 more)

### Community 28 - "Frontend Dependencies"
Cohesion: 0.07
Nodes (35): eslintConfig, dependencies, lucide-react@^1.76.0, next@16.4.6, next-intl@4.15.3, next-themes@^0.4.6, phaser@4.2.1, react@19.3.0 (+27 more)

### Community 29 - "Community 29"
Cohesion: 0.10
Nodes (15): assert_demo_database(), Edition, _load(), load_edition(), LoadResult, lookup_existing(), _set_if_changed(), _update_existing() (+7 more)

### Community 30 - "Community 30"
Cohesion: 0.09
Nodes (26): ANTHROPIC_API_KEY, anthropic SDK, CitationView, Edition status (current | historical | unconfirmed), GET /api/legal/citations/{citation_id}, GET /api/sessions/{session_id}/result, LLM_MODEL_FAST (claude-haiku-5-5), AI Legal Mentor RAG pipeline (+18 more)

### Community 31 - "Community 31"
Cohesion: 0.10
Nodes (23): 'Who Mezon is for' section (non-lawyer vs lawyer or law student; buttons open sign-up with the selected role), SignInPage(), SignUpPage(), Auth form error messages (429 rate limit, 422 validation, network errors), AuthForm(), done(), google(), submit() (+15 more)

### Community 32 - "Community 32"
Cohesion: 0.13
Nodes (23): GameSession, test_events_without_session(), test_more_than_50_events_is_422(), add_session(), app(), app_and_client(), app_factory(), build() (+15 more)

### Community 33 - "Community 33"
Cohesion: 0.11
Nodes (26): login(), signup(), account_out(), _flags(), test_auth_posts_require_origin(), test_cookie_flags_secure_on(), test_cookie_secure_off_for_local(), test_csrf_not_applied_to_get() (+18 more)

### Community 34 - "Community 34"
Cohesion: 0.09
Nodes (10): get_url(), run_migrations_offline(), run_migrations_online(), upgrade(), upgrade(), _int(), upgrade(), upgrade() (+2 more)

### Community 35 - "Community 35"
Cohesion: 0.19
Nodes (15): create_user(), get_evidence_document(), get_loaded(), get_result(), _get_session(), get_state(), load_replayed(), _log() (+7 more)

### Community 36 - "Community 36"
Cohesion: 0.08
Nodes (20): commissioner, fontVariables, nunito, onest, oswald, plexMono, plexSans, serif (+12 more)

### Community 37 - "History Store & NPC Asking"
Cohesion: 0.10
Nodes (6): record(), activity_key(), _canon_ts(), HistoryStore, make_activity(), safely()

### Community 38 - "Community 38"
Cohesion: 0.10
Nodes (12): load_session_context(), SessionContext, _article_label(), _call_mentor(), _history(), MentorPlan, prepare(), select_candidates() (+4 more)

### Community 39 - "Community 39"
Cohesion: 0.07
Nodes (31): NEXT_PUBLIC_API_MODE, args, context, environment, healthcheck, image, ports, volumes (+23 more)

### Community 40 - "Test Fixtures"
Cohesion: 0.14
Nodes (11): get_llm(), create_app(), scenario(), api(), Clock, clock(), game_client(), make_client() (+3 more)

### Community 41 - "Community 41"
Cohesion: 0.10
Nodes (15): get_optional_user(), User, POST /api/users, users table, Anonymous user_id in localStorage, Accounts and Google SSO (AUTH.md), AccountUser {id, display_name, email, provider, avatar_url?, audience?}, audience field (professional | public | null; added 2026-11-21, migration 0007) (+7 more)

### Community 42 - "Community 42"
Cohesion: 0.19
Nodes (16): Base, Article, ArticlePart, Chunk, DocumentVersion, LegalDocument, _article(), _cite() (+8 more)

### Community 43 - "Community 43"
Cohesion: 0.11
Nodes (28): test_document_locale_and_unknown(), test_documents_follow_the_case_file(), events table (analytics), GET /api/sessions/{session_id}/evidence/{evidence_id}, 409 ILLEGAL_ACTION, POST /api/events (P1), POST /api/sessions, POST /api/sessions/{session_id}/actions (+20 more)

### Community 44 - "Community 44"
Cohesion: 0.13
Nodes (22): loaded(), mistake_titles(), run(), sc(), test_best_path_is_granted_and_gives_max_score(), test_best_path_is_the_maximum_and_max_score_is_117(), test_committee_complaint_is_optional_and_changes_nothing(), test_constitution_and_new_citations_in_scenario() (+14 more)

### Community 45 - "Community 45"
Cohesion: 0.12
Nodes (20): bootstrap.sh script, vm1 deployment (CI/CD + systemd), CI deploy job (rsync to /opt/mezon/src + ssh sudo mezon-deploy), Turning on Google sign-in (Web OAuth client, redirect URI https://mezon.modeus.cc/api/auth/google/callback, restart mezon-backend, NEXT_PUBLIC_GOOGLE_AUTH=true, mezon-deploy frontend), /etc/mezon/frontend.build.env (NEXT_PUBLIC_API_MODE=mock|live, NEXT_PUBLIC_GOOGLE_AUTH; missing keys are appended), Frontend -> real backend (NEXT_PUBLIC_API_MODE=live in frontend.build.env, baked in at build time), Manual deploy (Actions -> CI/CD -> Run workflow: all, frontend or backend), mezon-backend.service (127.0.0.1:8000) (+12 more)

### Community 46 - "User Profile & Audience"
Cohesion: 0.15
Nodes (13): create_user(), get_user(), _get_user(), get_user_sessions(), _outcome_title(), patch_user(), _profile(), PatchUser (+5 more)

### Community 47 - "Community 47"
Cohesion: 0.07
Nodes (28): entrypoint.sh script, build, depends_on, env_file, environment, extra_hosts, ports, volumes (+20 more)

### Community 48 - "Community 48"
Cohesion: 0.09
Nodes (19): Palette (navy #0F1B2D, gold #C9A227, warm white #F5F1E8, teal #1FA39A, terracotta #C8553D), Courtroom characters and animations (judge, player, plaintiff, defendant rep, witness/expert, secretary), Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses), Phaser court scene (640x360, pixelArt, Scale.FIT), Court(), Props, bubble(), CAST (+11 more)

### Community 49 - "Community 49"
Cohesion: 0.17
Nodes (22): action(), broken(), has(), stage(), test_add_evidence_unknown(), m(), test_citation_not_listed(), test_dead_end_stage() (+14 more)

### Community 50 - "Community 50"
Cohesion: 0.07
Nodes (27): ActionView, GameEvent (say, react, stage_changed, evidence_added, score, legal_note, mistake), GameState, ActionKind, ActionView, ArticlePartView, CharacterView, CitationView (+19 more)

### Community 51 - "Auth Form & UI Primitives"
Cohesion: 0.14
Nodes (21): GET /api/health, Case selection screen /[locale]/cases, Guest home page Pitch (components/site/pitch.tsx, case-folder design), HomeGate (signed-in user's case desk on the home page), Landing screen /[locale], CaseDesk(), Landing(), cache (+13 more)

### Community 52 - "Community 52"
Cohesion: 0.13
Nodes (25): tx(), action(), apply(), availableActions(), EngineState, evaluate(), IllegalAction, initial() (+17 more)

### Community 53 - "Community 53"
Cohesion: 0.10
Nodes (22): CHARACTERS, citation(), Db, delay(), getSession(), load(), mentorStream(), mergeMockGuest() (+14 more)

### Community 54 - "Community 54"
Cohesion: 0.16
Nodes (17): load_sources(), blocks(), document_entry(), html_doc(), version_entry(), write_docx(), write_source(), write_sources_yaml() (+9 more)

### Community 55 - "Community 55"
Cohesion: 0.09
Nodes (10): get_dashboard(), get_quiz(), post_attempt(), GET /api/users/{user_id}/dashboard, Legal literacy level (0-100), Learning gain (post - pre), POST /api/quiz/{scenario_id}/attempts, quiz_attempts table (+2 more)

### Community 56 - "Engine Replay Tests"
Cohesion: 0.18
Nodes (18): apply(), available_actions(), initial_state(), _is_available(), test_random_walks_reach_results(), _at_decision(), test_after_finish_session_finished(), test_apply_does_not_mutate_old_state() (+10 more)

### Community 57 - "Community 57"
Cohesion: 0.15
Nodes (16): build_draft(), _d(), _empty(), merge_existing(), merge(), _note(), PageInfo, _q() (+8 more)

### Community 58 - "Community 58"
Cohesion: 0.12
Nodes (6): build_evidence_document(), build_result(), build_scenario_card(), present_actions(), present_evidence(), stage_index()

### Community 59 - "Auth API & Sessions"
Cohesion: 0.19
Nodes (9): _base(), _clear_bind(), _fail(), google_callback(), google_start(), logout(), me(), _open_session() (+1 more)

### Community 60 - "Community 60"
Cohesion: 0.11
Nodes (10): health(), HealthResponse, get_google(), Settings, get_reranker(), test_get_llm_selects_provider(), test_get_reranker_by_settings(), RERANK_CANDIDATES (candidates given to the reranker, default 15) (+2 more)

### Community 61 - "Community 61"
Cohesion: 0.15
Nodes (17): _check_graph(), collect_citation_ids(), collect_text_keys(), _conditions(), _dump(), _dups(), _effect_lists(), iter_text_keys() (+9 more)

### Community 62 - "Scenario Loader"
Cohesion: 0.18
Nodes (13): load_all(), load_scenario_dir(), LoadedScenario, _read_json(), ScenarioValidationError, copy_fixtures(), edit_json(), test_invalid_scenario_json_collected() (+5 more)

### Community 63 - "Community 63"
Cohesion: 0.21
Nodes (16): _add_score(), _award_forecasts(), _enter(), _run_effects(), _settle(), _Work, AvailableAction, EvidenceAddedEvent (+8 more)

### Community 64 - "Community 64"
Cohesion: 0.12
Nodes (14): get_citation_view(), get_citation_views(), _is_valid_on(), _pick(), seeded(), test_all_scenario_citations_resolve(), test_current_edition_on_date(), test_get_citation_views_order_and_dedup() (+6 more)

### Community 65 - "Community 65"
Cohesion: 0.17
Nodes (10): EmbedderError, OllamaEmbedder, test_connection_error_is_embedder_error(), test_embed_batches_and_request_shape(), test_embed_empty_makes_no_request(), test_embed_query_returns_vector(), test_errors_raise_in_embed_and_skip_in_query(), test_registry() (+2 more)

### Community 66 - "Community 66"
Cohesion: 0.17
Nodes (12): test_same_log_same_state(), test_uz_cyrl_falls_back(), _err(), session(), test_decision_without_valid_option_is_illegal(), test_illegal_action(), test_not_found(), test_outdated_session_after_scenario_change() (+4 more)

### Community 67 - "Scenario Schema & Tests"
Cohesion: 0.15
Nodes (16): _always(), Condition, Effect, React, Say, test_decision_action_requires_decision_id(), test_exactly_one_key(), test_gte_forms() (+8 more)

### Community 68 - "Community 68"
Cohesion: 0.17
Nodes (11): _classes(), _Collector, _inline_text(), iter_lexuz(), parse_docx(), parse_file(), parse_html(), _parse_lexuz() (+3 more)

### Community 69 - "Community 69"
Cohesion: 0.16
Nodes (12): clean_text(), normalize_blocks(), segment(), test_normalize_keeps_lex_id(), test_segment_lexuz(), _blocks(), test_chunks(), test_clean_text_only_junk() (+4 more)

### Community 70 - "Community 70"
Cohesion: 0.16
Nodes (6): create_session(), get_evidence_document(), get_result(), get_session(), patch_session(), post_action()

### Community 71 - "Community 71"
Cohesion: 0.16
Nodes (10): check(), clear_failures(), client_ip(), email_hash(), record_failure(), record_request(), _retry_after(), RateLimitedError (+2 more)

### Community 72 - "Community 72"
Cohesion: 0.15
Nodes (15): replay(), LoggedAction, play(), to_log(), test_replay_100_times_identical(), test_replay_empty_log_is_initial(), test_replay_equals_sequential_apply(), test_state_is_json_serializable() (+7 more)

### Community 73 - "Community 73"
Cohesion: 0.17
Nodes (3): MongoHistoryStore, run(), test_push_step_is_idempotent()

### Community 74 - "Community 74"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 75 - "Community 75"
Cohesion: 0.15
Nodes (7): _article_keys(), _chunk_keys(), _dedupe(), load_gold(), rank_all(), run_eval(), test_eval_without_gold_file_gives_clear_message()

### Community 76 - "Community 76"
Cohesion: 0.17
Nodes (16): AuthProviderDisabledError, AUTH_IP_MAX_REQUESTS=120 per 15 min (code default 30), /etc/mezon/backend.env (backend secrets, chmod 600), Backend-owned sign-in (/api/auth/*, cookie mezon_session), GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET (empty on vm1: Google sign-in off, 503), mezon.modeus.cc (production site), nginx reverse proxy (/api/* -> :8000, everything else -> :3000), PUBLIC_BASE_URL (https://mezon.modeus.cc on vm1) (+8 more)

### Community 77 - "Specs & Setup Docs"
Cohesion: 0.16
Nodes (18): Monorepo layout (frontend/ Next.js 16 + Phaser 4, backend/ FastAPI + Postgres/pgvector + MongoDB history, deploy/vm1/ systemd + CI/CD, docs/ specs), FastAPI, locale parameter (ru | uz-Latn | uz-Cyrl), PATCH /api/sessions/{session_id}, ADOLAT Frontend specification (FRONTEND.md), Generated API client (openapi-typescript + openapi-fetch, make api-client), next-intl (locale in URL), Next.js (App Router) (+10 more)

### Community 78 - "Community 78"
Cohesion: 0.12
Nodes (10): normalize_number(), _ord_alt(), _ord_alt_ru(), to_roman(), blocks(), html(), test_chapter_patterns(), test_section_patterns() (+2 more)

### Community 79 - "Community 79"
Cohesion: 0.14
Nodes (16): convertPlain(), convertWord(), fit(), IOTATED, isUpper(), latnToCyrl(), LETTERS, NEW_LETTERS (+8 more)

### Community 80 - "Community 80"
Cohesion: 0.21
Nodes (9): clear_cookie(), create_session(), hash_token(), resolve(), revoke_all(), revoke_token(), set_cookie(), AuthSession (+1 more)

### Community 81 - "Legal Citation Service"
Cohesion: 0.20
Nodes (11): NotFoundError, _build(), get_article_view(), get_legal_acts(), _title(), ArticlePartView, CitationView, EditionView (+3 more)

### Community 82 - "Community 82"
Cohesion: 0.12
Nodes (8): NullEmbedder, hclient(), _make(), Mentor, mentor_client(), _make(), no_network(), parse_sse()

### Community 83 - "Community 83"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 84 - "Community 84"
Cohesion: 0.18
Nodes (12): post_quiz(), mongo_docs(), play_everything(), _snapshot_mongo(), test_activity_has_all_types(), test_backfill_fills_gaps_next_to_live_records(), test_backfill_inmemory(), test_backfill_rebuilds_mongo() (+4 more)

### Community 85 - "Community 85"
Cohesion: 0.13
Nodes (6): ask(), gen(), format_sse(), get_event_db_factory(), open_db(), _recorder()

### Community 87 - "Community 87"
Cohesion: 0.17
Nodes (3): GoogleError, GoogleOAuth, GoogleProfile

### Community 88 - "Community 88"
Cohesion: 0.26
Nodes (6): merge_guest(), _stats_row(), Event, QuizAttempt, SessionAction, UserStats

### Community 89 - "Community 89"
Cohesion: 0.18
Nodes (10): missing_citation_ids(), Citation, CitationCheckError, _drop(), _ids(), test_all_scenario_citations_resolve(), test_invalid_scenario_stops_startup(), test_startup_fails_on_missing_citation() (+2 more)

### Community 90 - "Community 90"
Cohesion: 0.17
Nodes (6): eval_condition(), HasFacts, IllegalAction, ScenarioError, SessionFinished, JSON condition DSL (all, any, not, flag, gte, always)

### Community 91 - "Community 91"
Cohesion: 0.29
Nodes (8): dense(), exact(), _run(), scenario_chunks(), Scope, sparse_fts(), sparse_titles(), _where()

### Community 92 - "Community 92"
Cohesion: 0.26
Nodes (11): build_game_state(), _loaded(), _state(), test_decision_options_translated(), test_events_translated_and_typed(), test_evidence_visible_from_second_stage_with_flags(), test_finished_state_has_no_actions(), test_initial_state_stage_and_evidence() (+3 more)

### Community 93 - "Game Engine Core"
Cohesion: 0.28
Nodes (8): _freeze(), _chosen(), evaluate(), DecisionResult, EngineState, Outcome, Mistake, Recommendation

### Community 94 - "Community 94"
Cohesion: 0.21
Nodes (4): AccountUser, _lenient_uuid(), LoginIn, SignupIn

### Community 95 - "Community 95"
Cohesion: 0.24
Nodes (11): as_token(), calls(), do(), test_account_session_may_use_guest_ids(), test_expired_session_loses_access(), test_guests_work_without_login(), test_no_session_gets_401(), test_other_account_gets_403() (+3 more)

### Community 96 - "Community 96"
Cohesion: 0.22
Nodes (10): Api, stats(), test_profile_404_and_validation(), test_profile_get_patch(), test_stats_after_three_playthroughs_and_quiz(), test_stats_unfinished_session_counts_only_started(), test_streak_by_utc_days(), touch() (+2 more)

### Community 97 - "Community 97"
Cohesion: 0.20
Nodes (13): CC - Civil Code of Uzbekistan, consumer_dispute_001 (Faulty smartphone case), CPC - Civil Procedure Code of Uzbekistan, CPRL - Law of Uzbekistan 'On Consumer Rights Protection', GET /api/scenarios/{scenario_id}, All current corpus editions are drafts (verified_by empty, check_report.md reports errors), Current corpus (CONST, CC1, CC2, CPC, CPRL; ru and uz-Latn pages https://lex.uz/docs/<number>), citation_id (stable article identifier, e.g. CPRL.art.X) (+5 more)

### Community 98 - "Community 98"
Cohesion: 0.21
Nodes (11): Evidence document response {id, title, type, lines[]}, call(), LEGAL_KEYS, liveApi, newLatinTexts(), sse(), TEXT_KEYS, uzLatnUi() (+3 more)

### Community 99 - "Community 99"
Cohesion: 0.28
Nodes (8): article_label(), build_chunks(), _clean(), doc_title_for(), estimate_tokens(), make_header(), _text(), _tokens()

### Community 100 - "Community 100"
Cohesion: 0.16
Nodes (3): session_history(), _usable(), user_activity()

### Community 101 - "Community 101"
Cohesion: 0.15
Nodes (5): _dummy_hash(), hash_password(), loose_email(), normalize_email(), verify_password()

### Community 102 - "Community 102"
Cohesion: 0.21
Nodes (4): create_email_user(), find_by_email(), GoogleLinkError, upsert_google_user()

### Community 103 - "Community 103"
Cohesion: 0.23
Nodes (8): alembic_config(), client(), db_engine(), db_session(), db_url(), make_alembic_config(), mongo_store(), mongo_url()

### Community 104 - "Community 104"
Cohesion: 0.18
Nodes (4): _article_exists(), CitationEntry, link_citations(), _to_str()

### Community 105 - "Community 105"
Cohesion: 0.28
Nodes (5): SessionOutdatedError, build_session_doc(), event_dicts(), session_doc(), step_doc()

### Community 106 - "Community 106"
Cohesion: 0.40
Nodes (10): broken(), has(), q(), test_character_does_not_know_fact(), test_duplicate_question_id(), m(), test_results_stage_not_allowed(), test_unknown_character() (+2 more)

### Community 107 - "Community 107"
Cohesion: 0.24
Nodes (7): _opt(), path(), play(), loaded(), _result(), test_counterfactual_only_when_not_best_and_kind_is_exposed(), test_result_kind_and_label()

### Community 108 - "Community 108"
Cohesion: 0.23
Nodes (3): _articles(), diff_document(), _section()

### Community 109 - "Community 109"
Cohesion: 0.17
Nodes (4): get_summary(), GET /api/analytics/scenarios/{scenario_id}/summary (P1), Participant 3 (API, models, game engine, analytics owner), SQL views (v_session_metrics, v_learning_gain, v_mistakes)

### Community 110 - "Community 110"
Cohesion: 0.17
Nodes (3): get_history(), NullHistoryStore, test_null_store_history_from_postgres()

### Community 111 - "Community 111"
Cohesion: 0.24
Nodes (5): export_schemas(), _Model, Question, Quiz, QuizOption

### Community 112 - "Community 112"
Cohesion: 0.23
Nodes (12): CI backend job (critical pytest with a Postgres 16 + pgvector service), DATABASE_URL (Postgres), Explicit article reference lookup ('st. 15', '15-modda'), GET /api/legal/search, Hybrid legal search (explicit refs + vector top 30 + full-text/trigram top 30), pg_trgm, pgvector, PostgreSQL 16 (+4 more)

### Community 113 - "Community 113"
Cohesion: 0.31
Nodes (5): backfill(), BackfillResult, _ctx(), main(), build_store()

### Community 115 - "Community 115"
Cohesion: 0.49
Nodes (5): on_quiz_attempt(), on_session_finished(), on_session_started(), _row(), _touch()

### Community 116 - "Community 116"
Cohesion: 0.31
Nodes (10): Mezon: notes for Claude Code (CLAUDE.md), graphify-out/graph.html (interactive graph view), graphify-out/graph.json (graph data used by graphify query), graphify-out/GRAPH_REPORT.md (communities, god nodes, surprising connections, open questions), graphify CLI (graphify query / path / explain), Committed graphify knowledge graph (graphify-out/), Graphify local state in graphify-out/ (cache, manifest), git-ignored, /graphify skill (.claude/skills/graphify, installs graphifyy on first use) (+2 more)

### Community 117 - "Community 117"
Cohesion: 0.25
Nodes (9): Add a new law or edition (save lex.uz HTML -> name and place in raw/ -> update sources.yaml -> run --doc -> human review + activate -> citations.yaml, ingest-check, seed-dump), Debug step commands without DB (parse / segment / chunk --doc), --draft-activate flag (drafts loaded as active only into demo DB adolat_demo), make ingest ARGS="..." (legal_ingestion CLI, run from repo root with databases up), make ingest-check (integrity checks only), make seed-dump (build legal_data/seed.sql.gz: legal-table data with vectors, no schema; needs the db container), run command (full pipeline; --doc <key> for one document), sources-draft command (draft sources.yaml from downloaded pages, no DB or network; --force keeps filled fields) (+1 more)

### Community 118 - "Community 118"
Cohesion: 0.22
Nodes (3): SelectContent(), SelectScrollDownButton(), SelectScrollUpButton()

### Community 119 - "Community 119"
Cohesion: 0.33
Nodes (8): dash(), quiz(), test_dashboard_404(), test_dashboard_after_three_games(), test_dashboard_uz_latn(), test_knowledge_level_labels(), test_new_user_dashboard(), test_recommended_reasons()

### Community 120 - "Community 120"
Cohesion: 0.22
Nodes (3): fake(), FakeGoogle, gapp()

### Community 121 - "Community 121"
Cohesion: 0.27
Nodes (4): can_embed(), embed_texts(), EmbeddingCache, test_embed_texts_without_embedder()

### Community 122 - "Community 122"
Cohesion: 0.27
Nodes (4): to_search(), _Draft, _finish(), _structural()

### Community 124 - "Community 124"
Cohesion: 0.28
Nodes (3): get_scenario(), list_scenarios(), GET /api/scenarios

### Community 126 - "Community 126"
Cohesion: 0.22
Nodes (8): ACT_TITLES, actTitle(), Dict, QUIZ, RU, UZ, StoredSession, Locale

### Community 127 - "Community 127"
Cohesion: 0.32
Nodes (4): _signup(), test_audience_is_optional_and_validated(), test_patch_audience_owner_only(), test_signup_stores_audience()

### Community 129 - "Community 129"
Cohesion: 0.38
Nodes (3): get_article(), get_citation(), GET /api/legal/articles/{article_id}

### Community 130 - "Community 130"
Cohesion: 0.43
Nodes (4): ActivityItem, ActivityOut, HistoryStepOut, SessionHistoryOut

### Community 131 - "Community 131"
Cohesion: 0.33
Nodes (3): test_golden_path_via_api(), test_result_label_is_localized(), test_users_and_scenarios()

### Community 132 - "Community 132"
Cohesion: 0.29
Nodes (7): scripts, build, dev, i18n, lint, start, typecheck

### Community 133 - "Community 133"
Cohesion: 0.29
Nodes (6): allowBuilds, @parcel/watcher, sharp, @swc/core, unrs-resolver, minimumReleaseAgeExclude

### Community 134 - "Community 134"
Cohesion: 0.40
Nodes (3): fallback_language_note(), language_name(), unconfirmed_note()

### Community 135 - "Community 135"
Cohesion: 0.47
Nodes (3): _check(), test_everything_translated(), _texts()

### Community 136 - "Community 136"
Cohesion: 0.33
Nodes (3): no_network(), npc_client(), _make()

### Community 137 - "Community 137"
Cohesion: 0.33
Nodes (4): pnpm via corepack (corepack pnpm ..., pnpm@11.25.0 in package.json), packageManager, COREPACK_ENABLE_DOWNLOAD_PROMPT, dev-all.sh script

### Community 139 - "Community 139"
Cohesion: 0.83
Nodes (3): build_parser(), add(), _common()

### Community 140 - "Community 140"
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
- `sessions table (game sessions)` → `Opaque revocable server sessions (30-day sliding expiry)`  [AMBIGUOUS]
  frontend/AUTH.md · relation: conceptually_related_to
- `In-browser mock backend (localStorage)` → `Thin client: no game logic or scenario texts in the frontend`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to

## Knowledge Gaps
- **13 isolated node(s):** `adolat-ingestion`, `graphify-out/graph.html (interactive graph view)`, `graphify-out/GRAPH_REPORT.md (communities, god nodes, surprising connections, open questions)`, `anthropic SDK`, `multilingual-e5-large (local, passage:/query: prefixes)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1039 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Community 60` to `Community 0`, `Mentor API & Scenario Registry`, `Errors & CSRF`, `Community 9`, `Community 10`, `Ingestion Runs`, `Specs & Setup Docs`, `Community 16`, `NPC Tests`, `Google OAuth`, `Community 21`, `Community 22`, `Legal Data Pipeline Docs`, `Community 30`, `Community 32`, `Community 38`, `Test Fixtures`, `Community 47`, `Community 65`, `Community 71`, `Community 75`, `Community 76`, `Community 80`, `Community 85`, `Community 87`, `Community 103`, `Community 112`, `Community 113`, `Community 120`, `Community 123`?**
  _High betweenness centrality (0.118) - this node is a cross-community bridge._
- **Are the 63 inferred relationships involving `Settings` (e.g. with `classify_question()` and `get_llm()`) actually correct?**
  _`Settings` has 63 INFERRED edges - model-reasoned connections that need verification._
- **What connects `adolat-ingestion`, `graphify-out/graph.html (interactive graph view)`, `graphify-out/GRAPH_REPORT.md (communities, god nodes, surprising connections, open questions)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05275482093663912 - nodes in this community are weakly interconnected._
- **Why does `Mezon frontend README` connect `Specs & Setup Docs` to `Community 97`, `Community 98`, `Community 39`, `Court Play Screen`, `Community 41`, `Community 43`, `Community 76`, `Community 45`, `Specs & Setup Docs`, `Community 79`, `Community 48`, `Settings & Fonts`, `Community 50`, `Auth Form & UI Primitives`, `Community 31`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `GoogleOAuth` and `authlib (Starlette integration)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `courtroom.ts` and `Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._