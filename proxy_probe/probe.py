"""Isolated, opt-in Render proxy-header diagnostic (NO TalkConnect auth/DB).

Never import this app into talkconnect_api.main or production_auth_routes.
Run in a separate, temporary service only. No real IPs or headers are returned.
"""
from __future__ import annotations

import hashlib
import hmac
import ipaddress
import os
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Request, Response

app = FastAPI(
    title="Temporary TalkConnect Proxy Diagnostic",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

SPOOF = "203.0.113.77"  # IANA TEST-NET-3; never a real internet client.


def _tag(raw: str | None, secret: bytes) -> Optional[str]:
    if not raw:
        return None
    try:
        # No port parsing or permissive fallback; malformed values are ignored.
        normalized = ipaddress.ip_address(raw.strip()).compressed
    except ValueError:
        return None
    return hmac.new(secret, normalized.encode("ascii"), hashlib.sha256).hexdigest()[:12]


@app.middleware("http")
async def prevent_caching(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response


@app.get("/health")
def health():
    return {"status": "ok", "mode": "isolated-proxy-diagnostic", "real_auth": False}


@app.get("/probe")
def probe(request: Request, response: Response, x_probe_token: str | None = Header(default=None)):
    secret_text = os.getenv("TALKCONNECT_PROXY_PROBE_TOKEN", "")
    if len(secret_text.encode("utf-8")) < 32:
        raise HTTPException(404, "Not found")
    if not x_probe_token or not hmac.compare_digest(x_probe_token, secret_text):
        raise HTTPException(401, "Unauthorized")

    secret = secret_text.encode("utf-8")
    peer_raw = request.client.host if request.client else None
    # Preserve all repeated XFF header entries for diagnostics. Limit work.
    xff_values = request.headers.getlist("x-forwarded-for")
    full_xff = ",".join(xff_values)
    if len(full_xff) > 2048:
        raise HTTPException(400, "Forwarding header too long")
    hops = [item.strip() for item in full_xff.split(",") if item.strip()]
    if len(hops) > 12:
        raise HTTPException(400, "Forwarding chain too long")

    cf_raw = request.headers.get("cf-connecting-ip")
    peer = _tag(peer_raw, secret)
    first = _tag(hops[0], secret) if hops else None
    last = _tag(hops[-1], secret) if hops else None
    cf = _tag(cf_raw, secret)
    spoof = _tag(SPOOF, secret)
    # Keyed tags allow comparing requests without exposing personal IPs.
    return {
        "mode": "diagnostic-only",
        "asgi_peer_tag": peer,
        "xff_hop_count": len(hops),
        "xff_first_tag": first,
        "xff_last_tag": last,
        "cf_connecting_ip_present": cf_raw is not None,
        "cf_connecting_ip_tag": cf,
        "xff_first_is_reserved_spoof": bool(first and first == spoof),
        "xff_last_is_reserved_spoof": bool(last and last == spoof),
        "cf_is_reserved_spoof": bool(cf and cf == spoof),
        "cf_equals_xff_first": bool(cf and first and cf == first),
        "cf_equals_xff_last": bool(cf and last and cf == last),
        "raw_address_returned": False,
    }
