import base64
import logging
import re
import uuid
from dataclasses import asdict
from uuid import UUID

from garth import Client, exc
from garth.auth_tokens import OAuth1Token, OAuth2Token
from garth.sso import get_oauth1_token, exchange

from backend.server.database_interface import add_new_session
from backend.server.models import SessionsDB

logger = logging.getLogger(__name__)


def _get_csrf_token(html: str) -> str:
    CSRF_RE = re.compile(r'name="_csrf"\s+value="(.+?)"')
    match = re.search(CSRF_RE, html)
    if not match:
        raise Exception("CSRF token not found")
    else:
        return match.group(1)


def _get_response_title(html: str) -> str:
    TITLE_RE = re.compile(r"<title>(.+?)</title>")
    match = TITLE_RE.search(html)
    if not match:
        raise Exception("Couldn't find title")
    return match.group(1)


def custom_sso_login(email: str, password: str, client: Client) -> str | None:
    SSO = f"https://sso.garmin.com/sso"
    SSO_EMBED = f"{SSO}/embed"
    SSO_EMBED_PARAMS = dict(
        id="gauth-widget",
        embedWidget="true",
        gauthHost=SSO,
    )
    SIGNIN_PARAMS = {
        **SSO_EMBED_PARAMS,
        **dict(
            gauthHost=SSO_EMBED,
            service=SSO_EMBED,
            source=SSO_EMBED,
            redirectAfterAccountLoginUrl=SSO_EMBED,
            redirectAfterAccountCreationUrl=SSO_EMBED,
        ),
    }
    _csrf = None
    try:
        # Set cookies
        client.get("sso", "/sso/embed", params=SSO_EMBED_PARAMS)
        # Get CSRF token for signin
        client.get("sso", "/sso/signin", params=SIGNIN_PARAMS, referrer=True)
        _csrf = _get_csrf_token(client.last_resp.text)
        client.post(
            "sso",
            "/sso/signin",
            params=SIGNIN_PARAMS,
            referrer=True,
            data=dict(username=email, password=password, embed="true", _csrf=_csrf),
        )
    except exc.GarthHTTPError:
        _csrf = None
    finally:
        return _csrf


def mfa_authentication(_csrf: str, client: Client, mfa_code: str) -> int | None:
    SSO = f"https://sso.garmin.com/sso"
    SSO_EMBED = f"{SSO}/embed"
    SSO_EMBED_PARAMS = dict(
        id="gauth-widget",
        embedWidget="true",
        gauthHost=SSO,
    )
    SIGNIN_PARAMS = {
        **SSO_EMBED_PARAMS,
        **dict(
            gauthHost=SSO_EMBED,
            service=SSO_EMBED,
            source=SSO_EMBED,
            redirectAfterAccountLoginUrl=SSO_EMBED,
            redirectAfterAccountCreationUrl=SSO_EMBED,
        ),
    }

    if not hasattr(client, "last_resp"):
        logger.info(f"No active client.")
        return 1
    else:
        # Enter MFA code
        title = _get_response_title(client.last_resp.text)
        if "MFA" not in title:
            return 2

    client.post(
        "sso",
        "/sso/verifyMFA/loginEnterMfaCode",
        params=SIGNIN_PARAMS,
        referrer=True,
        data={
            "mfa-code": mfa_code,
            "embed": "true",
            "_csrf": _csrf,
            "fromPage": "setupEnterMfaCode",
        },
    )
    try:
        TICKET_RE = re.compile(r'embed\?ticket=([^"]+)"')
        match = re.search(TICKET_RE, client.last_resp.text)
        ticket = match.group(1)
    except AttributeError:
        logger.info(f"Incorrect MFA Code entered.")
        return 3

    oauth1: OAuth1Token = get_oauth1_token(ticket, client)
    client.oauth1_token = oauth1
    oauth2: OAuth2Token = exchange(oauth1, client)
    client.oauth2_token = oauth2

    client.configure(oauth1_token=oauth1, oauth2_token=oauth2, domain=oauth1.domain)
    store_session(oauth1, oauth2)
    logger.info(f"Correct MFA Code entered.")


def store_session(Oauth1: OAuth1Token, Oauth2: OAuth2Token) -> UUID:
    session_id = uuid.uuid1()
    Oauth1.mfa_expiration_timestamp = str(Oauth1.mfa_expiration_timestamp)

    Oauth1_json = asdict(Oauth1)
    Oauth2_json = asdict(Oauth2)

    Oauth1_b64 = base64.b64encode(bytes(Oauth1_json))
    Oauth2_b64 = base64.b64encode(bytes(Oauth2_json))
    _session = SessionsDB(session_id, Oauth1_b64, Oauth2_b64)

    # {'domain': 'garmin.com', 'mfa_expiration_timestamp': '2026-02-17 01:13:59', 'mfa_token': 'MFA-43068-YdciCZWfTeh9mIdXTQol1qqjunWXqukZmb7BaKBBPMcE9x2JBt-cas', 'oauth_token': '8921269f-51a4-44fc-b86b-2bd72a824ab3', 'oauth_token_secret': 'PWYfWAQszycWwlLg7LulQCGnZhEYE4AL8AV'}
    # {'access_token': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImRpLW9hdXRoLXNpZ25lci1wcm9kLTIwMjQtcTEifQ.eyJzY29wZSI6WyJBVFBfUkVBRCIsIkFUUF9XUklURSIsIkNPTU1VTklUWV9DT1VSU0VfUkVBRCIsIkNPTU1VTklUWV9DT1VSU0VfV1JJVEUiLCJDT05ORUNUX1JFQUQiLCJDT05ORUNUX1dSSVRFIiwiRElWRV9BUElfUkVBRCIsIkRUX0NMSUVOVF9BTkFMWVRJQ1NfV1JJVEUiLCJHQVJNSU5QQVlfUkVBRCIsIkdBUk1JTlBBWV9XUklURSIsIkdDT0ZGRVJfUkVBRCIsIkdDT0ZGRVJfV1JJVEUiLCJHSFNfU0FNRCIsIkdIU19VUExPQUQiLCJHT0xGX0FQSV9SRUFEIiwiR09MRl9BUElfV1JJVEUiLCJJTlNJR0hUU19SRUFEIiwiSU5TSUdIVFNfV1JJVEUiLCJPTVRfQ0FNUEFJR05fUkVBRCIsIk9NVF9TVUJTQ1JJUFRJT05fUkVBRCIsIlBST0RVQ1RfU0VBUkNIX1JFQUQiXSwiaXNzIjoiaHR0cHM6Ly9kaWF1dGguZ2FybWluLmNvbSIsIm1mYSI6dHJ1ZSwicmV2b2NhdGlvbl9lbGlnaWJpbGl0eSI6WyJHTE9CQUxfU0lHTk9VVCJdLCJjbGllbnRfdHlwZSI6IlVOREVGSU5FRCIsImV4cCI6MTczOTg1MjA4MCwiaWF0IjoxNzM5NzU0ODQwLCJnYXJtaW5fZ3VpZCI6ImNmYjk3YzU2LTYzN2QtNDU5Yi04NTIyLTM0ZGM5M2U2MDA1YyIsImp0aSI6IjkzNjI4YjBmLWQ3MGMtNDE4OC1iNzRlLWJmMjcxMGExZTc0ZSIsImNsaWVudF9pZCI6IkdBUk1JTl9DT05ORUNUX01PQklMRV9BTkRST0lEX0RJIn0.g6iml5TguHQc1MOd0K_V1_AaHarjUbK7xtgQJcRyfGSgGwZUha6ekA9gcSekfdXBfDvYTwuMCCn2YeJ21p-zygkEMdkw4GRfPaRFJeH3wSUd6eNLGluLocNgJ_IF5Mo5xPCekv0TCxendZ6L8Ac8wMKPvEgH-zxptKrj5htLfjplZ3V0yeE7tXA1kVDRAp4un5anxoEOQSMt2VXpXNDAGE6vPk_NPHfwBv4zodkFP6li-ZbWoZzE7KG0kxhh83PXiE0tC7L5M6l9lsWeh6ZxhDFyBYEz63JKwdV7FUgZoxNJrI-Qedz4igKRpVJKRR4kuwAhYikq58Qo3mEsa37uYQ', 'expires_at': 1739852079, 'expires_in': 97239, 'jti': '93628b0f-d70c-4188-b74e-bf2710a1e74e', 'refresh_token': 'eyJyZWZyZXNoVG9rZW5WYWx1ZSI6IjIyOWRlYTI5LTI0OWMtNDQwYy05ZjU2LWRhYWE1NjBlNDJkZCIsImdhcm1pbkd1aWQiOiJjZmI5N2M1Ni02MzdkLTQ1OWItODUyMi0zNGRjOTNlNjAwNWMifQ==', 'refresh_token_expires_at': 1742346839, 'refresh_token_expires_in': 2591999, 'scope': 'COMMUNITY_COURSE_READ GARMINPAY_WRITE GOLF_API_READ ATP_READ GHS_SAMD GHS_UPLOAD INSIGHTS_READ DIVE_API_READ COMMUNITY_COURSE_WRITE CONNECT_WRITE GCOFFER_WRITE GARMINPAY_READ DT_CLIENT_ANALYTICS_WRITE GOLF_API_WRITE INSIGHTS_WRITE PRODUCT_SEARCH_READ OMT_CAMPAIGN_READ OMT_SUBSCRIPTION_READ GCOFFER_READ CONNECT_READ ATP_WRITE', 'token_type': 'Bearer'}
    # UUID('7846677f-eccc-11ef-a514-001a7dda7115')

    add_new_session(_session)
    return session_id
