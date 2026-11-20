"""Write JSON Schemas for the content team: ``python -m app.schemas.export``."""

from __future__ import annotations

import json
from pathlib import Path

from app.schemas.quiz import Quiz
from app.schemas.scenario import Scenario

OUT_DIR = Path(__file__).parent


def export_schemas(out_dir: Path = OUT_DIR) -> list[Path]:
    """Write scenario.schema.json and quiz.schema.json, return their paths."""
    paths = []
    for name, model in (("scenario", Scenario), ("quiz", Quiz)):
        path = out_dir / f"{name}.schema.json"
        schema = model.model_json_schema()
        path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        paths.append(path)
    return paths


if __name__ == "__main__":
    for p in export_schemas():
        print(p)
