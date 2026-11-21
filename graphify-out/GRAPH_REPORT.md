# Graph Report - mezon  (2026-11-21)

## Corpus Check
- 364 files · ~149,309 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 26 file(s) not represented in the graph (top: (none) 11, .service 5, .example 4)

## Summary
- 3860 nodes · 11147 edges · 174 communities (132 shown, 42 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 1347 edges (avg confidence: 0.91)
- Token cost: 1,090,603 input · 0 output

## Graph Freshness
- Built from commit: `730ee96a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_mentor_flow.py
- situation-screen.tsx
- scenario.py
- store.py
- test_registry_paths.py
- api/mentor.py
- next-intl
- analytics/quiz.py
- evaluate
- react
- re
- ai/mentor.py
- package.json
- search.py
- search
- game/conftest.py
- vm1 deployment (CI/CD + systemd)
- test_consumer_moisture.py
- test_rent_deposit.py
- play-screen.tsx
- backfill.py
- app/errors.py
- test_wedding_photo.py
- game_engine/__init__.py
- test_npc_flow.py
- run
- test_google.py
- Scenario
- featured-case.tsx
- json
- Auth security basics (state/PKCE check, next-path validation, CSRF, rate limiting)
- Legal ingestion pipeline (10 steps)
- sqlalchemy
- storage
- _loc
- test_email_auth.py
- api.py
- play-screen.tsx
- accounts.py
- game.py
- lib/settings.ts
- test_search.py
- sqlalchemy
- health
- .start
- CI deploy job (main only: rsync to /opt/mezon/src + ssh sudo mezon-deploy --sha <sha> <backend|frontend|all>)
- providers.tsx
- builder.py
- engine/test_validate.py
- text.py
- api/users.py
- load_sources
- get_dashboard
- MongoHistoryStore
- service.py
- DocumentVersion
- db
- types.ts
- test_lexuz.py
- engine.ts
- make demo-laws (load real laws from legal_data/ into adolat_demo as drafts)
- api/auth.py
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
- test_citations_resolve.py
- ratelimit.py
- Cases in scenarios/ (one folder per case with scenario.json, quiz.json, texts.ru.json, texts.uz-Latn.json; not stored in git)
- ask_npc
- compilerOptions
- test_embed_db.py
- segment
- AI Legal Mentor RAG pipeline
- test_build_and_catalog.py
- Api
- ingestion/tests/conftest.py
- post_attempt
- Api
- test_lexuz.py
- Mezon frontend README
- cases/page.tsx
- analytics/dashboard.py
- LoadedScenario
- pytest
- test_access.py
- POST /api/sessions
- live.ts
- backend/tests/conftest.py
- api/history.py
- storage
- test_parse_segment.py
- auth/sessions.py
- ADOLAT Backend specification (BACKEND.md)
- test_history_store.py
- synth.py
- chunk.py
- load_all
- summary.py
- load_scenario_dir
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
- Settings
- scripts
- test_dashboard.py
- steps
- _OneOf
- Works without models (mentor shows found articles, NPCs use canned replies, full-text search)
- changes
- ci-cd.yml
- allowBuilds
- deploy
- legal_data/seed.sql.gz (demo seed)
- vm1 (vm1.modeus.cc)
- events.py
- .mcp.json
- select.tsx
- NullHistoryStore
- tts/conftest.py
- Озвучка реплик (TTS)
- get_glossary
- env.py
- SettableClock
- _make
- test_locales.py
- RunResult

## God Nodes (most connected - your core abstractions)
1. `Settings` - 137 edges
2. `apply()` - 57 edges
3. `LoadedScenario` - 53 edges
4. `run()` - 52 edges
5. `HistoryStore` - 51 edges
6. `initial_state()` - 50 edges
7. `User` - 47 edges
8. `IngestionError` - 43 edges
9. `Button()` - 42 edges
10. `DocumentVersion` - 41 edges

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
- **LLM access path: backend (OLLAMA_URL=http://host.docker.internal:11435) -> mezon-llm-tunnel.service -> Ollama on the vast.ai GPU server** — deploy_vm1_readme_mezon_backend_service, deploy_vm1_readme_backend_llm_settings, deploy_vm1_readme_mezon_llm_tunnel_service, deploy_vm1_readme_llm_tunnel_key, deploy_vm1_readme_llm_tunnel_env, deploy_vm1_readme_gpu_ollama_server [EXTRACTED 1.00]
- **AI mentor answer flow: detect language -> normalize -> classify -> hybrid search -> threshold refusal -> source-tagged context -> structured blocks -> validation -> SSE** — docs_backend_query_language_detection, docs_backend_query_normalization, docs_backend_query_classification, docs_backend_hybrid_search, docs_backend_insufficient_sources_refusal, docs_backend_source_tags_as_data, docs_backend_structured_answer_blocks, docs_backend_answer_block_validation, docs_backend_mentor_sse_events [EXTRACTED 1.00]
- **Edition verification flow: run (pending_review) -> human review of check_report.md -> fill verified_by in sources.yaml -> activate -> seed-dump** — docs_data_run_command, docs_data_check_report, docs_data_human_review_fields, docs_ingestion_activate_command, docs_data_make_seed_dump [EXTRACTED 1.00]
- **User journey: Landing -> Cases -> Case intro -> Pretest -> Play -> Results -> Posttest / Mentor -> Dashboard** — docs_frontend_landing_screen, docs_frontend_cases_screen, docs_frontend_case_intro_screen, docs_frontend_quiz_screens, docs_frontend_court_simulator_screen, docs_frontend_results_screen, docs_frontend_mentor_screen, docs_frontend_dashboard_screen [EXTRACTED 1.00]
- **Legal ingestion pipeline: validate -> parse -> normalize -> segment -> version -> chunk -> embed -> load -> link -> check** — docs_ingestion_validate_step, docs_ingestion_parse_step, docs_ingestion_normalize_step, docs_ingestion_segment_step, docs_ingestion_version_step, docs_ingestion_chunk_step, docs_ingestion_embed_step, docs_ingestion_load_step, docs_ingestion_link_step, docs_ingestion_check_step [EXTRACTED 1.00]
- **First local run: backend/.venv -> .env from .env.example -> Docker Desktop -> make demo-laws -> make dev-all** — docs_setup_backend_venv, docs_setup_env_file, docs_setup_docker_desktop, docs_setup_make_demo_laws, docs_setup_make_dev_all [EXTRACTED 1.00]
- **Case materials document flow: CaseFile panel -> api.document -> GET /api/sessions/{session_id}/evidence/{evidence_id} -> get_evidence_document -> build_evidence_document -> EvidenceDocument lines** — docs_frontend_case_file, frontend_components_play_case_file_casefile, frontend_lib_api_types_api_document, docs_backend_get_api_sessions_session_id_evidence_evidence_id, backend_app_api_sessions_get_evidence_document, backend_app_services_presenter_build_evidence_document, docs_backend_evidence_document [INFERRED 0.85]
- **Two case categories for everyone: card kind court | situation -> CaseKind -> /cases#track-situation and #track-court sections, linked from 'What's inside Mezon'** — docs_frontend_whats_inside_mezon, docs_frontend_case_tracks, scenarios_readme_life_situations, frontend_components_site_pitch_pitch, frontend_app_locale_app_cases_page_casespage, frontend_lib_api_types_casekind, backend_app_schemas_scenario_card [INFERRED 0.85]
- **Life situation flow: 'Life situations' category -> SituationScreen on the play route -> claim letter to the seller** — scenarios_readme_life_situations, docs_frontend_case_tracks, docs_frontend_situation_screen, docs_frontend_claim_letter, frontend_components_play_situation_screen_situationscreen, frontend_components_common_claim_letter_claimletter [INFERRED 0.85]

## Communities (174 total, 42 thin omitted)

### Community 0 - "test_mentor_flow.py"
Cohesion: 0.05
Nodes (81): AnthropicLLM, FakeLLM, get_llm(), OllamaLLM, RerankScore, RerankScores, strip_source_marks(), MentorAnswer (+73 more)

### Community 1 - "situation-screen.tsx"
Cohesion: 0.12
Nodes (35): CasePage(), fmt(), DashboardPage(), fmt(), DKINDS, KINDS, ResultsPage(), short() (+27 more)

### Community 2 - "scenario.py"
Cohesion: 0.10
Nodes (21): Card, Character, Chose, Claim, DecisionPoint, EvaluationRule, Evidence, Fact (+13 more)

### Community 3 - "store.py"
Cohesion: 0.15
Nodes (5): open_db(), record(), activity_key(), _canon_ts(), make_activity()

### Community 4 - "test_registry_paths.py"
Cohesion: 0.13
Nodes (12): find_missing_citations(), load_from_roots(), load_registry(), scenario_roots(), _copy_as(), _no_db(), test_duplicate_scenario_id_across_roots_is_error(), test_load_registry_uses_all_roots() (+4 more)

### Community 5 - "api/mentor.py"
Cohesion: 0.08
Nodes (20): GlossaryTerm, get_viewer(), require_path_session(), require_path_user(), Viewer, get_settings(), get_db(), ForbiddenError (+12 more)

### Community 6 - "next-intl"
Cohesion: 0.11
Nodes (27): AppLayout(), NotFound(), AccountArea(), initials(), DeskHeader(), LanguageSwitcher(), LOCALE_LABELS, SiteFooter() (+19 more)

### Community 7 - "analytics/quiz.py"
Cohesion: 0.17
Nodes (17): get_quiz(), _quiz_questions(), submit_attempt(), ClientEvent, DashboardLearningGain, DashboardOut, DashboardUser, KnowledgeLevel (+9 more)

### Community 8 - "evaluate"
Cohesion: 0.12
Nodes (18): replay(), LoggedAction, play(), scenario(), to_log(), test_replay_100_times_identical(), test_replay_empty_log_is_initial(), test_replay_equals_sequential_apply() (+10 more)

### Community 9 - "react"
Cohesion: 0.06
Nodes (31): SignInPage(), SignUpPage(), Auth form error messages (429 rate limit, 422 validation, network errors), AuthForm(), done(), google(), submit(), validate() (+23 more)

### Community 10 - "re"
Cohesion: 0.12
Nodes (17): unknown_names(), audio_for(), AudioRef, line_path(), _first_word(), infer_speaker(), lang_of(), line_hash() (+9 more)

### Community 11 - "ai/mentor.py"
Cohesion: 0.04
Nodes (47): classify_question(), load_session_context(), SessionContext, LLM, _article_label(), _call_mentor(), _history(), MentorPlan (+39 more)

### Community 12 - "package.json"
Cohesion: 0.07
Nodes (37): eslintConfig, dependencies, cn@^0.5.2, lucide-react@^1.76.0, next@16.4.6, next-intl@4.15.3, next-themes@^0.4.6, radix-ui@^1.8.1 (+29 more)

### Community 13 - "search.py"
Cohesion: 0.05
Nodes (47): _tokens(), rrf(), rrf_score(), base_normalize(), cyr_to_lat(), lat_to_cyr(), normalize(), tokenize() (+39 more)

### Community 14 - "search"
Cohesion: 0.24
Nodes (11): DATABASE_URL (Postgres), GET /api/legal/articles/{article_id}, GET /api/legal/search, Hybrid legal search (explicit refs + vector top 30 + full-text/trigram top 30), pg_trgm, pgvector, PostgreSQL 16, Reciprocal Rank Fusion (RRF) (+3 more)

### Community 15 - "game/conftest.py"
Cohesion: 0.14
Nodes (10): api(), Clock, clock(), game_client(), make_client(), _make(), seeded_db(), no_network() (+2 more)

### Community 16 - "vm1 deployment (CI/CD + systemd)"
Cohesion: 0.22
Nodes (8): bootstrap.sh script, vm1 deployment (CI/CD + systemd), /etc/mezon/frontend.build.env (NEXT_PUBLIC_API_MODE=mock|live, NEXT_PUBLIC_GOOGLE_AUTH; missing keys are appended), Frontend -> real backend (NEXT_PUBLIC_API_MODE=live in frontend.build.env, baked in at build time), API_MODE, mockApi, In-browser mock backend (localStorage), NEXT_PUBLIC_API_MODE (mock | live)

### Community 17 - "test_consumer_moisture.py"
Cohesion: 0.10
Nodes (28): loaded(), mistake_titles(), _opt(), path(), play(), loaded(), _result(), test_counterfactual_only_when_not_best_and_kind_is_exposed() (+20 more)

### Community 18 - "test_rent_deposit.py"
Cohesion: 0.10
Nodes (29): _ids(), loaded(), mistake_titles(), _opt(), path(), play(), run(), sc() (+21 more)

### Community 19 - "play-screen.tsx"
Cohesion: 0.12
Nodes (18): Askable, DecisionDialog(), NAMES, ThemeMenu(), Dialog(), DialogContent(), DialogDescription(), DialogFooter() (+10 more)

### Community 20 - "backfill.py"
Cohesion: 0.16
Nodes (7): backfill(), BackfillResult, _ctx(), main(), build_parser(), add(), _common()

### Community 21 - "app/errors.py"
Cohesion: 0.08
Nodes (24): AppError, DbUnavailableError, EmailExistsError, error_response(), IllegalActionError, install_error_handlers(), _app_error(), _db() (+16 more)

### Community 22 - "test_wedding_photo.py"
Cohesion: 0.10
Nodes (29): _ids(), loaded(), mistake_titles(), _opt(), path(), play(), _reach_motions(), run() (+21 more)

### Community 23 - "game_engine/__init__.py"
Cohesion: 0.09
Nodes (31): eval_condition(), HasFacts, _add_score(), _award_forecasts(), _enter(), _freeze(), _is_available(), _run_effects() (+23 more)

### Community 24 - "test_npc_flow.py"
Cohesion: 0.09
Nodes (17): NpcClassification, NpcReply, NpcFakeLLM, npc_events(), test_event_recorded(), test_llm_bad_or_failed_reply_falls_back(), test_llm_classifier_exception_uses_lexical(), test_llm_classifier_failure_uses_lexical() (+9 more)

### Community 25 - "run"
Cohesion: 0.15
Nodes (26): main(), EditionOutcome, run(), statuses(), test_cli_draft_activate_refused_outside_demo_database(), test_draft_activate_in_demo_database_is_idempotent_and_check_still_fails(), test_draft_activate_promotes_already_loaded_pending(), test_draft_activate_refused_outside_demo_database() (+18 more)

### Community 26 - "test_google.py"
Cohesion: 0.09
Nodes (27): get_google(), GoogleProfile, pkce_challenge(), OAuthState, assert_failed(), callback(), fake(), gapp() (+19 more)

### Community 27 - "Scenario"
Cohesion: 0.15
Nodes (17): _check_graph(), collect_citation_ids(), collect_text_keys(), _conditions(), _dump(), _dups(), _effect_lists(), iter_text_keys() (+9 more)

### Community 28 - "featured-case.tsx"
Cohesion: 0.11
Nodes (24): Case selection screen /[locale]/cases, Guest home page Pitch (components/site/pitch.tsx, case-folder design), HomeGate (signed-in user's case desk on the home page), Landing screen /[locale], Smooth page transitions (route template.tsx + .page-in CSS), Template(), Template(), Landing() (+16 more)

### Community 29 - "json"
Cohesion: 0.12
Nodes (15): _read_json(), BuildReport, _load_manifest(), cmd_build(), cmd_init_bucket(), cmd_upload(), cmd_voices(), main() (+7 more)

### Community 30 - "Auth security basics (state/PKCE check, next-path validation, CSRF, rate limiting)"
Cohesion: 0.09
Nodes (31): allowed_origins(), csrf_guard(), origin_of(), CsrfError, AUTH_IP_MAX_REQUESTS=120 per 15 min (code default 30), /etc/mezon/backend.env (backend secrets, chmod 600), Backend-owned sign-in (/api/auth/*, cookie mezon_session), COOKIE_SECURE=true (session cookie only over https) (+23 more)

### Community 31 - "Legal ingestion pipeline (10 steps)"
Cohesion: 0.08
Nodes (38): EMBEDDER (embedding model selection), Add a new law or edition (save lex.uz HTML -> name and place in raw/ -> update sources.yaml -> run --doc -> human review + activate -> citations.yaml, ingest-check, seed-dump), legal_data/processed/check_report.md (integrity report, prints edition version ids), citations.yaml entry (citation_id, document_key, article_number, part, topic, verified_by; template legal_data/citations.example.yaml), Stable citation id <document_key>.art.<number> (e.g. CPRL.art.14), All current corpus editions are drafts (verified_by empty, check_report.md reports errors), Debug step commands without DB (parse / segment / chunk --doc), Legal data kept in git (legal_data/raw/ as source of truth, sources.yaml, citations.yaml, processed/check_report.md, article_counts.json) (+30 more)

### Community 32 - "sqlalchemy"
Cohesion: 0.04
Nodes (51): _check_citations(), _check_counts(), _check_db(), CheckResult, _clip(), find_gaps(), Issue, _label() (+43 more)

### Community 33 - "storage"
Cohesion: 0.07
Nodes (26): RUSTFS_ADDRESS, RUSTFS_CONSOLE_ADDRESS, RUSTFS_CONSOLE_ENABLE, interval, retries, test, timeout, external (+18 more)

### Community 35 - "test_email_auth.py"
Cohesion: 0.08
Nodes (35): app(), app_and_client(), app_factory(), client(), login(), make_account(), make(), make_guest() (+27 more)

### Community 36 - "api.py"
Cohesion: 0.06
Nodes (38): create_user(), ActionParams, ActionRequest, ActionView, AudioLineView, CharacterView, ClaimView, CreateSession (+30 more)

### Community 37 - "play-screen.tsx"
Cohesion: 0.14
Nodes (19): Block, label(), MentorPage(), Msg, EXAMPLES, Msg, NpcPanel(), fmt() (+11 more)

### Community 38 - "accounts.py"
Cohesion: 0.23
Nodes (4): create_email_user(), find_by_email(), GoogleLinkError, upsert_google_user()

### Community 39 - "game.py"
Cohesion: 0.21
Nodes (16): NotFoundError, safely(), create_user(), get_evidence_document(), get_loaded(), get_result(), _get_session(), get_state() (+8 more)

### Community 40 - "lib/settings.ts"
Cohesion: 0.12
Nodes (30): FONT_VAR, SettingsPage(), ThemePicker(), ThemeStack(), RadioGroup(), RadioGroupItem(), Slider(), Court() (+22 more)

### Community 41 - "test_search.py"
Cohesion: 0.07
Nodes (37): _same_word(), ArticleRef, dense(), exact(), prefix_stem(), _run(), scenario_chunks(), Scope (+29 more)

### Community 43 - "sqlalchemy"
Cohesion: 0.06
Nodes (10): upgrade(), upgrade(), _int(), upgrade(), upgrade(), upgrade(), downgrade(), GET /api/analytics/scenarios/{scenario_id}/summary (P1) (+2 more)

### Community 44 - "health"
Cohesion: 0.22
Nodes (4): health(), HealthResponse, audio_lines(), scenarios()

### Community 45 - ".start"
Cohesion: 0.17
Nodes (10): test_golden_path_via_api(), test_result_label_is_localized(), test_same_log_same_state(), test_document_locale_and_unknown(), test_documents_follow_the_case_file(), test_result_and_events_with_new_fields(), test_everything_translated(), test_uz_cyrl_falls_back() (+2 more)

### Community 46 - "CI deploy job (main only: rsync to /opt/mezon/src + ssh sudo mezon-deploy --sha <sha> <backend|frontend|all>)"
Cohesion: 0.17
Nodes (13): CI deploy job (main only: rsync to /opt/mezon/src + ssh sudo mezon-deploy --sha <sha> <backend|frontend|all>), VM1_KNOWN_HOSTS (GitHub Actions variable), VM1_SSH_KEY (GitHub Actions secret), BE, EVENT, FE, HAS_KEY, INFRA (+5 more)

### Community 47 - "providers.tsx"
Cohesion: 0.11
Nodes (18): commissioner, fontVariables, nunito, onest, oswald, plexMono, plexSans, serif (+10 more)

### Community 48 - "builder.py"
Cohesion: 0.23
Nodes (7): SessionOutdatedError, build_session_doc(), event_dicts(), session_doc(), step_doc(), SessionAction, _replay_log()

### Community 49 - "engine/test_validate.py"
Cohesion: 0.17
Nodes (22): action(), broken(), has(), stage(), test_add_evidence_unknown(), m(), test_citation_not_listed(), test_dead_end_stage() (+14 more)

### Community 50 - "text.py"
Cohesion: 0.17
Nodes (17): _int(), latn_to_cyrl(), numbers_to_words(), prepare(), _ru_below_1000(), ru_day_genitive(), _ru_form(), ru_number() (+9 more)

### Community 51 - "api/users.py"
Cohesion: 0.23
Nodes (7): get_user(), _get_user(), get_user_sessions(), _outcome_title(), patch_user(), _profile(), UserProfileOut

### Community 52 - "load_sources"
Cohesion: 0.13
Nodes (19): Raw file naming <document_key>_<language>_<date>.html (e.g. CPRL_ru_2026-11-20.html; ru, uz-Latn or uz-Cyrl), check_version_file(), load_sources(), blocks(), document_entry(), html_doc(), version_entry(), write_docx() (+11 more)

### Community 53 - "get_dashboard"
Cohesion: 0.17
Nodes (9): get_dashboard(), GET /api/quiz/{scenario_id}?kind=pre|post, GET /api/users/{user_id}/dashboard, Legal literacy level (0-100), Learning gain (post - pre), POST /api/quiz/{scenario_id}/attempts, quiz_attempts table, Dashboard screen /[locale]/dashboard (+1 more)

### Community 54 - "MongoHistoryStore"
Cohesion: 0.18
Nodes (5): MongoHistoryStore, run(), mongo_store(), test_push_step_is_idempotent(), test_unreachable_mongo_does_not_break_game()

### Community 55 - "service.py"
Cohesion: 0.05
Nodes (39): get_article(), get_citation(), search(), fallback_language_note(), language_name(), unconfirmed_note(), _build(), get_article_view() (+31 more)

### Community 56 - "DocumentVersion"
Cohesion: 0.09
Nodes (32): Article, ArticlePart, Chunk, DocumentVersion, LegalDocument, main(), _article(), _cite() (+24 more)

### Community 57 - "db"
Cohesion: 0.09
Nodes (24): NEXT_PUBLIC_API_MODE, args, context, environment, image, ports, volumes, POSTGRES_DB (+16 more)

### Community 58 - "types.ts"
Cohesion: 0.09
Nodes (22): ActionView, ActionKind, ActionView, ArticlePartView, CharacterView, DashboardOut, Difficulty, EditionStatus (+14 more)

### Community 59 - "test_lexuz.py"
Cohesion: 0.15
Nodes (17): sources-draft command (draft sources.yaml from downloaded pages, no DB or network; --force keeps filled fields), build_draft(), _d(), _empty(), merge_existing(), merge(), _note(), PageInfo (+9 more)

### Community 60 - "engine.ts"
Cohesion: 0.12
Nodes (27): tx(), action(), apply(), availableActions(), EngineState, evaluate(), IllegalAction, initial() (+19 more)

### Community 61 - "make demo-laws (load real laws from legal_data/ into adolat_demo as drafts)"
Cohesion: 0.29
Nodes (7): --draft-activate flag (drafts loaded as active only into demo DB adolat_demo), Embedding model role (articles and questions -> vectors for semantic search), adolat_demo demo database (draft loading allowed only for DB names ending in _demo), make demo (backend only, with demo data), make demo-laws (load real laws from legal_data/ into adolat_demo as drafts), make demo-reset (drop the demo DB to recreate it), assert_demo_database()

### Community 62 - "api/auth.py"
Cohesion: 0.05
Nodes (35): _base(), _clear_bind(), _fail(), google_callback(), google_start(), login(), logout(), me() (+27 more)

### Community 63 - "Claude Haiku 5.5 via Anthropic API key (claude-haiku-5-5 for LLM_MODEL_MENTOR and LLM_MODEL_FAST)"
Cohesion: 0.13
Nodes (22): Backend LLM settings (LLM_PROVIDER=ollama, OLLAMA_URL=http://host.docker.internal:11435, OLLAMA_MODEL=gemma3:27b, EMBEDDER=ollama-bge-m3), gemma3:27b (production language model served by Ollama on the GPU server), GPU server: Ollama (gemma3:27b + bge-m3) on a vast.ai RTX 3090, listening only on 127.0.0.1:11434, /etc/mezon/llm-tunnel.env (GPU_HOST, GPU_PORT, GPU_USER, TUNNEL_BIND, TUNNEL_PORT; template env/llm-tunnel.env.example), /etc/mezon/llm-tunnel.key (tunnel-only key; restricted on the GPU server to port-forwarding 127.0.0.1:11434, no shell), /etc/mezon/llm-tunnel.known_hosts (pinned ED25519 host key of the GPU server), mezon-llm-tunnel.service (SSH tunnel to the GPU server's Ollama, exposed on vm1 docker0 172.17.0.1:11435), Re-pointing the tunnel after vast.ai recreates the instance (update llm-tunnel.env, rescan and verify host key, authorize llm-tunnel.key.pub, restart mezon-llm-tunnel) (+14 more)

### Community 64 - "mock/index.ts"
Cohesion: 0.12
Nodes (24): actTitle(), LoggedAction, CHARACTERS, citation(), Db, delay(), getSession(), levelLabel() (+16 more)

### Community 65 - "courtroom.ts"
Cohesion: 0.14
Nodes (27): Courtroom characters and animations (judge, player, plaintiff, defendant rep, witness/expert, secretary), ALIASES, archShape(), bubble(), CAST, COURT_THEMES, CourtHandle, CourtThemeId (+19 more)

### Community 66 - "schemas/quiz.py"
Cohesion: 0.24
Nodes (5): export_schemas(), _Model, Question, Quiz, QuizOption

### Community 67 - "OllamaEmbedder"
Cohesion: 0.18
Nodes (9): EmbedderError, OllamaEmbedder, test_connection_error_is_embedder_error(), test_embed_batches_and_request_shape(), test_embed_empty_makes_no_request(), test_embed_query_returns_vector(), test_errors_raise_in_embed_and_skip_in_query(), test_wrong_vector_count_is_error() (+1 more)

### Community 68 - "apply"
Cohesion: 0.10
Nodes (34): apply(), available_actions(), initial_state(), test_random_walks_reach_results(), _at_decision(), test_after_finish_session_finished(), test_apply_does_not_mutate_old_state(), test_decision_needs_valid_option() (+26 more)

### Community 69 - "re"
Cohesion: 0.17
Nodes (9): _classes(), _Collector, _inline_text(), iter_lexuz(), parse_docx(), parse_file(), _parse_lexuz(), _style() (+1 more)

### Community 70 - "create_session"
Cohesion: 0.18
Nodes (6): create_session(), get_evidence_document(), get_result(), get_session(), patch_session(), post_action()

### Community 71 - "load_seed.py"
Cohesion: 0.10
Nodes (21): entrypoint.sh script, build, depends_on, environment, extra_hosts, ports, volumes, condition (+13 more)

### Community 73 - "uuid"
Cohesion: 0.14
Nodes (21): merge_guest(), _stats_row(), Event, GameSession, QuizAttempt, User, UserStats, Base (+13 more)

### Community 74 - "components.json"
Cohesion: 0.09
Nodes (21): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+13 more)

### Community 75 - "translit.ts"
Cohesion: 0.13
Nodes (16): convertPlain(), convertWord(), fit(), IOTATED, isUpper(), LETTERS, NEW_LETTERS, toNewLatin() (+8 more)

### Community 76 - "test_citations_resolve.py"
Cohesion: 0.26
Nodes (7): CitationCheckError, _drop(), _ids(), test_all_scenario_citations_resolve(), test_invalid_scenario_stops_startup(), test_startup_fails_on_missing_citation(), test_startup_ok_when_not_strict()

### Community 77 - "ratelimit.py"
Cohesion: 0.19
Nodes (10): check(), clear_failures(), email_hash(), record_failure(), record_request(), _retry_after(), RateLimitedError, AuthAttempt (+2 more)

### Community 78 - "Cases in scenarios/ (one folder per case with scenario.json, quiz.json, texts.ru.json, texts.uz-Latn.json; not stored in git)"
Cohesion: 0.23
Nodes (10): Add a new case (copy test_consumer -> change scenario_id and texts -> citations in citations.yaml + make demo-laws -> make demo starts cleanly), scenarios/consumer_moisture_001/ (example case folder), quiz.json (case questions), scenario.json (case flow, roles, citations list), backend/app/schemas/scenario.schema.json and quiz.schema.json (case JSON schemas), Cases in scenarios/ (one folder per case with scenario.json, quiz.json, texts.ru.json, texts.uz-Latn.json; not stored in git), backend/tests/fixtures/scenarios/test_consumer/ (case template to copy), texts.ru.json and texts.uz-Latn.json (case texts, both languages required) (+2 more)

### Community 80 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 81 - "test_embed_db.py"
Cohesion: 0.14
Nodes (11): can_embed(), embed_texts(), EmbeddingCache, text_hash(), Calls, test_backend_search_skips_dense_branch_when_ollama_fails(), test_embed_texts_batches_and_cache(), test_embed_texts_without_embedder() (+3 more)

### Community 82 - "segment"
Cohesion: 0.17
Nodes (8): to_search(), _Draft, _finish(), segment(), _structural(), content_hash(), test_segment_chapter_title_on_next_line(), test_segment_dash_number_kept_and_duplicates_reported()

### Community 83 - "AI Legal Mentor RAG pipeline"
Cohesion: 0.14
Nodes (14): GET /api/sessions/{session_id}/result, AI Legal Mentor RAG pipeline, Mentor SSE events (sources, block, done, error), Participant 2 (legal/, rag/, ai/ and ingestion pipeline owner), POST /api/mentor/ask (text/event-stream), Query language detection (alphabet + stop words), Query normalization (apostrophes, transliteration for keyword search), RAG_MIN_SCORE (relevance threshold) (+6 more)

### Community 84 - "test_build_and_catalog.py"
Cohesion: 0.18
Nodes (15): build_scenario(), BuildError, attach_audio(), manifest_path(), spoken_lines(), fake_encode(), _attach(), _serve() (+7 more)

### Community 86 - "ingestion/tests/conftest.py"
Cohesion: 0.16
Nodes (8): alembic_config(), create_migrated_database(), ing_db_url(), ing_engine(), session_factory(), Workspace, ws(), demo_factory()

### Community 88 - "Api"
Cohesion: 0.21
Nodes (11): Api, post_quiz(), stats(), test_profile_404_and_validation(), test_profile_get_patch(), test_stats_after_three_playthroughs_and_quiz(), test_stats_unfinished_session_counts_only_started(), test_streak_by_utc_days() (+3 more)

### Community 89 - "test_lexuz.py"
Cohesion: 0.12
Nodes (10): normalize_number(), _ord_alt(), _ord_alt_ru(), to_roman(), blocks(), html(), test_chapter_patterns(), test_section_patterns() (+2 more)

### Community 90 - "Mezon frontend README"
Cohesion: 0.05
Nodes (56): Monorepo layout (frontend/ Next.js 16 + Phaser 4, backend/ FastAPI + Postgres/pgvector + MongoDB history, deploy/vm1/ systemd + CI/CD, docs/ specs), CitationView, Edition status (current | historical | unconfirmed), GameEvent (say, react, stage_changed, evidence_added, score, legal_note, mistake), GameState, GET /api/health, GET /api/legal/citations/{citation_id}, GET /api/sessions/{session_id}/evidence/{evidence_id} (+48 more)

### Community 91 - "cases/page.tsx"
Cohesion: 0.20
Nodes (14): Case list categories 'Life situations' and 'Court cases' (the same for everyone), Claim letter builder to the seller with a stamp (components/common/claim-letter.tsx), SituationScreen (life-situation layout on the play route for kind: "situation" cases), 'What's inside Mezon' section (two categories for everyone: life situations and court cases; buttons open their section of the case list), CasesPage(), hashKind(), KindTab, onHash() (+6 more)

### Community 92 - "analytics/dashboard.py"
Cohesion: 0.22
Nodes (8): build_dashboard(), _category_title(), _latest_attempts(), _level_label(), message(), CompletedSession, FocusTopic, option_label()

### Community 93 - "LoadedScenario"
Cohesion: 0.10
Nodes (14): fallback_chain(), translate(), _case(), lat_to_cyr_display(), _word(), LoadedScenario, build_evidence_document(), build_scenario_card() (+6 more)

### Community 94 - "pytest"
Cohesion: 0.20
Nodes (15): Action, _always(), Condition, Effect, React, Say, test_decision_action_requires_decision_id(), test_exactly_one_key() (+7 more)

### Community 95 - "test_access.py"
Cohesion: 0.24
Nodes (11): as_token(), calls(), do(), test_account_session_may_use_guest_ids(), test_expired_session_loses_access(), test_guests_work_without_login(), test_no_session_gets_401(), test_other_account_gets_403() (+3 more)

### Community 96 - "POST /api/sessions"
Cohesion: 0.20
Nodes (13): CC - Civil Code of Uzbekistan, consumer_dispute_001 (Faulty smartphone case), CPC - Civil Procedure Code of Uzbekistan, CPRL - Law of Uzbekistan 'On Consumer Rights Protection', GET /api/scenarios/{scenario_id}, Current corpus (CONST, CC1, CC2, CPC, CPRL; ru and uz-Latn pages https://lex.uz/docs/<number>), Case intro screen /[locale]/cases/[id], citation_id (stable article identifier, e.g. CPRL.art.X) (+5 more)

### Community 97 - "live.ts"
Cohesion: 0.20
Nodes (11): Evidence document response {id, title, type, lines[]}, call(), convertTexts(), LEGAL_KEYS, localizeTexts(), sse(), TEXT_KEYS, uiLang() (+3 more)

### Community 98 - "backend/tests/conftest.py"
Cohesion: 0.18
Nodes (11): create_app(), build(), alembic_config(), client(), db_engine(), db_session(), db_url(), make_alembic_config() (+3 more)

### Community 99 - "api/history.py"
Cohesion: 0.13
Nodes (7): session_history(), _usable(), user_activity(), ActivityItem, ActivityOut, HistoryStepOut, SessionHistoryOut

### Community 100 - "storage"
Cohesion: 0.16
Nodes (17): healthcheck, RUSTFS_ACCESS_KEY, RUSTFS_ADDRESS, RUSTFS_CONSOLE_ADDRESS, RUSTFS_CONSOLE_ENABLE, RUSTFS_SECRET_KEY, interval, retries (+9 more)

### Community 101 - "test_parse_segment.py"
Cohesion: 0.22
Nodes (11): clean_text(), normalize_blocks(), parse_html(), test_normalize_keeps_lex_id(), test_segment_lexuz(), _blocks(), test_chunks(), test_clean_text_only_junk() (+3 more)

### Community 102 - "auth/sessions.py"
Cohesion: 0.18
Nodes (7): get_optional_user(), create_session(), hash_token(), resolve(), revoke_all(), revoke_token(), AuthSession

### Community 103 - "ADOLAT Backend specification (BACKEND.md)"
Cohesion: 0.14
Nodes (22): ADOLAT Backend specification (BACKEND.md), ADOLAT (legal-education court simulator), CORS_ORIGINS (frontend address), SQLAlchemy 2 (sync, psycopg 3), How legal data and cases are assembled (DATA.md), ADOLAT Legal Ingestion specification (INGESTION.md), Local models and AI (MODELS.md), How to run the project (SETUP.md) (+14 more)

### Community 104 - "test_history_store.py"
Cohesion: 0.21
Nodes (9): mongo_docs(), play_everything(), _snapshot_mongo(), test_activity_has_all_types(), test_backfill_fills_gaps_next_to_live_records(), test_backfill_inmemory(), test_backfill_rebuilds_mongo(), test_inmemory_store_works_without_mongo() (+1 more)

### Community 105 - "synth.py"
Cohesion: 0.23
Nodes (6): ensure_model(), _sha256(), SileroSynth, split_text(), Synth, Voice

### Community 106 - "chunk.py"
Cohesion: 0.28
Nodes (8): article_label(), build_chunks(), _clean(), doc_title_for(), estimate_tokens(), make_header(), _text(), _tokens()

### Community 107 - "load_all"
Cohesion: 0.25
Nodes (10): load_all(), ScenarioValidationError, copy_fixtures(), edit_json(), test_invalid_scenario_json_collected(), test_load_all_fixtures_ok(), test_missing_cyrl_key_is_only_warning(), test_missing_quiz_key_is_error() (+2 more)

### Community 108 - "summary.py"
Cohesion: 0.16
Nodes (4): round_half_up(), scenario_summary(), get_summary(), ScenarioSummary

### Community 109 - "load_scenario_dir"
Cohesion: 0.10
Nodes (29): load_scenario_dir(), build_game_state(), _edit(), explained_dir(), sc(), _find_action(), _score_events(), test_effect_score_accepts_number_and_object() (+21 more)

### Community 110 - ".play"
Cohesion: 0.38
Nodes (8): _err(), test_decision_without_valid_option_is_illegal(), test_illegal_action(), test_not_found(), test_outdated_session_after_scenario_change(), test_patch_locale_keeps_game_state(), test_session_finished_and_not_finished(), test_validation_errors()

### Community 111 - "InMemoryHistoryStore"
Cohesion: 0.12
Nodes (5): InMemoryHistoryStore, test_mongo_history_is_reassigned(), hclient(), _make(), settable_clock()

### Community 112 - "stats.py"
Cohesion: 0.49
Nodes (5): on_quiz_attempt(), on_session_finished(), on_session_started(), _row(), _touch()

### Community 113 - "Committed graphify knowledge graph (graphify-out/)"
Cohesion: 0.31
Nodes (10): Mezon: notes for Claude Code (CLAUDE.md), graphify-out/graph.html (interactive graph view), graphify-out/graph.json (graph data used by graphify query), graphify-out/GRAPH_REPORT.md (communities, god nodes, surprising connections, open questions), graphify CLI (graphify query / path / explain), Committed graphify knowledge graph (graphify-out/), Graphify local state in graphify-out/ (cache, manifest), git-ignored, /graphify skill (.claude/skills/graphify, installs graphifyy on first use) (+2 more)

### Community 114 - "npc/test_schema.py"
Cohesion: 0.35
Nodes (11): broken(), has(), q(), test_character_does_not_know_fact(), test_duplicate_question_id(), m(), test_results_stage_not_allowed(), test_text_keys_collected() (+3 more)

### Community 117 - "content.ts"
Cohesion: 0.33
Nodes (5): ACT_TITLES, Dict, QUIZ, RU, UZ

### Community 118 - "get_scenario"
Cohesion: 0.25
Nodes (4): get_scenario(), get_scenario_audio(), list_scenarios(), GET /api/scenarios

### Community 119 - "target"
Cohesion: 0.20
Nodes (11): Manual deploy (Actions -> CI/CD -> Run workflow: all, frontend or backend), target, on, push, workflow_dispatch, branches, default, description (+3 more)

### Community 121 - "Settings"
Cohesion: 0.07
Nodes (18): ask(), gen(), format_sse(), get_event_db_factory(), _recorder(), Settings, embedder_dep(), Embedder (+10 more)

### Community 122 - "scripts"
Cohesion: 0.28
Nodes (8): Local pre-push checks (frontend: pnpm i18n && pnpm typecheck && pnpm build; backend: make test), scripts, build, dev, i18n, lint, start, typecheck

### Community 123 - "test_dashboard.py"
Cohesion: 0.33
Nodes (8): dash(), quiz(), test_dashboard_404(), test_dashboard_after_three_games(), test_dashboard_uz_latn(), test_knowledge_level_labels(), test_new_user_dashboard(), test_recommended_reasons()

### Community 124 - "steps"
Cohesion: 0.24
Nodes (10): steps, steps, id, if, name, run, uses, with (+2 more)

### Community 126 - "Works without models (mentor shows found articles, NPCs use canned replies, full-text search)"
Cohesion: 0.16
Nodes (9): env_file, path, required, ANTHROPIC_API_KEY, anthropic SDK, LLM_MODEL_FAST (claude-haiku-5-5), POST /api/sessions/{session_id}/npc/{character_id}/ask (P2), Query classification (article_lookup | concept | case_specific | out_of_scope) (+1 more)

### Community 127 - "changes"
Cohesion: 0.29
Nodes (6): outputs, runs-on, changes, backend, frontend, infra

### Community 128 - "ci-cd.yml"
Cohesion: 0.25
Nodes (7): concurrency, cancel-in-progress, group, jobs, name, permissions, contents

### Community 129 - "allowBuilds"
Cohesion: 0.29
Nodes (6): allowBuilds, @parcel/watcher, sharp, @swc/core, unrs-resolver, minimumReleaseAgeExclude

### Community 130 - "deploy"
Cohesion: 0.25
Nodes (8): environment, if, name, needs, runs-on, name, url, deploy

### Community 131 - "legal_data/seed.sql.gz (demo seed)"
Cohesion: 0.17
Nodes (11): volumes, mongodata, pgdata, storagedata, legal_data/processed/*.articles.jsonl (parsed articles, source of article numbers), legal_data/processed/embeddings_cache/ (vector cache), Legal data not in git (processed/*.jsonl, processed/embeddings_cache/, seed.sql.gz via Git LFS), Seed stored in Git LFS (.gitattributes; git pull fetches it when git-lfs is installed) (+3 more)

### Community 132 - "vm1 (vm1.modeus.cc)"
Cohesion: 0.36
Nodes (8): mezon-backend.service (127.0.0.1:8000), mezon-db.service (Postgres container), mezon-frontend.service (127.0.0.1:3000), mezon-mongo.service (MongoDB history), mezon-mongodata docker volume, mezon-pgdata docker volume, nginx reverse proxy (/api/* -> :8000, everything else -> :3000), vm1 (vm1.modeus.cc)

### Community 133 - "events.py"
Cohesion: 0.23
Nodes (5): ingest(), post_events(), EventsIn, EventsOut, POST /api/events (P1)

### Community 135 - ".mcp.json"
Cohesion: 0.67
Nodes (3): npx, next-devtools, shadcn

### Community 152 - "select.tsx"
Cohesion: 0.22
Nodes (3): SelectContent(), SelectScrollDownButton(), SelectScrollUpButton()

### Community 153 - "NullHistoryStore"
Cohesion: 0.20
Nodes (3): NullHistoryStore, test_history_endpoint_mongo_matches_postgres(), test_null_store_history_from_postgres()

### Community 154 - "tts/conftest.py"
Cohesion: 0.28
Nodes (3): FakeSynth, loaded(), synth()

### Community 155 - "Озвучка реплик (TTS)"
Cohesion: 0.22
Nodes (8): API, Голоса, Как собрать и залить, Кто каким голосом говорит, Лицензии, Озвучка реплик (TTS), Хранилище, Что озвучивается

### Community 156 - "get_glossary"
Cohesion: 0.25
Nodes (3): glossary(), get_glossary(), _load()

### Community 157 - "env.py"
Cohesion: 0.38
Nodes (4): get_url(), run_migrations_offline(), run_migrations_online(), Alembic migrations

### Community 159 - "_make"
Cohesion: 0.33
Nodes (3): Mentor, _make(), parse_sse()

## Ambiguous Edges - Review These
- `courtroom.ts` → `Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `GoogleOAuth` → `authlib (Starlette integration)`  [AMBIGUOUS]
  frontend/AUTH.md · relation: conceptually_related_to
- `types.ts` → `Generated API client (openapi-typescript + openapi-fetch, make api-client)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `In-browser mock backend (localStorage)` → `Thin client: no game logic or scenario texts in the frontend`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to
- `Uzbek Cyrillic -> Latin transliteration table (search only)` → `Uzbek Latin 2026 alphabet (law of 21.10.2026)`  [AMBIGUOUS]
  frontend/README.md · relation: conceptually_related_to

## Knowledge Gaps
- **13 isolated node(s):** `adolat-ingestion`, `graphify-out/graph.html (interactive graph view)`, `graphify-out/GRAPH_REPORT.md (communities, god nodes, surprising connections, open questions)`, `Uzbek text is legally binding; Russian lex.uz texts are unofficial translations`, `Pydantic v2` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1095 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **42 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Settings` to `test_mentor_flow.py`, `test_registry_paths.py`, `api/mentor.py`, `re`, `ai/mentor.py`, `search.py`, `search`, `game/conftest.py`, `test_npc_flow.py`, `run`, `test_google.py`, `Auth security basics (state/PKCE check, next-path validation, CSRF, rate limiting)`, `Legal ingestion pipeline (10 steps)`, `sqlalchemy`, `test_email_auth.py`, `health`, `service.py`, `DocumentVersion`, `api/auth.py`, `Claude Haiku 5.5 via Anthropic API key (claude-haiku-5-5 for LLM_MODEL_MENTOR and LLM_MODEL_FAST)`, `OllamaEmbedder`, `GoogleOAuth`, `ratelimit.py`, `Cases in scenarios/ (one folder per case with scenario.json, quiz.json, texts.ru.json, texts.uz-Latn.json; not stored in git)`, `ask_npc`, `test_embed_db.py`, `AI Legal Mentor RAG pipeline`, `test_build_and_catalog.py`, `backend/tests/conftest.py`, `auth/sessions.py`, `ADOLAT Backend specification (BACKEND.md)`, `Works without models (mentor shows found articles, NPCs use canned replies, full-text search)`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Are the 74 inferred relationships involving `Settings` (e.g. with `classify_question()` and `get_llm()`) actually correct?**
  _`Settings` has 74 INFERRED edges - model-reasoned connections that need verification._
- **What connects `adolat-ingestion`, `graphify-out/graph.html (interactive graph view)`, `graphify-out/GRAPH_REPORT.md (communities, god nodes, surprising connections, open questions)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_mentor_flow.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05015873015873016 - nodes in this community are weakly interconnected._
- **Why does `Accounts and Google SSO (AUTH.md)` connect `Auth security basics (state/PKCE check, next-path validation, CSRF, rate limiting)` to `situation-screen.tsx`, `auth/sessions.py`, `react`, `vm1 deployment (CI/CD + systemd)`, `Mezon frontend README`, `cases/page.tsx`, `api/auth.py`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `courtroom.ts` and `Game assets in frontend/public/game/ (Aseprite sprite sheets, sounds, licenses)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `GoogleOAuth` and `authlib (Starlette integration)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._