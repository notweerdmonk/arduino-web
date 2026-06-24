import pytest
from medminder_dash.app import create_app
from medminder_dash.medicines_state import Medicine


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        from medminder_dash.app import store

        store._medicines.clear()
        store._lock = __import__("threading").Lock()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seeded_store(app):
    from medminder_dash.app import store

    m1 = Medicine(name="Ibup", hour=8, minute=30, day_of_week=1, day_of_month=0)
    store.add(m1)
    store.add(Medicine(name="PaRa", hour=20, minute=0, day_of_week=3, day_of_month=0))
    return m1


class TestOnlyEnabled:
    def test_returns_enabled_only(self, app):
        from medminder_dash.app import store

        m1 = Medicine(name="A", hour=1, minute=0)
        m2 = Medicine(name="B", hour=2, minute=0)
        m2.enabled = False
        store.add(m1)
        store.add(m2)
        enabled = store.only_enabled()
        assert len(enabled) == 1
        assert enabled[0].name == "A"

    def test_returns_all_when_all_enabled(self, app):
        from medminder_dash.app import store

        store.add(Medicine(name="A", hour=1, minute=0))
        store.add(Medicine(name="B", hour=2, minute=0))
        assert len(store.only_enabled()) == 2

    def test_returns_empty_when_none_enabled(self, app):
        from medminder_dash.app import store

        m1 = Medicine(name="A", hour=1, minute=0)
        m2 = Medicine(name="B", hour=2, minute=0)
        m1.enabled = False
        m2.enabled = False
        store.add(m1)
        store.add(m2)
        assert len(store.only_enabled()) == 0


class TestGenerateEndpoint:
    """Legacy tests for the old /api/generate endpoint. Removed in Phase 60.
    The functionality is now provided by /medicines/generate-hpp (with confirm token)."""


class TestDeployPage:
    """Legacy tests for the old /deploy page. Removed in Phase 60.
    The functionality is now provided by the merged /admin page."""


class TestBoardList:
    def test_api_boards_returns_200(self, client):
        resp = client.get("/boards")
        assert resp.status_code == 200
