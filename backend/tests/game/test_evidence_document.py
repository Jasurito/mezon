"""Текст документов из материалов дела: GET /api/sessions/{id}/evidence/{evidence_id}."""

import uuid

import pytest

from tests.game.conftest import BEST

pytestmark = pytest.mark.db


def test_documents_follow_the_case_file(api, seeded_db):
    sid = api.start(api.user())["session_id"]

    # INTRO: материалов дела ещё нет
    assert api.c.get(f"/api/sessions/{sid}/evidence/contract").status_code == 404

    api.play(sid, BEST[:1])  # enter_courtroom -> материалы дела открыты
    r = api.c.get(f"/api/sessions/{sid}/evidence/contract")
    assert r.status_code == 200, r.text
    doc = r.json()
    assert doc["id"] == "contract" and doc["type"] == "document" and doc["title"]
    assert doc["lines"] == ["Смартфон куплен в магазине."]  # у договора нет своего текста: факты, которые он подтверждает

    # заключение эксперта появляется только после экспертизы
    assert api.c.get(f"/api/sessions/{sid}/evidence/expert_report").status_code == 404
    api.play(sid, BEST[1 : BEST.index(("request_expertise", None)) + 1])
    r = api.c.get(f"/api/sessions/{sid}/evidence/expert_report")
    assert r.status_code == 200, r.text
    assert r.json()["lines"] == ["Дефект зарядного разъёма носит производственный характер."]


def test_document_locale_and_unknown(api, seeded_db):
    sid = api.start(api.user())["session_id"]
    api.play(sid, BEST[:1])
    uz = api.c.get(f"/api/sessions/{sid}/evidence/contract", params={"locale": "uz-Latn"})
    assert uz.status_code == 200 and uz.json()["lines"] and uz.json()["lines"] != ["Смартфон куплен в магазине."]
    assert api.c.get(f"/api/sessions/{sid}/evidence/no_such_doc").status_code == 404
    assert api.c.get(f"/api/sessions/{uuid.uuid4()}/evidence/contract").status_code == 404
