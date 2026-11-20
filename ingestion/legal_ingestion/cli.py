"""CLI: python -m legal_ingestion <команда> (docs/INGESTION.md §5)."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from legal_ingestion import pipeline
from legal_ingestion.errors import IngestionError
from legal_ingestion.paths import REPO_ROOT, Paths
from legal_ingestion.sources import stem_of

FETCH_DISABLED = (
    "Команда fetch в MVP выключена: у lex.uz нет подтверждённого открытого API, а автоматическое "
    "скачивание без разрешения запрещено. Документы кладутся в legal_data/raw/ вручную "
    "(см. legal_data/README.md) и описываются в legal_data/sources.yaml."
)


def _common(p: argparse.ArgumentParser, *, suppress: bool) -> None:
    d = argparse.SUPPRESS if suppress else None
    p.add_argument("--legal-dir", type=Path, default=d, help="каталог legal_data (по умолчанию <repo>/legal_data)")
    p.add_argument("--scenarios-dir", type=Path, default=d, help="каталог scenarios (по умолчанию <repo>/scenarios)")
    p.add_argument("--processed-dir", type=Path, default=d, help="куда писать JSONL шагов (по умолчанию <legal-dir>/processed)")
    p.add_argument("--sources", type=Path, default=d, help="путь к sources.yaml")
    p.add_argument("--citations", type=Path, default=d, help="путь к citations.yaml")
    p.add_argument("--database-url", default=d, help="переопределить DATABASE_URL")
    p.add_argument("-v", "--verbose", action="store_true", default=argparse.SUPPRESS if suppress else False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m legal_ingestion",
        description="Офлайн-конвейер загрузки законодательства ADOLAT: legal_data/raw + sources.yaml -> Postgres.",
    )
    _common(parser, suppress=False)
    sub = parser.add_subparsers(dest="command", required=True, metavar="команда")

    def add(name: str, help_: str, *, doc: bool = False) -> argparse.ArgumentParser:
        sp = sub.add_parser(name, help=help_, description=help_)
        _common(sp, suppress=True)
        if doc:
            sp.add_argument("--doc", help="document_key (по умолчанию все документы)")
        return sp

    r = add("run", "шаги 1-10: validate, parse, normalize, segment, version, chunk, embed, load, link, check", doc=True)
    r.add_argument("--reembed", action="store_true", help="пересчитать векторы, игнорируя кэш")
    r.add_argument(
        "--draft-activate",
        action="store_true",
        help="загрузить редакции как active без verified_by (черновики для локальной проверки); "
        "только база, имя которой оканчивается на _demo",
    )
    for name, h in (
        ("parse", "только parse+normalize (без БД), пишет processed/*.blocks.jsonl"),
        ("segment", "parse+normalize+segment (без БД), пишет processed/*.articles.jsonl"),
        ("chunk", "до chunk включительно (без БД), пишет processed/*.chunks.jsonl"),
    ):
        add(name, h, doc=True)
    add("check", "только проверки целостности, отчёт processed/check_report.md")
    add("diff", "изменения по статьям между двумя последними редакциями", doc=True).set_defaults(need_doc=True)
    a = add("activate", "подтвердить редакцию (pending_review -> active)", doc=True)
    a.add_argument("--version", type=int, required=True, help="id в document_versions")
    a.add_argument("--by", required=True, help="инициалы проверяющего")
    e = add("eval", "Recall@K по eval/gold.jsonl (sparse/dense/hybrid)")
    e.add_argument("--k", type=int, default=5)
    e.add_argument("--gold", type=Path, help="путь к gold.jsonl (по умолчанию <repo>/eval/gold.jsonl)")
    add("dump", "дамп данных правовых таблиц в legal_data/seed.sql.gz").add_argument(
        "--out", type=Path, help="путь к seed (по умолчанию <legal-dir>/seed.sql.gz)"
    )
    sd = add("sources-draft", "черновик legal_data/sources.yaml из скачанных страниц lex.uz (без БД и сети)")
    sd.add_argument("--force", action="store_true", help="перезаписать существующий sources.yaml, сохранив заполненные поля")
    add("fetch", "выключено в MVP")
    return parser


def _session_factory(database_url: str | None) -> Callable[[], Session]:
    if database_url:
        return sessionmaker(bind=create_engine(database_url, pool_pre_ping=True), autoflush=False, expire_on_commit=False)
    from app.db import SessionLocal

    return SessionLocal


def _paths(args: argparse.Namespace) -> Paths:
    legal = (args.legal_dir or REPO_ROOT / "legal_data").resolve()
    return Paths(
        legal_dir=legal,
        scenarios_dir=(args.scenarios_dir or REPO_ROOT / "scenarios").resolve(),
        sources=args.sources,
        citations=args.citations,
        processed=args.processed_dir,
        gold=getattr(args, "gold", None),
        seed=getattr(args, "out", None),
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(message)s", stream=sys.stdout)
    try:
        return _dispatch(args)
    except IngestionError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 2


def _dispatch(args: argparse.Namespace) -> int:
    cmd = args.command
    if cmd == "fetch":
        print(FETCH_DISABLED)
        return 1
    paths = _paths(args)
    if cmd == "sources-draft":
        from legal_ingestion.draft import write_draft

        _, warnings = write_draft(paths.legal_dir, paths.sources_file, force=args.force)
        print(f"sources-draft: {paths.sources_file}")
        for w in warnings:
            print(f"  предупреждение: {w}", file=sys.stderr)
        return 0
    if cmd in ("parse", "segment", "chunk"):
        return _debug_steps(args, paths)

    from app.config import Settings, get_settings
    from app.rag.embedder import get_embedder

    settings = Settings(DATABASE_URL=args.database_url) if args.database_url else get_settings()
    sf = _session_factory(args.database_url)

    if cmd == "run":
        res = pipeline.run(paths, sf, get_embedder(settings), doc=args.doc, reembed=args.reembed, draft_activate=args.draft_activate)
        for e in res.editions:
            extra = f" ({e.error})" if e.error else f" version id={e.version_id}, {e.review_status}, статей {e.articles}, чанков {e.chunks}"
            print(f"{e.stem}: {e.action}{extra}")
        print(f"citations: {res.citations}")
        for m in res.link_errors:
            print(f"link: {m}", file=sys.stderr)
        ok = res.ok
        if res.check:
            print(f"check: ошибок {len(res.check.errors)}, предупреждений {len(res.check.warnings)}; отчёт {paths.processed_dir / 'check_report.md'}")
            for i in res.check.errors:
                print(f"  ошибка: {i.message}", file=sys.stderr)
            if args.draft_activate and not ok:
                # «активная редакция без verified_by» при --draft-activate ожидаема: check её по-прежнему
                # сообщает, но демо-загрузка из-за неё не падает
                rest = [i for i in res.check.errors if "без verified_by" not in i.message]
                ok = not (res.errors or res.link_errors or rest or any(e.action == "failed" for e in res.editions))
                if ok:
                    print("draft-activate: редакции без verified_by загружены как active (черновики, только для демо-базы)")
        return 0 if ok else 1

    if cmd == "check":
        from legal_ingestion.check import run_check
        from legal_ingestion.sources import load_sources

        sources, errs = load_sources(paths.sources_file, paths.legal_dir)
        res = run_check(sf, paths, sources, errs)
        print(f"check: ошибок {len(res.errors)}, предупреждений {len(res.warnings)}; отчёт {paths.processed_dir / 'check_report.md'}")
        for i in res.issues:
            print(f"  {'ошибка' if i.level == 'error' else 'предупреждение'}: {i.message}")
        return 1 if res.errors else 0

    if cmd == "diff":
        from legal_ingestion.diff import diff_document

        if not args.doc:
            raise IngestionError("diff: укажите --doc <document_key>")
        written = diff_document(sf, paths, args.doc)
        for p in written:
            print(f"diff: {p}")
        if not written:
            print("diff: у документа нет двух редакций одного языка, сравнивать нечего")
        return 0

    if cmd == "activate":
        return _activate(args, sf)

    if cmd == "eval":
        from legal_ingestion.evaluation import run_eval

        print(run_eval(sf, paths, settings, get_embedder(settings), k=args.k))
        return 0

    if cmd == "dump":
        from legal_ingestion.dump import assert_no_drafts, dump_seed

        assert_no_drafts(sf)
        out = dump_seed(paths, settings.DATABASE_URL)
        print(f"dump: {out} ({out.stat().st_size} байт)")
        return 0
    raise IngestionError(f"неизвестная команда {cmd}")


def _debug_steps(args: argparse.Namespace, paths: Paths) -> int:
    from legal_ingestion.parse import BODY_SELECTORS  # noqa: F401  (подсказка: правится в parse.py)

    sources = pipeline.validate(paths)
    code = 0
    for d in pipeline.select_documents(sources, args.doc):
        for v in d.versions:
            stem = stem_of(d, v)
            _, cleaned = pipeline.parse_edition(paths, d, v)
            if args.command == "parse":
                print(f"{stem}: блоков {len(cleaned)}")
                continue
            try:
                articles = pipeline.segment_edition(paths, d, v, cleaned)
            except IngestionError as exc:
                print(f"{stem}: ОШИБКА {exc}", file=sys.stderr)
                code = 1
                continue
            if args.command == "segment":
                print(f"{stem}: статей {len(articles)}")
                continue
            chunks = pipeline.chunk_edition(paths, d, v, articles)
            print(f"{stem}: чанков {len(chunks)}")
    return code


def _activate(args: argparse.Namespace, sf: Callable[[], Session]) -> int:
    from app.models.legal import DocumentVersion, LegalDocument
    from legal_ingestion.version import activate_version

    if not args.doc:
        raise IngestionError("activate: укажите --doc <document_key>")
    session = sf()
    try:
        with session.begin():
            doc = session.scalar(select(LegalDocument).where(LegalDocument.document_key == args.doc))
            v = session.get(DocumentVersion, args.version)
            if doc is None or v is None or v.document_id != doc.id:
                raise IngestionError(f"редакция id={args.version} документа {args.doc} не найдена")
            if v.review_status == "active" and v.verified_by:
                print(f"редакция id={v.id} уже active (verified_by={v.verified_by})")
                return 0
            changed = activate_version(session, v, args.by)
            for c in changed:
                print(f"id={c.id} {c.language} {c.effective_from}: {c.review_status}, effective_to={c.effective_to}")
        return 0
    finally:
        session.close()
