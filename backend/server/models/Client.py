import logging
import re

import garth
from garth import Client
from garth.auth_tokens import OAuth1Token, OAuth2Token
from garth.sso import get_oauth1_token, exchange

from backend.src.garmin_interaction import CREDS_PATH

USER_AGENT = {"User-Agent": "com.garmin.android.apps.connectmobile"}

CSRF_RE = re.compile(r'name="_csrf"\s+value="(.+?)"')
TITLE_RE = re.compile(r"<title>(.+?)</title>")
TICKET_RE = re.compile(r'embed\?ticket=([^"]+)"')
logger = logging.getLogger(__name__)


def _get_csrf_token(html: str) -> str:
    match = re.search(CSRF_RE, html)
    if not match:
        raise Exception("CSRF token not found")
    else:
        return match.group(1)


def _get_title(html: str) -> str:
    m = TITLE_RE.search(html)
    if not m:
        raise Exception("Couldn't find title")
    return m.group(1)


def custom_sso_login(email: str, password: str, client: Client) -> str:
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

    # Set cookies
    client.get("sso", "/sso/embed", params=SSO_EMBED_PARAMS)
    # Get CSRF token for signin
    client.get("sso", "/sso/signin", params=SIGNIN_PARAMS, referrer=True)
    _csrf = _get_csrf_token(client.last_resp.text)
    # Submit login form
    client.post(
        "sso",
        "/sso/signin",
        params=SIGNIN_PARAMS,
        referrer=True,
        data=dict(username=email, password=password, embed="true", _csrf=_csrf),
    )

    return _csrf


def MFA_auth(_csrf: str, client: Client, mfa_code: str):
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

    # Enter MFA code
    title = _get_title(client.last_resp.text)
    if "MFA" in title:
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

        # Parse ticket
        match = re.search(TICKET_RE, client.last_resp.text)
        ticket = match.group(1)

        oauth1: OAuth1Token = get_oauth1_token(ticket, client)
        client.oauth1_token = oauth1
        oauth2: OAuth2Token = exchange(oauth1, client)
        client.oauth2_token = oauth2

        client.dump(CREDS_PATH)
        garth.resume(CREDS_PATH)
