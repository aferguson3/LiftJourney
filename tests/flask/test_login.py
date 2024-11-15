from unittest.mock import patch

import pytest
from garth import Client

# noinspection PyProtectedMember
from backend.server.routes.auth import _validate_login
from tests.flask import client

LOGIN_PATH = "/login"
MFA_PATH = "/mfa_code"


@pytest.fixture
def oauth_tokens_found():
    with patch(
        "backend.server.routes.auth.load_oauth_tokens", return_value=False
    ) as mock_function:
        yield mock_function


@pytest.fixture
def valid_login_form():
    with patch("backend.server.routes.auth.LoginForm") as mock_form:
        mock_form.validate_on_submit.return_value = True
        yield mock_form


@pytest.fixture
def successful_login():
    with patch("backend.server.routes.auth.custom_sso_login") as mock_login_status:
        mock_login_status.return_value = "valid csrf token"
        yield mock_login_status


def test_get_request_login(client):
    response = client.get(LOGIN_PATH)
    assert response.status_code == 200
    assert b"Login" in response.data


def test_successful_load_oauth_tokens(oauth_tokens_found, client):
    oauth_tokens_found.return_value = True

    assert oauth_tokens_found() is True
    response = client.get("/login")

    assert response.status_code == 200
    assert b"Login Success" in response.data


def test_invalid_login_form_entry(oauth_tokens_found, successful_login, client):
    def _returns_to_login_page(response):
        assert response.status_code == 200
        assert b"email" in response.data
        assert b"password" in response.data

    oauth_tokens_found.return_value = False
    assert oauth_tokens_found() is False
    assert isinstance(successful_login(), str)

    resp = client.post("/login", data={"email": "", "password": ""})
    _returns_to_login_page(resp)
    resp = client.post("/login", data={"email": "", "password": "testpassword"})
    _returns_to_login_page(resp)
    resp = client.post(
        "/login", data={"email": "email.gmail.com", "password": "testpassword"}
    )
    _returns_to_login_page(resp)
    resp = client.post("/login", data={"email": "email@gmail.com", "password": ""})
    _returns_to_login_page(resp)
    resp = client.post("/login", data={"email": "johhnyappl@gmail.com", "password": ""})
    _returns_to_login_page(resp)


def test_valid_login_entry_login_fail(client):
    email = "a-@gmail.com"
    email2 = "abcc-@gmail.com"
    password = "validPassw0rd"
    password2 = "V3ryV4LiD$"
    garth_client = Client()

    result = _validate_login(email, password, garth_client)
    assert result is None
    result = _validate_login(email2, password2, garth_client)
    assert result is None


def test_mfa_code_get(client):
    response = client.get(MFA_PATH)
    assert response.status_code == 200
    assert b"MFA Code" in response.data
