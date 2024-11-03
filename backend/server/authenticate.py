import logging
import re

from garth import Client, exc, resume
from garth.auth_tokens import OAuth1Token, OAuth2Token
from garth.sso import get_oauth1_token, exchange

from backend.src.garmin_interaction import CREDS_PATH

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

    client.dump(CREDS_PATH)
    resume(CREDS_PATH)
    logger.info(f"Correct MFA Code entered.")
