"""Тесты настоящих дел: дела хранятся вне git (scenarios/ в .gitignore).

Если папки дела нет (например, в CI), тесты этого дела не собираются.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "scenarios"
CASES = {
    "test_consumer_moisture": "consumer_moisture_001",
    "test_wedding_photo": "wedding_photo_002",
    "test_rent_deposit": "rent_deposit_003",
    "test_phone_life": "phone_defect_life_001",
}

collect_ignore = [
    p.name
    for p in Path(__file__).parent.glob("test_*.py")
    for prefix, case in CASES.items()
    if p.stem.startswith(prefix) and not (ROOT / case / "scenario.json").is_file()
]
