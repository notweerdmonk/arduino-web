import pytest
from medminder_dash.app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        from medminder_dash.app import store

        # Reset the persisted metadata to a clean state
        store._board_meta.clear()
        store._save()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_per_board_storage_isolation(client, app):
    # Select a board first (e.g., "Board1")
    with app.app_context():
        with client.session_transaction() as sess:
            sess["board_port"] = "Board1"

    # Create a medicine on Board1
    resp = client.post(
        "/medicine",
        data={"name": "Aspirin", "hour": "8", "minute": "0"},
    )
    assert resp.status_code == 200
    assert b"Aspirin" in resp.data

    # Switch to a different board (e.g., COM3) directly via session
    # (avoid board_select route which triggers lazy alarm.hpp bootstrap)
    with client.session_transaction() as sess:
        sess["board_port"] = "COM3"

    # Create a second medicine on the COM3 board
    resp = client.post(
        "/medicine",
        data={"name": "Ibuprofen", "hour": "9", "minute": "30"},
    )
    assert resp.status_code == 200
    assert b"Ibuprofen" in resp.data

    # Verify that each board has its own medicine list
    from medminder_dash.app import store

    board1_meds = store._board_meta.get("Board1", {}).get("medicines", [])
    com3_meds = store._board_meta.get("COM3", {}).get("medicines", [])
    assert len(board1_meds) == 1
    assert board1_meds[0].name == "Aspirin"
    assert len(com3_meds) == 1
    assert com3_meds[0].name == "Ibuprofen"


def test_create_medicine_requires_board(client, app):
    """POST /medicine without a board selected must return 400."""
    resp = client.post(
        "/medicine",
        data={"name": "Test", "hour": "12", "minute": "0"},
    )
    assert resp.status_code == 400
    assert b"Select a board first" in resp.data
