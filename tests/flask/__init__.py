import pytest

from backend.server.app import create_app


@pytest.fixture
def client():
    app = create_app(app_config="test")
    with app.test_client() as client:
        yield client
