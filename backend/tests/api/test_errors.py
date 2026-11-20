import pytest
from pydantic import BaseModel

from app.errors import IllegalActionError, SessionFinishedError

pytestmark = pytest.mark.db


class Body(BaseModel):
    n: int


def test_unknown_route_is_not_found(client):
    r = client.get("/api/nope")
    assert r.status_code == 404
    err = r.json()["error"]
    assert err["code"] == "NOT_FOUND"
    assert isinstance(err["message"], str)
    assert "details" in err


def test_validation_error_format(client):
    @client.app.post("/api/_test/validate")
    def validate(body: Body):
        return body

    r = client.post("/api/_test/validate", json={"n": "abc"})
    assert r.status_code == 422
    err = r.json()["error"]
    assert err["code"] == "VALIDATION_ERROR"
    assert isinstance(err["details"]["errors"], list) and err["details"]["errors"]


@pytest.mark.parametrize(
    "exc,status,code",
    [
        (IllegalActionError(), 409, "ILLEGAL_ACTION"),
        (SessionFinishedError(details={"x": 1}), 409, "SESSION_FINISHED"),
    ],
)
def test_app_error(client, exc, status, code):
    @client.app.get("/api/_test/boom")
    def boom():
        raise exc

    r = client.get("/api/_test/boom")
    assert r.status_code == status
    assert r.json()["error"]["code"] == code
    assert r.json()["error"]["details"] == exc.details
