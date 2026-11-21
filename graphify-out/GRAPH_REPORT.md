# Graph Report - mezon  (2026-11-21)

## Corpus Check
- 334 files · ~132,150 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3599 nodes · 9751 edges · 152 communities (128 shown, 24 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1130 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Court Play Screen
- Scenario Schema & Tests
- History Store & NPC Asking
- Community 4
- Mentor API & Scenario Registry
- Community 6
- Analytics & Dashboard
- Engine Replay Tests
- Auth Form & UI Primitives
- Community 10
- Community 11
- Frontend Dependencies
- Query Normalization
- Community 14
- Test Fixtures
- Community 16
- Community 17
- Community 18
- Specs & Setup Docs
- Community 20
- Errors & CSRF
- Community 22
- Game Engine Core
- NPC Tests
- Ingestion Runs
- Google OAuth
- Community 27
- Community 28
- Community 29
- Community 30
- Legal Data Pipeline Docs
- Community 32
- Life Situation Screen
- Community 34
- Community 35
- Game API Presenter
- Community 37
- Community 38
- Community 39
- Settings & Fonts
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- CI/CD Workflow
- Community 47
- Community 48
- Community 49
- Community 50
- User Profile
- Community 52
- Community 53
- Community 54
- Community 55
- Community 56
- Community 57
- Community 58
- Community 59
- Community 60
- Specs & Setup Docs
- Auth API & Sessions
- Community 63
- Community 64
- Community 65
- Scenario Loader
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
- Legal Citation Service
- Community 85
- Community 86
- Community 87
- Community 88
- Community 89
- Specs & Setup Docs
- Community 91
- Community 92
- Community 93
- Community 94
- Community 95
- Community 96
- Live API Client & Scripts
- Seed Dump
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
- Community 135

## God Nodes (most connected - your core abstractions)
1. `Settings` - 121 edges
2. `run()` - 52 edges
3. `User` - 44 edges
4. `IngestionError` - 43 edges
5. `react` - 39 edges
6. `HistoryStore` - 38 edges
7. `apply()` - 37 edges
8. `Event` - 37 edges
9. `Scenario` - 37 edges
10. `next-intl` - 36 edges

## Surprising Connections (you probably didn't know these)
- `GoogleOAuth` --conceptually_related_to--> `authlib (Starlette integration)`  [AMBIGUOUS]
  backend/app/auth/google.py → frontend/AUTH.md
- `ArticlePart` --implements--> `article_parts table`  [INFERRED]
  backend/app/models/legal.py → docs/INGESTION.md
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
- **Legal ingestion pipeline: validate -> parse -> normalize -> segment -> version -> chunk -> embed -> load -> link -> check** — docs_ingestion_validate_step, docs_ingestion_parse_step, docs_ingestion_normalize_step, docs_ingestion_segment_step, docs_ingestion_version_step, docs_ingestion_chunk_step, docs_ingestion_embed_step, docs_ingestion_load_step, docs_ingestion_link_step, docs_ingestion_check_step [EXTRACTED 1.00]
- **First local run: backend/.venv -> .env from .env.example -> Docker Desktop -> make demo-laws -> make dev-all** — docs_setup_backend_venv, docs_setup_env_file, docs_setup_docker_desktop, docs_setup_make_demo_laws, docs_setup_make_dev_all [EXTRACTED 1.00]
- **Case materials document flow: CaseFile panel -> api.document -> GET /api/sessions/{session_id}/evidence/{evidence_id} -> get_evidence_document -> build_evidence_document -> EvidenceDocument lines** — docs_frontend_case_file, frontend_components_play_case_file_casefile, frontend_lib_api_types_api_document, docs_backend_get_api_sessions_session_id_evidence_evidence_id, backend_app_api_sessions_get_evidence_document, backend_app_services_presenter_build_evidence_document, docs_backend_evidence_document [INFERRED 0.85]
- **User journey: Landing -> Cases -> Case intro -> Pretest -> Play -> Results -> Posttest / Mentor -> Dashboard** — docs_frontend_landing_screen, docs_frontend_cases_screen, docs_frontend_case_intro_screen, docs_frontend_quiz_screens, docs_frontend_court_simulator_screen, docs_frontend_results_screen, docs_frontend_mentor_screen, docs_frontend_dashboard_screen [EXTRACTED 1.00]
- **Life situation flow: 'Life situations' category -> SituationScreen on the play route -> claim letter to the seller** — scenarios_readme_life_situations, docs_frontend_case_tracks, docs_frontend_situation_screen, docs_frontend_claim_letter, frontend_components_play_situation_screen_situationscreen, frontend_components_common_claim_letter_claimletter [INFERRED 0.85]
- **Two case categories for everyone: card kind court | situation -> CaseKind -> /cases#track-situation and #track-court sections, linked from 'What's inside Mezon'** — docs_frontend_whats_inside_mezon, docs_frontend_case_tracks, scenarios_readme_life_situations, frontend_components_site_pitch_pitch, frontend_app_locale_app_cases_page_casespage, frontend_lib_api_types_casekind, backend_app_schemas_scenario_card [INFERRED 0.85]

## Communities (152 total, 24 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (75): AnthropicLLM, FakeLLM, RerankScore, RerankScores, MentorAnswer, MentorBlock, QueryClassification, first() (+67 more)

### Community 1 - "Court Play Screen"
Cohesion: 0.06
Nodes (42): CasePage(), fmt(), DashboardPage(), fmt(), DKINDS, KINDS, ResultsPage(), short() (+34 more)

### Community 2 - "Scenario Schema & Tests"
Cohesion: 0.06
Nodes (37): Action, _always(), Card, Character, Chose, Claim, Condition, DecisionPoint (+29 more)

### Community 3 - "History Store & NPC Asking"
Cohesion: 0.06
Nodes (16): ingest(), ask_npc(), backfill(), BackfillResult, _ctx(), main(), build_store(), get_history() (+8 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (32): _db_opener(), lifespan(), load_all(), ScenarioValidationError, find_missing_citations(), load_from_roots(), load_registry(), scenario_roots() (+24 more)

### Community 5 - "Mentor API & Scenario Registry"
Cohesion: 0.10
Nodes (8): post_events(), get_optional_user(), get_viewer(), require_path_session(), require_path_user(), Viewer, get_registry(), POST /api/events (P1)

### Community 6 - "Community 6"
Cohesion: 0.09
Nodes (27): AppLayout(), AccountArea(), initials(), DeskHeader(), LanguageSwitcher(), LOCALE_LABELS, SiteFooter(), SiteHeader() (+19 more)

### Community 7 - "Analytics & Dashboard"
Cohesion: 0.10
Nodes (29): build_dashboard(), _category_title(), _latest_attempts(), _level_label(), get_quiz(), _quiz_questions(), submit_attempt(), round_half_up() (+21 more)

### Community 8 - "Engine Replay Tests"
Cohesion: 0.09
Nodes (35): apply(), available_actions(), initial_state(), replay(), LoggedAction, play(), scenario(), to_log() (+27 more)

### Community 9 - "Auth Form & UI Primitives"
Cohesion: 0.07
Nodes (27): Claim letter builder to the seller with a stamp (components/common/claim-letter.tsx), SignInPage(), SignUpPage(), Auth form error messages (429 rate limit, 422 validation, network errors), AuthForm(), done(), google(), submit() (+19 more)

### Community 10 - "Community 10"
Cohesion: 0.08
Nodes (22): assert_demo_database(), Edition, _load(), load_edition(), LoadResult, lookup_existing(), _set_if_changed(), _update_existing() (+14 more)

### Community 11 - "Community 11"
Cohesion: 0.08
Nodes (19): classify_question(), load_session_context(), SessionContext, _article_label(), _call_mentor(), _history(), MentorPlan, prepare() (+11 more)

### Community 12 - "Frontend Dependencies"
Cohesion: 0.06
Nodes (45): eslintConfig, nextConfig, withNextIntl, dependencies, class-variance-authority@^0.7.1, cn@^0.5.2, lucide-react@^1.76.0, next@16.4.6 (+37 more)

### Community 13 - "Query Normalization"
Cohesion: 0.08
Nodes (23): rrf(), rrf_score(), detect_language(), cyr_to_lat(), lat_to_cyr(), normalize(), tokenize(), _ranks() (+15 more)

### Community 14 - "Community 14"
Cohesion: 0.09
Nodes (20): get_article(), get_citation(), search(), get_db(), embedder_dep(), Embedder, get_embedder(), base_normalize() (+12 more)

### Community 15 - "Test Fixtures"
Cohesion: 0.08
Nodes (16): NullEmbedder, get_now(), api(), Clock, clock(), game_client(), make_client(), seeded_db() (+8 more)

### Community 16 - "Community 16"
Cohesion: 0.07
Nodes (32): bootstrap.sh script, vm1 deployment (CI/CD + systemd), CI deploy job (main only: rsync to /opt/mezon/src + ssh sudo mezon-deploy --sha <sha> <backend|frontend|all>), /etc/mezon/frontend.build.env (NEXT_PUBLIC_API_MODE=mock|live, NEXT_PUBLIC_GOOGLE_AUTH; missing keys are appended), Frontend -> real backend (NEXT_PUBLIC_API_MODE=live in frontend.build.env, baked in at build time), Manual deploy (Actions -> CI/CD -> Run workflow: all, frontend or backend), mockApi, In-browser mock backend (localStorage) (+24 more)

### Community 17 - "Community 17"
Cohesion: 0.09
Nodes (29): loaded(), mistake_titles(), _opt(), path(), play(), loaded(), _result(), test_counterfactual_only_when_not_best_and_kind_is_exposed() (+21 more)

### Community 18 - "Community 18"
Cohesion: 0.09
Nodes (30): _ids(), loaded(), mistake_titles(), _opt(), path(), play(), run(), sc() (+22 more)

### Community 19 - "Specs & Setup Docs"
Cohesion: 0.07
Nodes (30): Courtroom characters and animations (judge, player, plaintiff, defendant rep, witness/expert, secretary), Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses), next-intl (locale in URL), Phaser court scene (640x360, pixelArt, Scale.FIT), SketchSwitcher(), Court(), Props, bubble() (+22 more)

### Community 20 - "Community 20"
Cohesion: 0.09
Nodes (17): log(), main(), _activate(), build_parser(), add(), _common(), _debug_steps(), _dispatch() (+9 more)

### Community 21 - "Errors & CSRF"
Cohesion: 0.07
Nodes (27): get_current_user(), AppError, AuthProviderDisabledError, DbUnavailableError, EmailExistsError, error_response(), ForbiddenError, IllegalActionError (+19 more)

### Community 22 - "Community 22"
Cohesion: 0.10
Nodes (30): _ids(), loaded(), mistake_titles(), _opt(), path(), play(), _reach_motions(), run() (+22 more)

### Community 23 - "Game Engine Core"
Cohesion: 0.13
Nodes (25): _add_score(), _award_forecasts(), _enter(), _freeze(), _is_available(), _run_effects(), _settle(), _Work (+17 more)

### Community 24 - "NPC Tests"
Cohesion: 0.08
Nodes (19): NpcAnswer, NpcAskRequest, NpcClassification, NpcReply, NpcFakeLLM, npc_events(), test_event_recorded(), test_llm_bad_or_failed_reply_falls_back() (+11 more)

### Community 25 - "Ingestion Runs"
Cohesion: 0.11
Nodes (28): main(), assert_no_drafts(), can_embed(), embed_texts(), EditionOutcome, run(), statuses(), test_cli_draft_activate_refused_outside_demo_database() (+20 more)

### Community 26 - "Google OAuth"
Cohesion: 0.11
Nodes (25): pkce_challenge(), safe_next(), OAuthState, sha(), assert_failed(), callback(), start(), test_bad_id_token_rejected() (+17 more)

### Community 27 - "Community 27"
Cohesion: 0.11
Nodes (28): _check_graph(), collect_citation_ids(), collect_text_keys(), _conditions(), _dump(), _dups(), _effect_lists(), iter_text_keys() (+20 more)

### Community 28 - "Community 28"
Cohesion: 0.08
Nodes (28): test_document_locale_and_unknown(), test_documents_follow_the_case_file(), GET /api/health, GET /api/scenarios, GET /api/sessions/{session_id}/evidence/{evidence_id}, Case selection screen /[locale]/cases, Guest home page Pitch (components/site/pitch.tsx, case-folder design), HomeGate (signed-in user's case desk on the home page) (+20 more)

### Community 29 - "Community 29"
Cohesion: 0.09
Nodes (15): allowed_questions(), answer_question(), _choice_model(), classify_lexical(), classify_llm(), NpcResult, _numbers(), rephrase() (+7 more)

### Community 30 - "Community 30"
Cohesion: 0.09
Nodes (29): allowed_origins(), csrf_guard(), origin_of(), CsrfError, AUTH_IP_MAX_REQUESTS=120 per 15 min (code default 30), /etc/mezon/backend.env (backend secrets, chmod 600), Backend-owned sign-in (/api/auth/*, cookie mezon_session), CSRF Origin check (POSTs from any other Origin get 403 CSRF_FAILED) (+21 more)

### Community 31 - "Legal Data Pipeline Docs"
Cohesion: 0.10
Nodes (33): Participant 2 (legal/, rag/, ai/ and ingestion pipeline owner), Add a new law or edition (save lex.uz HTML -> name and place in raw/ -> update sources.yaml -> run --doc -> human review + activate -> citations.yaml, ingest-check, seed-dump), legal_data/processed/check_report.md (integrity report, prints edition version ids), citations.yaml entry (citation_id, document_key, article_number, part, topic, verified_by; template legal_data/citations.example.yaml), Stable citation id <document_key>.art.<number> (e.g. CPRL.art.14), All current corpus editions are drafts (verified_by empty, check_report.md reports errors), Debug step commands without DB (parse / segment / chunk --doc), Legal data kept in git (legal_data/raw/ as source of truth, sources.yaml, citations.yaml, processed/check_report.md, article_counts.json) (+25 more)

### Community 32 - "Community 32"
Cohesion: 0.12
Nodes (18): _check_citations(), _check_counts(), _check_db(), CheckResult, _clip(), find_gaps(), Issue, _label() (+10 more)

### Community 33 - "Life Situation Screen"
Cohesion: 0.10
Nodes (30): review_<evidence_id> game action, ActionMenu, Case materials panel (CaseFile, components/play/case-file.tsx), Case list categories 'Life situations' and 'Court cases' (the same for everyone), Court simulator screen /[locale]/play/[sessionId] (main screen; SituationScreen for kind: "situation" cases), DECISION modal dialog, DialogueBox, Event queue playback (+22 more)

### Community 34 - "Community 34"
Cohesion: 0.11
Nodes (13): Raw file naming <document_key>_<language>_<date>.html (e.g. CPRL_ru_2026-11-20.html; ru, uz-Latn or uz-Cyrl), Paths, chunk_edition(), parse_edition(), prepare_edition(), RunResult, segment_edition(), validate() (+5 more)

### Community 35 - "Community 35"
Cohesion: 0.11
Nodes (27): login(), signup(), _flags(), test_auth_posts_require_origin(), test_cookie_flags_secure_on(), test_cookie_secure_off_for_local(), test_csrf_not_applied_to_get(), test_csrf_on_regular_posts_only_with_cookie() (+19 more)

### Community 36 - "Game API Presenter"
Cohesion: 0.12
Nodes (29): ActionParams, ActionRequest, ActionView, CharacterView, ClaimView, CreateSession, CreateUser, DecisionView (+21 more)

### Community 37 - "Community 37"
Cohesion: 0.11
Nodes (19): Block, label(), MentorPage(), Msg, Askable, EXAMPLES, Msg, NpcPanel() (+11 more)

### Community 38 - "Community 38"
Cohesion: 0.10
Nodes (10): account_out(), create_email_user(), find_by_email(), GoogleLinkError, upsert_google_user(), User, AccountUser, _lenient_uuid() (+2 more)

### Community 39 - "Community 39"
Cohesion: 0.19
Nodes (15): create_user(), get_evidence_document(), get_loaded(), get_result(), _get_session(), get_state(), load_replayed(), _log() (+7 more)

### Community 40 - "Settings & Fonts"
Cohesion: 0.11
Nodes (24): FONT_VAR, SettingsPage(), LocaleLayout(), viewport, PageTitle(), AuthErrorNotice(), Providers(), RadioGroup() (+16 more)

### Community 41 - "Community 41"
Cohesion: 0.11
Nodes (24): FakeEmbedder, client(), dense_client(), factory(), make(), search(), test_dense_adds_to_sparse_score(), test_dense_branch_orders_by_vector() (+16 more)

### Community 42 - "Community 42"
Cohesion: 0.12
Nodes (9): EvidenceDocument, build_evidence_document(), build_game_state(), build_result(), build_scenario_card(), present_actions(), present_evidence(), stage_index() (+1 more)

### Community 43 - "Community 43"
Cohesion: 0.11
Nodes (7): upgrade(), upgrade(), _int(), upgrade(), upgrade(), upgrade(), downgrade()

### Community 44 - "Community 44"
Cohesion: 0.11
Nodes (17): get_llm(), health(), HealthResponse, clear_cookie(), set_cookie(), Settings, get_reranker(), test_no_key_means_no_llm() (+9 more)

### Community 45 - "Community 45"
Cohesion: 0.13
Nodes (15): test_same_log_same_state(), _check(), test_everything_translated(), test_uz_cyrl_falls_back(), _texts(), _err(), session(), test_decision_without_valid_option_is_illegal() (+7 more)

### Community 46 - "CI/CD Workflow"
Cohesion: 0.07
Nodes (30): VM1_KNOWN_HOSTS (GitHub Actions variable), VM1_SSH_KEY (GitHub Actions secret), steps, environment, if, name, needs, runs-on (+22 more)

### Community 47 - "Community 47"
Cohesion: 0.12
Nodes (11): LLM, build_rerank_user(), CandidateForPrompt, _llm_factory(), LLMReranker, NullReranker, order_by_scores(), Reranker (+3 more)

### Community 48 - "Community 48"
Cohesion: 0.11
Nodes (11): SessionOutdatedError, eval_condition(), HasFacts, IllegalAction, ScenarioError, SessionFinished, build_session_doc(), event_dicts() (+3 more)

### Community 49 - "Community 49"
Cohesion: 0.17
Nodes (22): action(), broken(), has(), stage(), test_add_evidence_unknown(), m(), test_citation_not_listed(), test_dead_end_stage() (+14 more)

### Community 50 - "Community 50"
Cohesion: 0.15
Nodes (15): _same_word(), hybrid_search(), matches_document(), dense(), exact(), prefix_stem(), _run(), scenario_chunks() (+7 more)

### Community 51 - "User Profile"
Cohesion: 0.17
Nodes (13): create_user(), get_user(), _get_user(), get_user_sessions(), _outcome_title(), patch_user(), _profile(), SessionAction (+5 more)

### Community 52 - "Community 52"
Cohesion: 0.15
Nodes (18): load_sources(), blocks(), document_entry(), html_doc(), version_entry(), write_docx(), write_source(), write_sources_yaml() (+10 more)

### Community 53 - "Community 53"
Cohesion: 0.09
Nodes (11): get_dashboard(), get_quiz(), post_attempt(), GET /api/quiz/{scenario_id}?kind=pre|post, GET /api/users/{user_id}/dashboard, Legal literacy level (0-100), Learning gain (post - pre), POST /api/quiz/{scenario_id}/attempts (+3 more)

### Community 54 - "Community 54"
Cohesion: 0.14
Nodes (6): MongoHistoryStore, run(), mongo_store(), test_live_session_document_grows_and_finishes(), test_push_step_is_idempotent(), test_unreachable_mongo_does_not_break_game()

### Community 55 - "Community 55"
Cohesion: 0.11
Nodes (17): get_citation_view(), get_citation_views(), _is_valid_on(), _pick(), seeded(), test_all_scenario_citations_resolve(), test_article_view(), test_current_edition_on_date() (+9 more)

### Community 56 - "Community 56"
Cohesion: 0.21
Nodes (16): Base, Article, ArticlePart, Chunk, DocumentVersion, LegalDocument, _article(), _cite() (+8 more)

### Community 57 - "Community 57"
Cohesion: 0.09
Nodes (26): environment, healthcheck, image, ports, volumes, POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER (+18 more)

### Community 58 - "Community 58"
Cohesion: 0.08
Nodes (26): ActionView, GameEvent (say, react, stage_changed, evidence_added, score, legal_note, mistake), GameState, ActionKind, ActionView, ArticlePartView, CharacterView, DashboardOut (+18 more)

### Community 59 - "Community 59"
Cohesion: 0.15
Nodes (17): sources-draft command (draft sources.yaml from downloaded pages, no DB or network; --force keeps filled fields), build_draft(), _d(), _empty(), merge_existing(), merge(), _note(), PageInfo (+9 more)

### Community 60 - "Community 60"
Cohesion: 0.13
Nodes (25): tx(), action(), apply(), availableActions(), EngineState, evaluate(), IllegalAction, initial() (+17 more)

### Community 61 - "Specs & Setup Docs"
Cohesion: 0.15
Nodes (25): main(), ADOLAT Backend specification (BACKEND.md), ADOLAT (legal-education court simulator), CORS_ORIGINS (frontend address), SQLAlchemy 2 (sync, psycopg 3), How legal data and cases are assembled (DATA.md), Add a new case (copy test_consumer -> change scenario_id and texts -> citations in citations.yaml + make demo-laws -> make demo starts cleanly), --draft-activate flag (drafts loaded as active only into demo DB adolat_demo) (+17 more)

### Community 62 - "Auth API & Sessions"
Cohesion: 0.19
Nodes (9): _base(), _clear_bind(), _fail(), google_callback(), google_start(), logout(), me(), _open_session() (+1 more)

### Community 63 - "Community 63"
Cohesion: 0.11
Nodes (21): gemma3:27b (production language model served by Ollama on the GPU server), GPU server: Ollama (gemma3:27b + bge-m3) on a vast.ai RTX 3090, listening only on 127.0.0.1:11434, /etc/mezon/llm-tunnel.env (GPU_HOST, GPU_PORT, GPU_USER, TUNNEL_BIND, TUNNEL_PORT; template env/llm-tunnel.env.example), /etc/mezon/llm-tunnel.key (tunnel-only key; restricted on the GPU server to port-forwarding 127.0.0.1:11434, no shell), /etc/mezon/llm-tunnel.known_hosts (pinned ED25519 host key of the GPU server), mezon-llm-tunnel.service (SSH tunnel to the GPU server's Ollama, exposed on vm1 docker0 172.17.0.1:11435), Re-pointing the tunnel after vast.ai recreates the instance (update llm-tunnel.env, rescan and verify host key, authorize llm-tunnel.key.pub, restart mezon-llm-tunnel), env_file (+13 more)

### Community 64 - "Community 64"
Cohesion: 0.11
Nodes (20): CHARACTERS, citation(), Db, delay(), getSession(), load(), mentorStream(), mergeMockGuest() (+12 more)

### Community 65 - "Community 65"
Cohesion: 0.12
Nodes (11): NullHistoryStore, mongo_docs(), play_everything(), _snapshot_mongo(), test_activity_has_all_types(), test_backfill_fills_gaps_next_to_live_records(), test_backfill_inmemory(), test_backfill_rebuilds_mongo() (+3 more)

### Community 66 - "Scenario Loader"
Cohesion: 0.13
Nodes (8): fallback_chain(), translate(), LoadedScenario, export_schemas(), _Model, Question, Quiz, QuizOption

### Community 67 - "Community 67"
Cohesion: 0.17
Nodes (10): EmbedderError, OllamaEmbedder, test_connection_error_is_embedder_error(), test_embed_batches_and_request_shape(), test_embed_empty_makes_no_request(), test_embed_query_returns_vector(), test_errors_raise_in_embed_and_skip_in_query(), test_registry() (+2 more)

### Community 68 - "Community 68"
Cohesion: 0.13
Nodes (15): ArticleRef, canonical_number(), DocHint, extract_article_numbers(), extract_refs(), _hint_in(), _numbers(), strip_source_marks() (+7 more)

### Community 69 - "Community 69"
Cohesion: 0.17
Nodes (11): _classes(), _Collector, _inline_text(), iter_lexuz(), parse_docx(), parse_file(), parse_html(), _parse_lexuz() (+3 more)

### Community 70 - "Community 70"
Cohesion: 0.15
Nodes (7): create_session(), get_evidence_document(), get_result(), get_session(), patch_session(), post_action(), GET /api/sessions/{session_id}

### Community 71 - "Community 71"
Cohesion: 0.10
Nodes (21): entrypoint.sh script, build, depends_on, environment, extra_hosts, ports, volumes, condition (+13 more)

### Community 72 - "Community 72"
Cohesion: 0.13
Nodes (4): get_google(), GoogleError, GoogleOAuth, GoogleProfile

### Community 73 - "Community 73"
Cohesion: 0.23
Nodes (16): GameSession, UserStats, test_events_without_session(), test_more_than_50_events_is_422(), add_session(), login(), signup(), seed_guest() (+8 more)

### Community 74 - "Community 74"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 75 - "Community 75"
Cohesion: 0.13
Nodes (17): convertPlain(), convertWord(), fit(), IOTATED, isUpper(), latnToCyrl(), LETTERS, NEW_LETTERS (+9 more)

### Community 76 - "Community 76"
Cohesion: 0.10
Nodes (6): demo_db(), test_all_citations_resolve_on_legal_date(), demo_db(), test_all_citations_resolve_on_legal_date(), demo_db(), test_all_citations_resolve_on_legal_date()

### Community 77 - "Community 77"
Cohesion: 0.19
Nodes (8): check(), clear_failures(), client_ip(), record_failure(), record_request(), _retry_after(), RateLimitedError, AuthAttempt

### Community 78 - "Community 78"
Cohesion: 0.17
Nodes (16): mezon-backend.service (127.0.0.1:8000), mezon-db.service (Postgres container), mezon-frontend.service (127.0.0.1:3000), mezon-mongo.service (MongoDB history), mezon-mongodata docker volume, mezon-pgdata docker volume, nginx reverse proxy (/api/* -> :8000, everything else -> :3000), vm1 (vm1.modeus.cc) (+8 more)

### Community 79 - "Community 79"
Cohesion: 0.13
Nodes (7): ask(), gen(), format_sse(), get_event_db_factory(), open_db(), _recorder(), record()

### Community 80 - "Community 80"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 81 - "Community 81"
Cohesion: 0.18
Nodes (7): _article_keys(), _chunk_keys(), _dedupe(), load_gold(), rank_all(), run_eval(), test_eval_without_gold_file_gives_clear_message()

### Community 82 - "Community 82"
Cohesion: 0.17
Nodes (9): estimate_tokens(), clean_text(), _blocks(), test_chunks(), test_clean_text_only_junk(), test_parse_removes_junk_and_keeps_order(), test_segment_chapter_title_on_next_line(), test_segment_dash_number_kept_and_duplicates_reported() (+1 more)

### Community 83 - "Community 83"
Cohesion: 0.20
Nodes (14): CitationView, Edition status (current | historical | unconfirmed), GET /api/legal/citations/{citation_id}, GET /api/sessions/{session_id}/result, Mentor SSE events (sources, block, done, error), POST /api/mentor/ask (text/event-stream), 409 SESSION_NOT_FINISHED (result requested before the end of the game), sse-starlette (+6 more)

### Community 84 - "Legal Citation Service"
Cohesion: 0.23
Nodes (8): _build(), get_article_view(), get_legal_acts(), _title(), ArticlePartView, CitationView, EditionView, LegalActView

### Community 86 - "Community 86"
Cohesion: 0.16
Nodes (8): alembic_config(), create_migrated_database(), ing_db_url(), ing_engine(), session_factory(), Workspace, ws(), demo_factory()

### Community 87 - "Community 87"
Cohesion: 0.13
Nodes (7): email_hash(), legal_data/processed/*.articles.jsonl (parsed articles, source of article numbers), legal_data/processed/embeddings_cache/ (vector cache), Legal data not in git (processed/*.jsonl, processed/embeddings_cache/, seed.sql.gz via Git LFS), EmbeddingCache, text_hash(), content_hash()

### Community 88 - "Community 88"
Cohesion: 0.21
Nodes (11): Api, post_quiz(), stats(), test_profile_404_and_validation(), test_profile_get_patch(), test_stats_after_three_playthroughs_and_quiz(), test_stats_unfinished_session_counts_only_started(), test_streak_by_utc_days() (+3 more)

### Community 89 - "Community 89"
Cohesion: 0.19
Nodes (12): loaded(), _opt(), path(), run(), sc(), test_best_path_is_a_win_with_max_score(), test_claim_copy_appears_only_after_written_claim(), test_every_stage_offers_a_way_forward() (+4 more)

### Community 90 - "Specs & Setup Docs"
Cohesion: 0.18
Nodes (12): Monorepo layout (frontend/ Next.js 16 + Phaser 4, backend/ FastAPI + Postgres/pgvector + MongoDB history, deploy/vm1/ systemd + CI/CD, docs/ specs), FastAPI, locale parameter (ru | uz-Latn | uz-Cyrl), Participant 4 (legal content, localization texts, Legal QA), PATCH /api/sessions/{session_id}, ADOLAT Frontend specification (FRONTEND.md), Generated API client (openapi-typescript + openapi-fetch, make api-client), Next.js (App Router) (+4 more)

### Community 91 - "Community 91"
Cohesion: 0.13
Nodes (12): Explicit article reference lookup ('st. 15', '15-modda'), GET /api/legal/search, Hybrid legal search (explicit refs + vector top 30 + full-text/trigram top 30), LLM_MODEL_FAST (claude-haiku-5-5), AI Legal Mentor RAG pipeline, POST /api/sessions/{session_id}/npc/{character_id}/ask (P2), Query classification (article_lookup | concept | case_specific | out_of_scope), Query language detection (alphabet + stop words) (+4 more)

### Community 92 - "Community 92"
Cohesion: 0.16
Nodes (8): normalize_blocks(), blocks(), html(), test_chapter_patterns(), test_normalize_keeps_lex_id(), test_section_patterns(), test_segment_lexuz(), test_segment_skips_part_subsection_paragraph_headings()

### Community 93 - "Community 93"
Cohesion: 0.23
Nodes (10): create_app(), build(), alembic_config(), client(), db_engine(), db_session(), db_url(), make_alembic_config() (+2 more)

### Community 94 - "Community 94"
Cohesion: 0.22
Nodes (9): missing_citation_ids(), Citation, CitationCheckError, _drop(), _ids(), test_all_scenario_citations_resolve(), test_invalid_scenario_stops_startup(), test_startup_fails_on_missing_citation() (+1 more)

### Community 95 - "Community 95"
Cohesion: 0.24
Nodes (11): as_token(), calls(), do(), test_account_session_may_use_guest_ids(), test_expired_session_loses_access(), test_guests_work_without_login(), test_no_session_gets_401(), test_other_account_gets_403() (+3 more)

### Community 96 - "Community 96"
Cohesion: 0.20
Nodes (13): CC - Civil Code of Uzbekistan, consumer_dispute_001 (Faulty smartphone case), CPC - Civil Procedure Code of Uzbekistan, CPRL - Law of Uzbekistan 'On Consumer Rights Protection', GET /api/scenarios/{scenario_id}, Current corpus (CONST, CC1, CC2, CPC, CPRL; ru and uz-Latn pages https://lex.uz/docs/<number>), Case intro screen /[locale]/cases/[id], citation_id (stable article identifier, e.g. CPRL.art.X) (+5 more)

### Community 97 - "Live API Client & Scripts"
Cohesion: 0.20
Nodes (10): call(), convertTexts(), LEGAL_KEYS, localizeTexts(), sse(), TEXT_KEYS, uiLang(), ApiError (+2 more)

### Community 98 - "Seed Dump"
Cohesion: 0.16
Nodes (5): _article_exists(), CitationEntry, link_citations(), LinkError, _to_str()

### Community 99 - "Community 99"
Cohesion: 0.16
Nodes (3): session_history(), _usable(), user_activity()

### Community 100 - "Community 100"
Cohesion: 0.23
Nodes (7): app(), app_and_client(), app_factory(), client(), make_account(), make(), make_guest()

### Community 101 - "Community 101"
Cohesion: 0.15
Nodes (5): _dummy_hash(), hash_password(), loose_email(), normalize_email(), verify_password()

### Community 102 - "Community 102"
Cohesion: 0.32
Nodes (6): create_session(), hash_token(), resolve(), revoke_all(), revoke_token(), AuthSession

### Community 103 - "Community 103"
Cohesion: 0.14
Nodes (13): NEXT_PUBLIC_API_MODE, args, context, build, ports, restart, services, frontend (+5 more)

### Community 104 - "Community 104"
Cohesion: 0.14
Nodes (10): Palette (navy #0F1B2D, gold #C9A227, warm white #F5F1E8, teal #1FA39A, terracotta #C8553D), commissioner, fontVariables, nunito, onest, oswald, plexMono, plexSans (+2 more)

### Community 105 - "Community 105"
Cohesion: 0.22
Nodes (6): to_search(), _Draft, _finish(), segment(), _structural(), test_segment_lexuz_preamble_and_unknown_heading()

### Community 106 - "Community 106"
Cohesion: 0.23
Nodes (4): get_url(), run_migrations_offline(), run_migrations_online(), Alembic migrations

### Community 107 - "Community 107"
Cohesion: 0.23
Nodes (3): _articles(), diff_document(), _section()

### Community 108 - "Community 108"
Cohesion: 0.17
Nodes (4): get_summary(), GET /api/analytics/scenarios/{scenario_id}/summary (P1), Participant 3 (API, models, game engine, analytics owner), SQL views (v_session_metrics, v_learning_gain, v_mistakes)

### Community 109 - "Community 109"
Cohesion: 0.30
Nodes (10): _loaded(), _state(), test_decision_options_translated(), test_events_translated_and_typed(), test_evidence_visible_from_second_stage_with_flags(), test_finished_state_has_no_actions(), test_initial_state_stage_and_evidence(), test_mistake_events_hidden_unless_revealed() (+2 more)

### Community 110 - "Community 110"
Cohesion: 0.35
Nodes (7): article_label(), build_chunks(), _clean(), doc_title_for(), make_header(), _text(), _tokens()

### Community 112 - "Community 112"
Cohesion: 0.49
Nodes (5): on_quiz_attempt(), on_session_finished(), on_session_started(), _row(), _touch()

### Community 113 - "Community 113"
Cohesion: 0.31
Nodes (10): Mezon: notes for Claude Code (CLAUDE.md), graphify-out/graph.html (interactive graph view), graphify-out/graph.json (graph data used by graphify query), graphify-out/GRAPH_REPORT.md (communities, god nodes, surprising connections, open questions), graphify CLI (graphify query / path / explain), Committed graphify knowledge graph (graphify-out/), Graphify local state in graphify-out/ (cache, manifest), git-ignored, /graphify skill (.claude/skills/graphify, installs graphifyy on first use) (+2 more)

### Community 114 - "Community 114"
Cohesion: 0.22
Nodes (3): SelectContent(), SelectScrollDownButton(), SelectScrollUpButton()

### Community 115 - "Community 115"
Cohesion: 0.22
Nodes (3): fake(), FakeGoogle, gapp()

### Community 117 - "Community 117"
Cohesion: 0.22
Nodes (8): ACT_TITLES, actTitle(), Dict, QUIZ, RU, UZ, StoredSession, Locale

### Community 122 - "Community 122"
Cohesion: 0.32
Nodes (8): Local pre-push checks (frontend: pnpm i18n && pnpm typecheck && pnpm build; backend: make test), scripts, build, dev, i18n, lint, start, typecheck

### Community 123 - "Community 123"
Cohesion: 0.29
Nodes (8): DATABASE_URL (Postgres), GET /api/legal/articles/{article_id}, pg_trgm, pgvector, PostgreSQL 16, article_parts table, articles table, chunks table (embedding vector + tsv)

### Community 124 - "Community 124"
Cohesion: 0.32
Nodes (7): EMBEDDER (embedding model selection), BGE-M3 (local embedding model), embed step (embed.py), Embedder.embed(texts, kind=passage|query), eval/gold.jsonl (~40 questions, 20 ru + 20 uz-Latn), multilingual-e5-large (local, passage:/query: prefixes), bge-m3 via Ollama (EMBEDDER=ollama-bge-m3, ~1.2 GB)

### Community 125 - "Community 125"
Cohesion: 0.43
Nodes (4): ActivityItem, ActivityOut, HistoryStepOut, SessionHistoryOut

### Community 126 - "Community 126"
Cohesion: 0.29
Nodes (3): test_me_without_session_is_401(), GET /api/auth/me, AuthService

### Community 127 - "Community 127"
Cohesion: 0.33
Nodes (3): test_golden_path_via_api(), test_result_label_is_localized(), test_users_and_scenarios()

### Community 128 - "Community 128"
Cohesion: 0.38
Nodes (6): events table (analytics), POST /api/sessions, POST /api/users, sessions table (game sessions), users table, Anonymous user_id in localStorage

### Community 129 - "Community 129"
Cohesion: 0.29
Nodes (6): allowBuilds, @parcel/watcher, sharp, @swc/core, unrs-resolver, minimumReleaseAgeExclude

### Community 130 - "Community 130"
Cohesion: 0.38
Nodes (4): normalize_number(), _ord_alt(), _ord_alt_ru(), to_roman()

### Community 131 - "Community 131"
Cohesion: 0.40
Nodes (3): fallback_language_note(), language_name(), unconfirmed_note()

### Community 132 - "Community 132"
Cohesion: 0.33
Nodes (3): no_network(), npc_client(), _make()

### Community 133 - "Community 133"
Cohesion: 0.33
Nodes (4): pnpm via corepack (corepack pnpm ..., pnpm@11.25.0 in package.json), packageManager, COREPACK_ENABLE_DOWNLOAD_PROMPT, dev-all.sh script

### Community 135 - "Community 135"
Cohesion: 0.67
Nodes (3): npx, next-devtools, shadcn

## Ambiguous Edges - Review These
- `GoogleOAuth` → `authlib (Starlette integration)`  [AMBIGUOUS]
  frontend/AUTH.md · relation: conceptually_related_to
- `courtroom.ts` → `Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `In-browser mock backend (localStorage)` → `Thin client: no game logic or scenario texts in the frontend`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `Uzbek Cyrillic -> Latin transliteration table (search only)` → `Uzbek Latin 2026 alphabet (law of 21.10.2026)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `types.ts` → `Generated API client (openapi-typescript + openapi-fetch, make api-client)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to

## Knowledge Gaps
- **13 isolated node(s):** `adolat-ingestion`, `graphify-out/graph.html (interactive graph view)`, `graphify-out/GRAPH_REPORT.md (communities, god nodes, surprising connections, open questions)`, `Uzbek text is legally binding; Russian lex.uz texts are unofficial translations`, `Next.js agent rules (AGENTS.md)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1018 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Community 44` to `Community 0`, `History Store & NPC Asking`, `Community 4`, `Mentor API & Scenario Registry`, `Community 11`, `Query Normalization`, `Community 14`, `Test Fixtures`, `Community 20`, `NPC Tests`, `Ingestion Runs`, `Google OAuth`, `Community 29`, `Community 30`, `Community 47`, `Community 50`, `Specs & Setup Docs`, `Community 63`, `Community 67`, `Community 72`, `Community 77`, `Community 78`, `Community 79`, `Community 81`, `Community 91`, `Community 93`, `Community 100`, `Community 102`, `Community 115`, `Community 123`, `Community 124`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Are the 64 inferred relationships involving `Settings` (e.g. with `classify_question()` and `get_llm()`) actually correct?**
  _`Settings` has 64 INFERRED edges - model-reasoned connections that need verification._
- **What connects `adolat-ingestion`, `graphify-out/graph.html (interactive graph view)`, `graphify-out/GRAPH_REPORT.md (communities, god nodes, surprising connections, open questions)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.058786346396965866 - nodes in this community are weakly interconnected._
- **Why does `Accounts and Google SSO (AUTH.md)` connect `Community 30` to `Community 128`, `Life Situation Screen`, `Court Play Screen`, `Auth Form & UI Primitives`, `Community 16`, `Specs & Setup Docs`, `Auth API & Sessions`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `GoogleOAuth` and `authlib (Starlette integration)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `courtroom.ts` and `Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._