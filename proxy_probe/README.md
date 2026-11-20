# Temporary Render proxy diagnostic

Temporary deployment-only branch `temporary/render-proxy-probe-m10b5e`. This branch does not alter `main` or any existing service.

The Dockerfile copies **only** `proxy_probe/probe.py`, with no access to any other source code, database or SMS services.

This branch is public because the existing Render GitHub integration cannot fetch the separate private TalkConnect repository. **No passwords, tokens or customer data are committed.** All access is protected by the `TALKCONNECT_PROXY_PROBE_TOKEN` Render environment variable.

Render settings: Dockerfile `proxy_probe/Dockerfile`, Docker context `.`, auto-deploy disabled, Free plan, Singapore. Remove the service after observing header handling.
