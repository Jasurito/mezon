"""Кто учится: юрист / студент-юрист (professional) или не специалист (public)."""

import pytest

from tests.auth.conftest import H, ORIGIN, PASSWORD, as_token

pytestmark = pytest.mark.db


def _signup(c, email, audience="__omit__"):
    body = {"display_name": "Aziz", "email": email, "password": PASSWORD}
    if audience != "__omit__":
        body["audience"] = audience
    return c.post("/api/auth/signup", json=body, headers={"Origin": ORIGIN})


@pytest.mark.parametrize("audience", ["professional", "public"])
def test_signup_stores_audience(client, audience):
    r = _signup(client, f"{audience}@example.com", audience)
    assert r.status_code == 201, r.text
    assert r.json()["audience"] == audience
    assert client.get("/api/auth/me").json()["audience"] == audience


def test_audience_is_optional_and_validated(client):
    r = _signup(client, "old@example.com")  # older clients do not send it
    assert r.status_code == 201 and r.json()["audience"] is None
    client.cookies.clear()
    bad = _signup(client, "bad@example.com", "judge")
    assert bad.status_code == 422


def test_patch_audience_owner_only(client, make_account):
    uid, token = make_account("own@example.com")
    _other, other_token = make_account("other@example.com")

    as_token(client, token)
    r = client.patch(f"/api/users/{uid}", json={"audience": "professional"}, headers=H)
    assert r.status_code == 200, r.text
    assert r.json()["audience"] == "professional"
    assert client.get("/api/auth/me").json()["audience"] == "professional"
    # other fields untouched, null clears
    assert client.patch(f"/api/users/{uid}", json={"display_name": "Aziz 2"}, headers=H).json()["audience"] == "professional"
    assert client.patch(f"/api/users/{uid}", json={"audience": None}, headers=H).json()["audience"] is None
    assert client.patch(f"/api/users/{uid}", json={"audience": "lawyer"}, headers=H).status_code == 422

    as_token(client, other_token)
    assert client.patch(f"/api/users/{uid}", json={"audience": "public"}, headers=H).status_code == 403


def test_guest_can_set_audience(client, make_guest):
    gid = make_guest()
    r = client.patch(f"/api/users/{gid}", json={"audience": "public"})
    assert r.status_code == 200 and r.json()["audience"] == "public"
    assert client.get(f"/api/users/{gid}").json()["audience"] == "public"
