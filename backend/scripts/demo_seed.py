"""Prepare the local demo database: create it, run migrations, load TEST legal data once.

Used by `make demo`. The data is the test corpus from tests/fixtures (clearly marked as
test data, not real law). It goes into a separate database (adolat_demo), so the main
`adolat` database stays empty for the real seed from ingestion.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.models.legal import LegalDocument  # noqa: E402
from tests.fixtures.legal_seed import seed_test_legal_data  # noqa: E402
from tests.fixtures.rag_seed import seed_test_chunks  # noqa: E402


def main() -> None:
    url = make_url(os.environ["DATABASE_URL"])
    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        if not conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": url.database}).scalar():
            conn.execute(text(f'CREATE DATABASE "{url.database}"'))
            print(f"created database {url.database}")
    admin.dispose()

    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    cfg.attributes["url"] = url.render_as_string(hide_password=False)
    cfg.attributes["configure_logging"] = False
    command.upgrade(cfg, "head")

    engine = create_engine(url)
    with Session(engine) as s:
        if s.scalar(select(func.count()).select_from(LegalDocument)):
            print("demo legal data already loaded")
        else:
            seed_test_legal_data(s)
            seed_test_chunks(s)
            s.commit()
            print("loaded TEST legal data (not real law)")
    engine.dispose()


if __name__ == "__main__":
    main()
