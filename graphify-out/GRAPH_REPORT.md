# Graph Report - mezon  (2026-11-21)

## Corpus Check
- 318 files · ~133,468 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3382 nodes · 9196 edges · 174 communities (142 shown, 32 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 940 edges (avg confidence: 0.91)
- Token cost: 171,247 input · 0 output

## Community Hubs (Navigation)
- Errors & Analytics
- History Store & Mentor API
- Test Fixtures
- i18n & Navigation
- Scenario Loading & Validation
- UI Primitives
- Court Play Screen & NPC Panel
- Quiz & Results UI
- Frontend Dependencies
- NPC Answering
- Mentor Reranking
- Ingestion Errors & Seed Dump
- Legal Source Registry
- LLM Settings & Mentor
- Ingestion Pipeline & Checks
- Ingestion Runs
- NPC Tests
- Frontend Spec & Docs
- Legal Search API
- Hybrid Search Tests
- Scenario Schema
- Legal Data Pipeline Docs
- Ingestion CLI
- Game API Presenter
- Auth API
- Google OAuth Tests
- Email Auth Tests
- Settings & Fonts
- NPC Events & Activity
- User & Event Models
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
- Community 138
- Community 139
- Community 140
- Community 141
- Community 142
- Community 144
- Community 145
- Community 146
- Community 147
- Community 148
- Community 149
- Community 150
- Community 152
- Community 153
- Community 154
- Community 155
- Community 157

## God Nodes (most connected - your core abstractions)
1. `Settings` - 119 edges
2. `run()` - 52 edges
3. `HistoryStore` - 51 edges
4. `User` - 47 edges
5. `IngestionError` - 43 edges
6. `Event` - 40 edges
7. `apply()` - 39 edges
8. `initial_state()` - 37 edges
9. `Scenario` - 37 edges
10. `react` - 33 edges

## Surprising Connections (you probably didn't know these)
- `ArticlePart` --implements--> `article_parts table`  [INFERRED]
  backend/app/models/legal.py → docs/INGESTION.md
- `detect_language()` --implements--> `Query language detection (alphabet + stop words)`  [INFERRED]
  backend/app/rag/language.py → docs/BACKEND.md
- `extract_refs()` --implements--> `Explicit article reference lookup ('st. 15', '15-modda')`  [INFERRED]
  backend/app/rag/refs.py → docs/BACKEND.md
- `sanitize_text()` --implements--> `<source> tags treated as data, not instructions`  [INFERRED]
  backend/app/ai/prompts/sanitize.py → docs/BACKEND.md
- `Settings` --implements--> `Claude timeouts (LLM_MENTOR_TIMEOUT 20 s, LLM_FAST_TIMEOUT 4 s)`  [INFERRED]
  backend/app/config.py → docs/MODELS.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **AI mentor answer flow: detect language -> normalize -> classify -> hybrid search -> threshold refusal -> source-tagged context -> structured blocks -> validation -> SSE** — docs_backend_query_language_detection, docs_backend_query_normalization, docs_backend_query_classification, docs_backend_hybrid_search, docs_backend_insufficient_sources_refusal, docs_backend_source_tags_as_data, docs_backend_structured_answer_blocks, docs_backend_answer_block_validation, docs_backend_mentor_sse_events [EXTRACTED 1.00]
- **User journey: Landing -> Cases -> Case intro -> Pretest -> Play -> Results -> Posttest / Mentor -> Dashboard** — docs_frontend_landing_screen, docs_frontend_cases_screen, docs_frontend_case_intro_screen, docs_frontend_quiz_screens, docs_frontend_court_simulator_screen, docs_frontend_results_screen, docs_frontend_mentor_screen, docs_frontend_dashboard_screen [EXTRACTED 1.00]
- **Legal ingestion pipeline: validate -> parse -> normalize -> segment -> version -> chunk -> embed -> load -> link -> check** — docs_ingestion_validate_step, docs_ingestion_parse_step, docs_ingestion_normalize_step, docs_ingestion_segment_step, docs_ingestion_version_step, docs_ingestion_chunk_step, docs_ingestion_embed_step, docs_ingestion_load_step, docs_ingestion_link_step, docs_ingestion_check_step [EXTRACTED 1.00]
- **Ingestion pipeline run by make ingest ARGS="run": parse -> segment -> chunk -> embed -> load -> link -> check** — docs_data_pipeline_overview, ingestion_legal_ingestion_parse, ingestion_legal_ingestion_segment, ingestion_legal_ingestion_chunk, ingestion_legal_ingestion_embed, ingestion_legal_ingestion_load, ingestion_legal_ingestion_link, ingestion_legal_ingestion_check [INFERRED 0.85]
- **Edition verification flow: run (pending_review) -> human review of check_report.md -> fill verified_by in sources.yaml -> activate -> seed-dump** — docs_data_run_command, docs_data_check_report, docs_data_human_review_fields, docs_ingestion_activate_command, docs_data_make_seed_dump [EXTRACTED 1.00]
- **First local run: backend/.venv -> .env from .env.example -> Docker Desktop -> make demo-laws -> make dev-all** — docs_setup_backend_venv, docs_setup_env_file, docs_setup_docker_desktop, docs_setup_make_demo_laws, docs_setup_make_dev_all [EXTRACTED 1.00]

## Communities (174 total, 32 thin omitted)

### Community 0 - "Errors & Analytics"
Cohesion: 0.06
Nodes (39): build_dashboard(), _category_title(), _latest_attempts(), _level_label(), get_quiz(), _quiz_questions(), submit_attempt(), round_half_up() (+31 more)

### Community 1 - "History Store & Mentor API"
Cohesion: 0.09
Nodes (12): post_events(), get_current_user(), get_optional_user(), get_viewer(), require_path_session(), require_path_user(), Viewer, get_db() (+4 more)

### Community 2 - "Test Fixtures"
Cohesion: 0.06
Nodes (23): get_history(), NullEmbedder, get_now(), api(), Clock, clock(), game_client(), make_client() (+15 more)

### Community 3 - "i18n & Navigation"
Cohesion: 0.08
Nodes (31): AppLayout(), NotFound(), Landing(), AccountArea(), initials(), DeskHeader(), LanguageSwitcher(), LOCALE_LABELS (+23 more)

### Community 4 - "Scenario Loading & Validation"
Cohesion: 0.07
Nodes (32): _check_graph(), collect_citation_ids(), collect_text_keys(), _conditions(), _dump(), _dups(), _effect_lists(), iter_text_keys() (+24 more)

### Community 5 - "UI Primitives"
Cohesion: 0.06
Nodes (25): SignInPage(), SignUpPage(), AuthForm(), done(), google(), submit(), validate(), GoogleG() (+17 more)

### Community 6 - "Court Play Screen & NPC Panel"
Cohesion: 0.08
Nodes (32): PlayPage(), Askable, EXAMPLES, Msg, NpcPanel(), NAMES, PlayScreen(), fmt() (+24 more)

### Community 7 - "Quiz & Results UI"
Cohesion: 0.13
Nodes (29): CasePage(), fmt(), PretestPage(), CasesPage(), DashboardPage(), fmt(), Block, label() (+21 more)

### Community 8 - "Frontend Dependencies"
Cohesion: 0.05
Nodes (47): Toaster(), eslintConfig, dependencies, cn@^0.5.2, lucide-react@^1.76.0, next@16.4.6, next-intl@4.15.3, next-themes@^0.4.6 (+39 more)

### Community 9 - "NPC Answering"
Cohesion: 0.08
Nodes (23): allowed_questions(), answer_question(), _choice_model(), classify_lexical(), classify_llm(), NpcResult, _numbers(), rephrase() (+15 more)

### Community 10 - "Mentor Reranking"
Cohesion: 0.11
Nodes (31): build_rerank_user(), CandidateForPrompt, get_reranker(), _llm_factory(), LLMReranker, NullReranker, order_by_scores(), Reranker (+23 more)

### Community 11 - "Ingestion Errors & Seed Dump"
Cohesion: 0.08
Nodes (13): dump_seed(), pg_dump_command(), sequence_fixups(), IngestionError, alembic_config(), create_migrated_database(), ing_db_url(), ing_engine() (+5 more)

### Community 12 - "Legal Source Registry"
Cohesion: 0.09
Nodes (23): Raw file naming <document_key>_<language>_<date>.html (e.g. CPRL_ru_2026-11-20.html; ru, uz-Latn or uz-Cyrl), check_version_file(), load_sources(), _loc(), SourceDocument, _Strict, TermsOfUse, blocks() (+15 more)

### Community 13 - "LLM Settings & Mentor"
Cohesion: 0.09
Nodes (18): classify_question(), get_llm(), LLM, _article_label(), _call_mentor(), _history(), MentorPlan, prepare() (+10 more)

### Community 14 - "Ingestion Pipeline & Checks"
Cohesion: 0.11
Nodes (19): _check_citations(), _check_counts(), _check_db(), CheckResult, _clip(), find_gaps(), Issue, _label() (+11 more)

### Community 15 - "Ingestion Runs"
Cohesion: 0.12
Nodes (29): main(), assert_no_drafts(), chunk_edition(), EditionOutcome, run(), select_documents(), statuses(), test_cli_draft_activate_refused_outside_demo_database() (+21 more)

### Community 16 - "NPC Tests"
Cohesion: 0.09
Nodes (18): NpcAnswer, NpcAskRequest, NpcClassification, NpcReply, NpcFakeLLM, npc_events(), test_event_recorded(), test_llm_bad_or_failed_reply_falls_back() (+10 more)

### Community 17 - "Frontend Spec & Docs"
Cohesion: 0.09
Nodes (33): Monorepo layout (frontend/ Next.js 16 + Phaser 4, backend/ FastAPI + Postgres/pgvector + MongoDB history, deploy/vm1/ systemd + CI/CD, docs/ specs), FastAPI, locale parameter (ru | uz-Latn | uz-Cyrl), Participant 4 (legal content, localization texts, Legal QA), PATCH /api/sessions/{session_id}, ADOLAT Frontend specification (FRONTEND.md), ActionMenu, Court simulator screen /[locale]/play/[sessionId] (+25 more)

### Community 18 - "Legal Search API"
Cohesion: 0.11
Nodes (14): search(), embedder_dep(), Embedder, get_embedder(), detect_language(), Candidate, SearchOutcome, doc_title() (+6 more)

### Community 19 - "Hybrid Search Tests"
Cohesion: 0.10
Nodes (27): prefix_stem(), _tsquery(), FakeEmbedder, client(), dense_client(), factory(), make(), search() (+19 more)

### Community 20 - "Scenario Schema"
Cohesion: 0.09
Nodes (20): Action, _always(), Card, Character, Chose, Claim, DecisionPoint, EvaluationRule (+12 more)

### Community 21 - "Legal Data Pipeline Docs"
Cohesion: 0.11
Nodes (29): Add a new law or edition (save lex.uz HTML -> name and place in raw/ -> update sources.yaml -> run --doc -> human review + activate -> citations.yaml, ingest-check, seed-dump), legal_data/processed/check_report.md (integrity report, prints edition version ids), citations.yaml entry (citation_id, document_key, article_number, part, topic, verified_by; template legal_data/citations.example.yaml), Stable citation id <document_key>.art.<number> (e.g. CPRL.art.14), All current corpus editions are drafts (verified_by empty, check_report.md reports errors), Legal data kept in git (legal_data/raw/ as source of truth, sources.yaml, citations.yaml, processed/check_report.md, article_counts.json), make ingest-check (integrity checks only), make seed-dump (build legal_data/seed.sql.gz: legal-table data with vectors, no schema; needs the db container) (+21 more)

### Community 22 - "Ingestion CLI"
Cohesion: 0.12
Nodes (16): _activate(), build_parser(), add(), _common(), _debug_steps(), _dispatch(), _paths(), _session_factory() (+8 more)

### Community 23 - "Game API Presenter"
Cohesion: 0.10
Nodes (23): ActionParams, ActionRequest, ActionView, CharacterView, ClaimView, CreateSession, CreateUser, DocumentView (+15 more)

### Community 24 - "Auth API"
Cohesion: 0.13
Nodes (16): _base(), _clear_bind(), _fail(), google_callback(), google_start(), login(), logout(), me() (+8 more)

### Community 25 - "Google OAuth Tests"
Cohesion: 0.14
Nodes (22): pkce_challenge(), OAuthState, assert_failed(), callback(), start(), test_bad_id_token_rejected(), test_email_of_other_google_identity_is_refused(), test_expired_state_rejected() (+14 more)

### Community 26 - "Email Auth Tests"
Cohesion: 0.12
Nodes (28): login(), sha(), signup(), _flags(), test_auth_posts_require_origin(), test_cookie_flags_secure_on(), test_cookie_secure_off_for_local(), test_csrf_not_applied_to_get() (+20 more)

### Community 27 - "Settings & Fonts"
Cohesion: 0.11
Nodes (24): FONT_VAR, SettingsPage(), LocaleLayout(), viewport, AuthErrorNotice(), Providers(), SketchSwitcher(), RadioGroup() (+16 more)

### Community 28 - "NPC Events & Activity"
Cohesion: 0.08
Nodes (8): ingest(), ask_npc(), activity_key(), _canon_ts(), make_activity(), safely(), EventsIn, EventsOut

### Community 29 - "User & Event Models"
Cohesion: 0.18
Nodes (16): merge_guest(), _stats_row(), Event, GameSession, QuizAttempt, User, UserStats, test_events_without_session() (+8 more)

### Community 30 - "Community 30"
Cohesion: 0.12
Nodes (14): Edition, _load(), load_edition(), LoadResult, lookup_existing(), _set_if_changed(), _update_existing(), upsert_document() (+6 more)

### Community 31 - "Community 31"
Cohesion: 0.13
Nodes (22): loaded(), mistake_titles(), run(), sc(), test_best_path_is_granted_and_gives_max_score(), test_best_path_is_the_maximum_and_max_score_is_117(), test_committee_complaint_is_optional_and_changes_nothing(), test_constitution_and_new_citations_in_scenario() (+14 more)

### Community 32 - "Community 32"
Cohesion: 0.08
Nodes (31): NEXT_PUBLIC_API_MODE, args, context, environment, healthcheck, image, ports, volumes (+23 more)

### Community 33 - "Community 33"
Cohesion: 0.20
Nodes (17): Base, Article, ArticlePart, Chunk, DocumentVersion, LegalDocument, _article(), _cite() (+9 more)

### Community 34 - "Community 34"
Cohesion: 0.12
Nodes (18): base_normalize(), cyr_to_lat(), lat_to_cyr(), normalize(), tokenize(), matches_document(), content_tokens(), stopwords_for() (+10 more)

### Community 35 - "Community 35"
Cohesion: 0.11
Nodes (28): tx(), action(), apply(), availableActions(), EngineState, evaluate(), IllegalAction, initial() (+20 more)

### Community 36 - "Community 36"
Cohesion: 0.17
Nodes (19): _add_score(), _award_forecasts(), _enter(), _freeze(), _run_effects(), _settle(), _Work, AvailableAction (+11 more)

### Community 37 - "Community 37"
Cohesion: 0.17
Nodes (21): apply(), available_actions(), initial_state(), _is_available(), play(), test_state_is_json_serializable(), test_random_walks_reach_results(), _at_decision() (+13 more)

### Community 38 - "Community 38"
Cohesion: 0.17
Nodes (22): action(), broken(), has(), stage(), test_add_evidence_unknown(), m(), test_citation_not_listed(), test_dead_end_stage() (+14 more)

### Community 39 - "Community 39"
Cohesion: 0.23
Nodes (15): SessionAction, create_user(), get_loaded(), get_result(), _get_session(), get_state(), load_replayed(), _log() (+7 more)

### Community 40 - "Community 40"
Cohesion: 0.08
Nodes (26): ActionView, GameEvent (say, react, stage_changed, evidence_added, score, legal_note, mistake), GameState, ActionKind, ActionView, ArticlePartView, CharacterView, DashboardOut (+18 more)

### Community 41 - "Community 41"
Cohesion: 0.12
Nodes (14): legal_data/processed/*.articles.jsonl (parsed articles, source of article numbers), legal_data/processed/embeddings_cache/ (vector cache), Legal data not in git (processed/*.jsonl, processed/embeddings_cache/, seed.sql.gz via Git LFS), can_embed(), embed_texts(), EmbeddingCache, text_hash(), Calls (+6 more)

### Community 42 - "Community 42"
Cohesion: 0.11
Nodes (16): get_citation_view(), get_citation_views(), _is_valid_on(), _pick(), seeded(), test_all_scenario_citations_resolve(), test_article_view(), test_current_edition_on_date() (+8 more)

### Community 43 - "Community 43"
Cohesion: 0.12
Nodes (18): Courtroom characters and animations (judge, player, plaintiff, defendant rep, witness/expert, secretary), Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses), Phaser court scene (640x360, pixelArt, Scale.FIT), Court(), Props, bubble(), CAST, CourtHandle (+10 more)

### Community 44 - "Community 44"
Cohesion: 0.15
Nodes (16): build_draft(), _d(), _empty(), merge_existing(), merge(), _note(), PageInfo, _q() (+8 more)

### Community 45 - "Community 45"
Cohesion: 0.13
Nodes (16): Accounts and Google SSO proposal (AUTH.md), Input(), API_MODE, mockApi, AccountUser, auth, AuthError, AuthErrorCode (+8 more)

### Community 46 - "Community 46"
Cohesion: 0.12
Nodes (24): actTitle(), LoggedAction, CHARACTERS, citation(), Db, delay(), getSession(), load() (+16 more)

### Community 47 - "Community 47"
Cohesion: 0.13
Nodes (5): upgrade(), upgrade(), _int(), upgrade(), upgrade()

### Community 48 - "Community 48"
Cohesion: 0.13
Nodes (11): backfill(), BackfillResult, mongo_docs(), play_everything(), _snapshot_mongo(), test_activity_has_all_types(), test_backfill_fills_gaps_next_to_live_records(), test_backfill_inmemory() (+3 more)

### Community 49 - "Community 49"
Cohesion: 0.16
Nodes (8): create_user(), get_user(), _get_user(), get_user_sessions(), _outcome_title(), patch_user(), _profile(), UserOut

### Community 50 - "Community 50"
Cohesion: 0.09
Nodes (22): entrypoint.sh script, build, depends_on, env_file, environment, extra_hosts, ports, volumes (+14 more)

### Community 51 - "Community 51"
Cohesion: 0.12
Nodes (21): main(), EMBEDDER (embedding model selection), Add a new case (copy test_consumer -> change scenario_id and texts -> citations in citations.yaml + make demo-laws -> make demo starts cleanly), --draft-activate flag (drafts loaded as active only into demo DB adolat_demo), run command (full pipeline; --doc <key> for one document), backend/tests/fixtures/scenarios/test_consumer/ (case template to copy), texts.ru.json and texts.uz-Latn.json (case texts, both languages required), BGE-M3 (local embedding model) (+13 more)

### Community 52 - "Community 52"
Cohesion: 0.17
Nodes (12): test_same_log_same_state(), test_uz_cyrl_falls_back(), _err(), session(), test_decision_without_valid_option_is_illegal(), test_illegal_action(), test_not_found(), test_outdated_session_after_scenario_change() (+4 more)

### Community 53 - "Community 53"
Cohesion: 0.16
Nodes (12): OllamaLLM, call(), make(), reply(), test_bad_json_and_schema_mismatch(), test_get_llm_selects_provider(), test_http_500(), test_mentor_ask_end_to_end_with_ollama() (+4 more)

### Community 54 - "Community 54"
Cohesion: 0.17
Nodes (6): MongoHistoryStore, run(), mongo_store(), test_live_session_document_grows_and_finishes(), test_push_step_is_idempotent(), test_unreachable_mongo_does_not_break_game()

### Community 55 - "Community 55"
Cohesion: 0.18
Nodes (9): EmbedderError, OllamaEmbedder, test_connection_error_is_embedder_error(), test_embed_batches_and_request_shape(), test_embed_empty_makes_no_request(), test_embed_query_returns_vector(), test_errors_raise_in_embed_and_skip_in_query(), test_wrong_vector_count_is_error() (+1 more)

### Community 56 - "Community 56"
Cohesion: 0.15
Nodes (14): Condition, Effect, React, Say, test_decision_action_requires_decision_id(), test_exactly_one_key(), test_gte_forms(), test_react_short_form_and_bad_reaction() (+6 more)

### Community 57 - "Community 57"
Cohesion: 0.10
Nodes (19): volumes, mongodata, pgdata, Seed stored in Git LFS (.gitattributes; git pull fetches it when git-lfs is installed), ingest docker compose service (tools profile), backend/.venv (Python 3.12 venv with editable backend[dev] and ingestion installs), pnpm via corepack (corepack pnpm ..., pnpm@11.25.0 in package.json), Docker Desktop (runs the Postgres and MongoDB databases) (+11 more)

### Community 58 - "Community 58"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 59 - "Community 59"
Cohesion: 0.16
Nodes (10): find_missing_citations(), load_from_roots(), load_registry(), scenario_roots(), _copy_as(), _no_db(), test_duplicate_scenario_id_across_roots_is_error(), test_load_registry_uses_all_roots() (+2 more)

### Community 60 - "Community 60"
Cohesion: 0.35
Nodes (15): FakeLLM, MentorAnswer, names(), cls(), good_answer(), mentor_events(), test_classification_failure_falls_back_to_concept(), test_event_order_and_llm_settings() (+7 more)

### Community 61 - "Community 61"
Cohesion: 0.15
Nodes (13): _chosen(), evaluate(), Outcome, Mistake, Recommendation, test_best_path_gives_max_score(), test_events_use_keys_not_text(), test_loss_path() (+5 more)

### Community 62 - "Community 62"
Cohesion: 0.22
Nodes (11): hybrid_search(), _ranks(), ArticleRef, dense(), exact(), _run(), scenario_chunks(), Scope (+3 more)

### Community 63 - "Community 63"
Cohesion: 0.17
Nodes (6): ScenarioCard, build_game_state(), build_scenario_card(), present_actions(), present_evidence(), stage_index()

### Community 64 - "Community 64"
Cohesion: 0.12
Nodes (15): ANTHROPIC_API_KEY, anthropic SDK, LLM_MODEL_FAST (claude-haiku-5-5), LLM_MODEL_MENTOR (claude-sonnet-5-5), AI Legal Mentor RAG pipeline, Participant 2 (legal/, rag/, ai/ and ingestion pipeline owner), POST /api/sessions/{session_id}/npc/{character_id}/ask (P2), Query classification (article_lookup | concept | case_specific | out_of_scope) (+7 more)

### Community 65 - "Community 65"
Cohesion: 0.13
Nodes (7): ask(), gen(), format_sse(), get_event_db_factory(), open_db(), _recorder(), record()

### Community 66 - "Community 66"
Cohesion: 0.17
Nodes (6): create_session(), get_result(), get_session(), patch_session(), post_action(), GET /api/sessions/{session_id}

### Community 67 - "Community 67"
Cohesion: 0.16
Nodes (6): loose_email(), normalize_email(), AccountUser, _lenient_uuid(), LoginIn, SignupIn

### Community 68 - "Community 68"
Cohesion: 0.20
Nodes (8): check(), clear_failures(), client_ip(), record_failure(), record_request(), _retry_after(), RateLimitedError, AuthAttempt

### Community 69 - "Community 69"
Cohesion: 0.15
Nodes (17): ACT_TITLES, Dict, QUIZ, RU, UZ, convertPlain(), convertWord(), fit() (+9 more)

### Community 70 - "Community 70"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 71 - "Community 71"
Cohesion: 0.18
Nodes (8): _classes(), _inline_text(), iter_lexuz(), _parse_lexuz(), normalize_number(), _ord_alt(), _ord_alt_ru(), to_roman()

### Community 72 - "Community 72"
Cohesion: 0.22
Nodes (8): clear_cookie(), create_session(), hash_token(), resolve(), revoke_all(), revoke_token(), set_cookie(), AuthSession

### Community 73 - "Community 73"
Cohesion: 0.16
Nodes (6): eval_condition(), HasFacts, IllegalAction, ScenarioError, SessionFinished, JSON condition DSL (all, any, not, flag, gte, always)

### Community 74 - "Community 74"
Cohesion: 0.18
Nodes (11): replay(), LoggedAction, to_log(), test_replay_100_times_identical(), test_replay_empty_log_is_initial(), test_replay_equals_sequential_apply(), Uniform error envelope {error: {code, message, details}}, 409 ILLEGAL_ACTION (+3 more)

### Community 75 - "Community 75"
Cohesion: 0.25
Nodes (10): load_all(), ScenarioValidationError, copy_fixtures(), edit_json(), test_invalid_scenario_json_collected(), test_load_all_fixtures_ok(), test_missing_cyrl_key_is_only_warning(), test_missing_quiz_key_is_error() (+2 more)

### Community 76 - "Community 76"
Cohesion: 0.23
Nodes (16): ADOLAT Backend specification (BACKEND.md), ADOLAT (legal-education court simulator), SQLAlchemy 2 (sync, psycopg 3), How legal data and cases are assembled (DATA.md), ADOLAT Legal Ingestion specification (INGESTION.md), Local models and AI (MODELS.md), gemma3:12b (local language model, ~8 GB), llama3.1:8b (smaller local model for 8 GB machines, weaker Uzbek) (+8 more)

### Community 78 - "Community 78"
Cohesion: 0.14
Nodes (9): normalize_blocks(), blocks(), html(), test_chapter_patterns(), test_normalize_keeps_lex_id(), test_section_patterns(), test_segment_lexuz(), test_segment_lexuz_preamble_and_unknown_heading() (+1 more)

### Community 79 - "Community 79"
Cohesion: 0.18
Nodes (5): _article_keys(), _chunk_keys(), _dedupe(), load_gold(), rank_all()

### Community 80 - "Community 80"
Cohesion: 0.14
Nodes (6): get_google(), rrf_score(), ActivityItem, ActivityOut, HistoryStepOut, SessionHistoryOut

### Community 81 - "Community 81"
Cohesion: 0.23
Nodes (8): _build(), get_article_view(), get_legal_acts(), _title(), ArticlePartView, CitationView, EditionView, LegalActView

### Community 82 - "Community 82"
Cohesion: 0.27
Nodes (12): HistoryItem, MentorAskRequest, MentorBlock, QueryClassification, SearchMatch, SearchResultItem, concept(), mentor_events() (+4 more)

### Community 83 - "Community 83"
Cohesion: 0.14
Nodes (3): session_history(), _usable(), user_activity()

### Community 84 - "Community 84"
Cohesion: 0.22
Nodes (9): AnthropicLLM, call(), FakeAnthropic, reply(), test_adapter_empty_parsed_output_is_unavailable(), test_adapter_errors_mean_unavailable(), test_adapter_passes_sdk_arguments(), test_adapter_refusal_and_truncation_mean_unavailable() (+1 more)

### Community 85 - "Community 85"
Cohesion: 0.17
Nodes (4): load_session_context(), SessionContext, fallback_chain(), translate()

### Community 86 - "Community 86"
Cohesion: 0.19
Nodes (10): allowed_origins(), csrf_guard(), origin_of(), get_settings(), CsrfError, create_app(), _db_opener(), lifespan() (+2 more)

### Community 87 - "Community 87"
Cohesion: 0.20
Nodes (10): missing_citation_ids(), Citation, CitationCheckError, _drop(), _ids(), test_all_scenario_citations_resolve(), test_invalid_scenario_stops_startup(), test_startup_fails_on_missing_citation() (+2 more)

### Community 88 - "Community 88"
Cohesion: 0.21
Nodes (11): Api, post_quiz(), stats(), test_profile_404_and_validation(), test_profile_get_patch(), test_stats_after_three_playthroughs_and_quiz(), test_stats_unfinished_session_counts_only_started(), test_streak_by_utc_days() (+3 more)

### Community 89 - "Community 89"
Cohesion: 0.19
Nodes (16): steps, steps, steps, steps, id, if, name, run (+8 more)

### Community 90 - "Community 90"
Cohesion: 0.19
Nodes (7): to_search(), is_note(), _Draft, _finish(), segment(), _structural(), content_hash()

### Community 91 - "Community 91"
Cohesion: 0.16
Nodes (5): _article_exists(), CitationEntry, link_citations(), LinkError, _to_str()

### Community 92 - "Community 92"
Cohesion: 0.25
Nodes (10): parse_docx(), parse_file(), parse_html(), _blocks(), test_chunks(), test_parse_html_fallback_to_body_when_no_selector(), test_parse_removes_junk_and_keeps_order(), test_segment_chapter_title_on_next_line() (+2 more)

### Community 94 - "Community 94"
Cohesion: 0.17
Nodes (9): get_dashboard(), GET /api/quiz/{scenario_id}?kind=pre|post, GET /api/users/{user_id}/dashboard, Legal literacy level (0-100), Learning gain (post - pre), POST /api/quiz/{scenario_id}/attempts, quiz_attempts table, Dashboard screen /[locale]/dashboard (+1 more)

### Community 95 - "Community 95"
Cohesion: 0.36
Nodes (12): RerankScores, article_numbers(), baseline(), last_first(), make_llm(), mentor_event(), set_settings(), test_llm_reranker_changes_sources_order() (+4 more)

### Community 96 - "Community 96"
Cohesion: 0.24
Nodes (11): as_token(), calls(), do(), test_account_session_may_use_guest_ids(), test_expired_session_loses_access(), test_guests_work_without_login(), test_no_session_gets_401(), test_other_account_gets_403() (+3 more)

### Community 97 - "Community 97"
Cohesion: 0.23
Nodes (7): app(), app_and_client(), app_factory(), client(), make_account(), make(), make_guest()

### Community 98 - "Community 98"
Cohesion: 0.22
Nodes (5): create_email_user(), find_by_email(), GoogleLinkError, upsert_google_user(), GoogleProfile

### Community 99 - "Community 99"
Cohesion: 0.19
Nodes (9): extract_article_numbers(), strip_source_marks(), validate_blocks(), ValidatedBlock, ValidationResult, test_inline_source_marks_are_stripped(), test_detect_language(), test_extract_article_numbers() (+1 more)

### Community 100 - "Community 100"
Cohesion: 0.35
Nodes (11): broken(), has(), q(), test_character_does_not_know_fact(), test_duplicate_question_id(), m(), test_results_stage_not_allowed(), test_text_keys_collected() (+3 more)

### Community 101 - "Community 101"
Cohesion: 0.23
Nodes (5): bootstrap.sh script, vm1 deployment (CI/CD + systemd), /etc/mezon/frontend.build.env, GET /api/health, Landing screen /[locale]

### Community 102 - "Community 102"
Cohesion: 0.29
Nodes (10): CitationView, Edition status (current | historical | unconfirmed), GET /api/legal/citations/{citation_id}, GET /api/sessions/{session_id}/result, Mentor SSE events (sources, block, done, error), POST /api/mentor/ask (text/event-stream), sse-starlette, LegalPanel (shared article panel) (+2 more)

### Community 103 - "Community 103"
Cohesion: 0.19
Nodes (10): POST /api/users, users table, Anonymous user_id in localStorage, AccountUser {id, display_name, email, provider, avatar_url?}, GET /api/auth/me, Ministry of Justice (jury and track), OneID (Uzbekistan government SSO), Uzbekistan Law 'On Personal Data' (ZRU-547) (+2 more)

### Community 104 - "Community 104"
Cohesion: 0.14
Nodes (10): Palette (navy #0F1B2D, gold #C9A227, warm white #F5F1E8, teal #1FA39A, terracotta #C8553D), commissioner, fontVariables, nunito, onest, oswald, plexMono, plexSans (+2 more)

### Community 105 - "Community 105"
Cohesion: 0.30
Nodes (8): article_label(), build_chunks(), _clean(), doc_title_for(), estimate_tokens(), make_header(), _text(), _tokens()

### Community 106 - "Community 106"
Cohesion: 0.18
Nodes (9): get_article(), get_citation(), GET /api/legal/articles/{article_id}, article_parts table, articles table, chunks table (embedding vector + tsv), citations table, document_versions table (+1 more)

### Community 107 - "Community 107"
Cohesion: 0.18
Nodes (7): get_scenario(), list_scenarios(), GET /api/scenarios, GET /api/scenarios/{scenario_id}, Case intro screen /[locale]/cases/[id], Case selection screen /[locale]/cases, Backend gap: GET /api/scenarios/{id}/documents/{doc}

### Community 108 - "Community 108"
Cohesion: 0.24
Nodes (7): _opt(), path(), play(), loaded(), _result(), test_counterfactual_only_when_not_best_and_kind_is_exposed(), test_result_kind_and_label()

### Community 109 - "Community 109"
Cohesion: 0.23
Nodes (12): /etc/mezon/backend.env (backend secrets, chmod 600), mezon-backend.service (127.0.0.1:8000), mezon-db.service (Postgres container), mezon-frontend.service (127.0.0.1:3000), mezon.modeus.cc (production site), mezon-mongo.service (MongoDB history), mezon-mongodata docker volume, mezon-pgdata docker volume (+4 more)

### Community 110 - "Community 110"
Cohesion: 0.17
Nodes (4): get_summary(), GET /api/analytics/scenarios/{scenario_id}/summary (P1), Participant 3 (API, models, game engine, analytics owner), SQL views (v_session_metrics, v_learning_gain, v_mistakes)

### Community 113 - "Community 113"
Cohesion: 0.20
Nodes (10): rrf(), test_rrf_merge(), CI backend job (pytest with Postgres 16 + pgvector service, docker build), Explicit article reference lookup ('st. 15', '15-modda'), GET /api/legal/search, Hybrid legal search (explicit refs + vector top 30 + full-text/trigram top 30), pg_trgm, pgvector (+2 more)

### Community 114 - "Community 114"
Cohesion: 0.30
Nodes (10): _loaded(), _state(), test_decision_options_translated(), test_events_translated_and_typed(), test_evidence_visible_from_second_stage_with_flags(), test_finished_state_has_no_actions(), test_initial_state_stage_and_evidence(), test_mistake_events_hidden_unless_revealed() (+2 more)

### Community 115 - "Community 115"
Cohesion: 0.17
Nodes (10): CI deploy job (rsync to /opt/mezon/src + ssh sudo mezon-deploy), CI frontend job (pnpm i18n check, typecheck, lint, build), VM1_KNOWN_HOSTS (GitHub Actions variable), VM1_SSH_KEY (GitHub Actions secret), concurrency, cancel-in-progress, group, name (+2 more)

### Community 116 - "Community 116"
Cohesion: 0.17
Nodes (12): BE, EVENT, FE, HAS_KEY, INFRA, INPUT_TARGET, NEXT_TELEMETRY_DISABLED, TARGETS (+4 more)

### Community 117 - "Community 117"
Cohesion: 0.20
Nodes (3): _dummy_hash(), hash_password(), verify_password()

### Community 118 - "Community 118"
Cohesion: 0.25
Nodes (3): _ctx(), main(), build_store()

### Community 119 - "Community 119"
Cohesion: 0.25
Nodes (7): error_response(), install_error_handlers(), _app_error(), _db(), _http(), _validation(), _safe_error()

### Community 120 - "Community 120"
Cohesion: 0.35
Nodes (4): build_session_doc(), event_dicts(), session_doc(), step_doc()

### Community 121 - "Community 121"
Cohesion: 0.25
Nodes (7): canonical_number(), DocHint, extract_refs(), _hint_in(), _numbers(), test_extract_refs_with_document_hint(), pairs()

### Community 122 - "Community 122"
Cohesion: 0.49
Nodes (5): on_quiz_attempt(), on_session_finished(), on_session_started(), _row(), _touch()

### Community 123 - "Community 123"
Cohesion: 0.29
Nodes (7): alembic_config(), client(), db_engine(), db_session(), make_alembic_config(), mongo_url(), make test (backend tests; brings up the databases itself)

### Community 124 - "Community 124"
Cohesion: 0.29
Nodes (9): CC - Civil Code of Uzbekistan, consumer_dispute_001 (Faulty smartphone case), CPC - Civil Procedure Code of Uzbekistan, CPRL - Law of Uzbekistan 'On Consumer Rights Protection', Current corpus (CONST, CC1, CC2, CPC, CPRL; ru and uz-Latn pages https://lex.uz/docs/<number>), citation_id (stable article identifier, e.g. CPRL.art.X), Constitution of the Republic of Uzbekistan, Minimal legal corpus for the scenario (+1 more)

### Community 125 - "Community 125"
Cohesion: 0.18
Nodes (11): target, on, pull_request, push, workflow_dispatch, branches, default, description (+3 more)

### Community 126 - "Community 126"
Cohesion: 0.33
Nodes (8): dash(), quiz(), test_dashboard_404(), test_dashboard_after_three_games(), test_dashboard_uz_latn(), test_knowledge_level_labels(), test_new_user_dashboard(), test_recommended_reasons()

### Community 127 - "Community 127"
Cohesion: 0.22
Nodes (3): fake(), FakeGoogle, gapp()

### Community 128 - "Community 128"
Cohesion: 0.24
Nodes (6): test_golden_path_via_api(), test_result_label_is_localized(), test_users_and_scenarios(), events table (analytics), POST /api/sessions, sessions table (game sessions)

### Community 129 - "Community 129"
Cohesion: 0.33
Nodes (5): authlib (Starlette integration), GET /api/auth/google/callback, GET /api/auth/google/start, Google OAuth 2.0 Authorization Code + PKCE (backend-handled), POST /api/auth/logout

### Community 132 - "Community 132"
Cohesion: 0.33
Nodes (8): Mezon: notes for Claude Code (CLAUDE.md), graphify-out/graph.html (interactive graph view), graphify-out/graph.json (graph data used by graphify query), graphify-out/GRAPH_REPORT.md (communities, god nodes, surprising connections, open questions), graphify CLI (graphify query / path / explain), Committed graphify knowledge graph (graphify-out/), /graphify skill (.claude/skills/graphify, installs graphifyy on first use), Shared tooling in .claude/ (vendored skills, see .claude/README.md)

### Community 133 - "Community 133"
Cohesion: 0.22
Nodes (5): Uzbek Latin 2026 alphabet (law of 21.10.2026), base, dir, keys(), latn

### Community 134 - "Community 134"
Cohesion: 0.22
Nodes (9): defaults, run, defaults, if, name, needs, runs-on, frontend (+1 more)

### Community 135 - "Community 135"
Cohesion: 0.22
Nodes (9): services, POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, env, image, options, ports (+1 more)

### Community 137 - "Community 137"
Cohesion: 0.39
Nodes (5): PatchUser, UserProfileOut, UserSessionItem, UserSessionsOut, UserStatsOut

### Community 139 - "Community 139"
Cohesion: 0.39
Nodes (4): first(), test_no_key_message_follows_question_language(), test_no_key_returns_sources_and_ai_unavailable(), test_no_key_still_applies_threshold()

### Community 140 - "Community 140"
Cohesion: 0.29
Nodes (5): call(), liveApi, sse(), ApiError, MentorEvent

### Community 141 - "Community 141"
Cohesion: 0.25
Nodes (8): environment, if, name, needs, runs-on, name, url, deploy

### Community 145 - "Community 145"
Cohesion: 0.43
Nodes (3): email_hash(), log(), main()

### Community 146 - "Community 146"
Cohesion: 0.29
Nodes (5): DecisionView, MistakeView, RecommendationView, SessionResult, build_result()

### Community 147 - "Community 147"
Cohesion: 0.29
Nodes (6): allowBuilds, @parcel/watcher, sharp, @swc/core, unrs-resolver, minimumReleaseAgeExclude

### Community 148 - "Community 148"
Cohesion: 0.29
Nodes (7): outputs, runs-on, jobs, changes, backend, frontend, infra

### Community 149 - "Community 149"
Cohesion: 0.40
Nodes (3): fallback_language_note(), language_name(), unconfirmed_note()

### Community 150 - "Community 150"
Cohesion: 0.47
Nodes (3): get_url(), run_migrations_offline(), run_migrations_online()

### Community 153 - "Community 153"
Cohesion: 0.40
Nodes (5): if, name, needs, runs-on, backend

### Community 155 - "Community 155"
Cohesion: 0.67
Nodes (3): npx, next-devtools, shadcn

## Ambiguous Edges - Review These
- `courtroom.ts` → `Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `Uzbek Cyrillic -> Latin transliteration table (search only)` → `Uzbek Latin 2026 alphabet (law of 21.10.2026)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `In-browser mock backend (localStorage)` → `Thin client: no game logic or scenario texts in the frontend`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `sessions table (game sessions)` → `Opaque revocable server sessions (30-day sliding expiry)`  [AMBIGUOUS]
  frontend/AUTH.md · relation: conceptually_related_to
- `Generated API client (openapi-typescript + openapi-fetch, make api-client)` → `types.ts`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to

## Knowledge Gaps
- **18 isolated node(s):** `multilingual-e5-large (local, passage:/query: prefixes)`, `Palette (navy #0F1B2D, gold #C9A227, warm white #F5F1E8, teal #1FA39A, terracotta #C8553D)`, `Participant 1 (frontend owner)`, `anthropic SDK`, `RAG_MIN_SCORE (relevance threshold)` (+13 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1006 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `LLM Settings & Mentor` to `History Store & Mentor API`, `Test Fixtures`, `Scenario Loading & Validation`, `NPC Answering`, `Mentor Reranking`, `Community 139`, `Ingestion Runs`, `Community 144`, `NPC Tests`, `Legal Search API`, `Ingestion CLI`, `Auth API`, `Google OAuth Tests`, `NPC Events & Activity`, `Community 41`, `Community 51`, `Community 53`, `Community 55`, `Community 59`, `Community 60`, `Community 61`, `Community 62`, `Community 64`, `Community 65`, `Community 68`, `Community 72`, `Community 76`, `Community 79`, `Community 80`, `Community 86`, `Community 93`, `Community 95`, `Community 97`, `Community 118`, `Community 123`, `Community 127`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Are the 61 inferred relationships involving `Settings` (e.g. with `classify_question()` and `get_llm()`) actually correct?**
  _`Settings` has 61 INFERRED edges - model-reasoned connections that need verification._
- **What connects `multilingual-e5-large (local, passage:/query: prefixes)`, `Palette (navy #0F1B2D, gold #C9A227, warm white #F5F1E8, teal #1FA39A, terracotta #C8553D)`, `Participant 1 (frontend owner)` to the rest of the system?**
  _18 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Errors & Analytics` be split into smaller, more focused modules?**
  _Cohesion score 0.05980861244019139 - nodes in this community are weakly interconnected._
- **Why does `Mezon frontend README` connect `Frontend Spec & Docs` to `Community 69`, `Community 133`, `Community 40`, `Community 104`, `Community 43`, `Community 140`, `Community 45`, `Community 109`, `Community 107`, `Community 76`, `Community 57`, `Community 124`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `courtroom.ts` and `Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Uzbek Cyrillic -> Latin transliteration table (search only)` and `Uzbek Latin 2026 alphabet (law of 21.10.2026)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._