import pytest

from app.game_engine import collect_citation_ids
from app.legal.service import missing_citation_ids
from app.models.legal import Citation
from app.scenarios import load_scenario_dir
from app.scenarios.registry import CitationCheckError
from tests.game.conftest import SCENARIOS_FIXTURES

pytestmark = pytest.mark.db


def _ids():
    return collect_citation_ids(load_scenario_dir(SCENARIOS_FIXTURES / "test_consumer").scenario)


def test_all_scenario_citations_resolve(seeded_db):
    ids = _ids()
    assert ids
    assert missing_citation_ids(seeded_db, ids) == set()


def _drop(db, citation_id):
    assert db.query(Citation).filter(Citation.citation_id == citation_id).delete() == 1
    db.flush()


def test_startup_fails_on_missing_citation(seeded_db, make_client):
    victim = sorted(_ids())[0]
    _drop(seeded_db, victim)
    with pytest.raises(CitationCheckError) as ei:
        with make_client():
            pass
    msg = str(ei.value)
    assert "test_consumer" in msg and victim in msg


def test_startup_ok_when_not_strict(seeded_db, make_client, caplog):
    victim = sorted(_ids())[0]
    _drop(seeded_db, victim)
    with caplog.at_level("WARNING"):
        with make_client(strict_citations=False) as c:
            assert c.get("/api/health").json()["scenarios"] == 1
    assert victim in caplog.text


def test_missing_scenarios_dir_gives_empty_registry(make_client, tmp_path, caplog):
    with caplog.at_level("WARNING"):
        with make_client(scenarios_dir=tmp_path / "nope") as c:
            assert c.get("/api/health").json()["scenarios"] == 0
            assert c.get("/api/scenarios").json() == []
    assert "nope" in caplog.text


def test_invalid_scenario_stops_startup(make_client, tmp_path):
    import shutil

    from app.scenarios import ScenarioValidationError

    dst = tmp_path / "bad"
    shutil.copytree(SCENARIOS_FIXTURES / "test_consumer", dst / "test_consumer")
    (dst / "test_consumer" / "texts.ru.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ScenarioValidationError):
        with make_client(scenarios_dir=dst):
            pass
