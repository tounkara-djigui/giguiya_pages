import asyncio
import ipaddress
import logging
import re
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)

EMAIL_BASE_URL = "https://integrations.emergentagent.com"
RESEND_URL = "https://api.resend.com/emails"

_SHORTENERS = ("bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "goo.gl", "rebrand.ly")
_CRED_ASK = ("reply with your password", "reply with the code", "send your password", "cvv",
             "send us your password", "enter your password below", "confirm your card number",
             "your full card number", "seed phrase", "recovery phrase", "verify your card",
             "social security number", "confirm your bank details")
_HOSTISH = re.compile(r"\b(?:https?://)?((?:[a-z0-9-]+\.)+[a-z]{2,})", re.I)


def _host_ok(host: str) -> bool:
    if not host or "xn--" in host:
        return False
    try:
        ipaddress.ip_address(host)
        return False
    except ValueError:
        pass
    return not any(host == s or host.endswith("." + s) for s in _SHORTENERS)


def _same_site(shown: str, real: str) -> bool:
    return shown == real or real.endswith("." + shown) or shown.endswith("." + real)


class _EmailScan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.urls, self.anchors = set(), [], []
        self._href, self._text = None, []

    def handle_starttag(self, tag, attrs):
        self.tags.add(tag.lower())
        self.urls += [v for k, v in attrs if k.lower() in ("href", "src") and v]
        if tag.lower() == "a":
            self._href = dict((k.lower(), v) for k, v in attrs).get("href")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._href is not None:
            self.anchors.append((self._href, "".join(self._text)))
            self._href, self._text = None, []


def _check_tags(scan: "_EmailScan") -> None:
    if scan.tags & {"form", "input", "textarea", "select"}:
        raise ValueError("No forms or input fields in email (G2)")


def _check_credential_asks(subject: str, html: str) -> None:
    body = f"{subject}\n{html}".lower()
    for p in _CRED_ASK:
        if p in body:
            raise ValueError(f"Email asks the recipient for credentials: {p!r} (G2)")


def _check_url(url: str) -> None:
    low = url.strip().lower()
    if low.startswith(("mailto:", "tel:", "cid:", "#")):
        return
    if not low.startswith("https://"):
        raise ValueError(f"Email links/assets must be absolute https: {url!r} (G3)")
    parsed = urlparse(low)
    if not _host_ok(parsed.hostname or "") or parsed.username is not None:
        raise ValueError(f"Shortened, numeric-host or credential-bearing URL: {url!r} (G3)")


def _check_anchor(href: str, text: str) -> None:
    real = urlparse(href.strip().lower()).hostname or ""
    if not real:
        return
    for m in _HOSTISH.finditer(text):
        if not _same_site(m.group(1).lower(), real):
            raise ValueError(f"Anchor text {m.group(1)!r} ≠ real link host {real!r} (G3)")


def _assert_safe_email(subject: str, html: str) -> None:
    scan = _EmailScan()
    scan.feed(html)
    _check_tags(scan)
    _check_credential_asks(subject, html)
    for url in scan.urls:
        _check_url(url)
    for href, text in scan.anchors:
        _check_anchor(href, text)


def _smtp_send(to: str, subject: str, html: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((settings.EMAIL_FROM_NAME, settings.SMTP_FROM))
    msg["To"] = to
    if settings.EMAIL_REPLY_TO:
        msg["Reply-To"] = settings.EMAIL_REPLY_TO
    msg.set_content("Apri questa email con un programma che supporta HTML.")
    msg.add_alternative(html, subtype="html")
    if settings.SMTP_PORT == 465:
        server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30)
    else:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30)
        server.starttls()
    with server:
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)


async def _resend_send(to: str, subject: str, html: str) -> str | None:
    payload = {"from": formataddr((settings.EMAIL_FROM_NAME, settings.EMAIL_FROM)), "to": [to],
               "subject": subject, "html": html}
    if settings.EMAIL_REPLY_TO:
        payload["reply_to"] = settings.EMAIL_REPLY_TO
    headers = {"Authorization": f"Bearer {settings.RESEND_API_KEY}", "User-Agent": "giguiya-api/1.0"}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(RESEND_URL, json=payload, headers=headers)
    except httpx.RequestError as e:
        logger.error(f"Resend network error: {e}")
        raise HTTPException(status_code=502, detail="Invio email non riuscito")
    if resp.status_code == 429:
        raise HTTPException(status_code=429, detail="Troppi invii email, riprova tra poco")
    if resp.status_code >= 400:
        logger.error(f"Resend send failed: {resp.status_code} {resp.text}")
        raise HTTPException(status_code=502, detail="Invio email non riuscito")
    return resp.json().get("id")


async def send_email(*, to: str, subject: str, html: str) -> str | None:
    _assert_safe_email(subject, html)
    if settings.RESEND_API_KEY:
        return await _resend_send(to, subject, html)
    if settings.SMTP_HOST:
        try:
            await asyncio.to_thread(_smtp_send, to, subject, html)
        except (smtplib.SMTPException, OSError) as e:
            logger.error(f"SMTP send failed: {e}")
            raise HTTPException(status_code=502, detail="Invio email non riuscito")
        return None
    payload = {"to": [to], "subject": subject, "html": html, "from_name": settings.EMAIL_FROM_NAME}
    if settings.EMAIL_REPLY_TO:
        payload["contact_email"] = settings.EMAIL_REPLY_TO
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{EMAIL_BASE_URL}/api/v1/email/send",
                headers={"X-Email-Key": settings.EMERGENT_EMAIL_KEY},
                json=payload,
            )
        resp.raise_for_status()
        return resp.json().get("id")
    except httpx.HTTPStatusError as e:
        try:
            code = e.response.json().get("code", "")
        except ValueError:
            code = ""
        if code in ("insufficient_credits", "integration_disabled", "daily_limit_reached"):
            logger.warning(f"Email paused: {code} ({e.response.status_code}): {e.response.text}")
            raise HTTPException(status_code=503, detail="Email temporaneamente non disponibile")
        if e.response.status_code == 429:
            logger.warning(f"Email rate limited: {e.response.text}")
            raise HTTPException(status_code=429, detail="Troppi invii email, riprova tra poco")
        logger.error(f"Email send failed: {e.response.status_code} {e.response.text}")
        raise HTTPException(status_code=502, detail="Invio email non riuscito")
    except Exception as e:
        logger.error(f"Email send error: {str(e)}")
        raise HTTPException(status_code=500, detail="Invio email non riuscito")


async def try_send_email(*, to: str, subject: str, html: str) -> bool:
    for attempt in range(2):
        try:
            await send_email(to=to, subject=subject, html=html)
            return True
        except HTTPException as e:
            if e.status_code != 429 or attempt:
                return False
            await asyncio.sleep(2)
        except ValueError as e:
            logger.error(f"Email blocked by guardrail: {e}")
            return False
    return False
