import pytest

from tests.game.conftest import BEST, LOSS, PARTIAL

pytestmark = pytest.mark.db


@pytest.mark.parametrize("path", [BEST, PARTIAL, LOSS], ids=["best", "partial", "loss"])
def test_same_log_same_state(api, path):
    a = api.start(api.user())["session_id"]
    b = api.start(api.user())["session_id"]
    sa, sb = api.play(a, path), api.play(b, path)

    def strip(s):
        return {k: v for k, v in s.items() if k != "session_id"}

    assert [strip(x) for x in sa] == [strip(x) for x in sb]
    ga, gb = api.c.get(f"/api/sessions/{a}").json(), api.c.get(f"/api/sessions/{b}").json()
    assert strip(ga) == strip(gb)
    ra, rb = api.c.get(f"/api/sessions/{a}/result").json(), api.c.get(f"/api/sessions/{b}/result").json()
    # время прохождения зависит от часов, остальное определяется логом
    assert {k: v for k, v in ra.items() if k not in ("session_id", "time_spent_sec")} == {
        k: v for k, v in rb.items() if k not in ("session_id", "time_spent_sec")
    }
