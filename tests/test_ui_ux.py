#!/usr/bin/env python3
"""Базовые автоматические проверки UI/UX RatioT SCADA 6.41.09.

Проверяет:
- доступность Web UI и ключевых статических ресурсов;
- публичный конфиг / логин / dashboard URL;
- REST API авторизацию и базовые контексты;
- ошибки в логах сервера.
"""

import http.client
import json
import ssl
import time
import urllib.request
from pathlib import Path

BASE_HOST = "localhost"
HTTPS_PORT = 8443
HTTP_PORT = 8080
LOG_PATH = Path("C:/Program Files/RatioTScada/logs/server.log")

# Список URL, которые должны отвечать
URLS = [
    "/web/",
    "/web/static/js/dashboard-sdk.js",
    "/web/static/style/dashboard-sdk.af5eae16.css",
]


def fetch(url, use_https=True, method="GET", headers=None, data=None, timeout=10):
    port = HTTPS_PORT if use_https else HTTP_PORT
    scheme = "https" if use_https else "http"
    full = f"{scheme}://{BASE_HOST}:{port}{url}"
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(full, method=method, headers=headers or {}, data=data)
    start = time.time()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            body = resp.read()
            return resp.status, dict(resp.headers), body, time.time() - start
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read(), time.time() - start


def test_public_config():
    status, headers, body, elapsed = fetch("/web/v1/public/config")
    assert status == 200, f"public config status {status}"
    cfg = json.loads(body)
    assert cfg.get("serverVersion") == "6.41.09", f"unexpected version {cfg.get('serverVersion')}"
    assert cfg.get("customTitle") == "RatioT SCADA"
    print(f"[OK] public config: version={cfg['serverVersion']}, title={cfg['customTitle']}, time={elapsed:.3f}s")
    return cfg


def test_static_assets():
    for path in URLS:
        status, _, body, elapsed = fetch(path)
        assert status == 200, f"{path} returned {status}"
        assert len(body) > 0, f"{path} body empty"
        print(f"[OK] {path}: {len(body)} bytes, {elapsed:.3f}s")


def test_login_page():
    status, _, body, elapsed = fetch("/web/login")
    assert status == 200, f"/web/login status {status}"
    text = body.decode("utf-8", errors="ignore")
    assert '<div id="app"' in text, "login page does not contain app mount point"
    print(f"[OK] /web/login SPA shell: {len(body)} bytes, {elapsed:.3f}s")


def test_rest_auth_required():
    status, _, body, _ = fetch("/rest/v1/contexts/users.admin")
    assert status == 401, f"unauthenticated REST expected 401, got {status}"
    print("[OK] REST API requires auth (401)")


def test_rest_login():
    # Согласно документации: POST /rest/auth с JSON {"username": ..., "password": ...}
    payload = json.dumps({"username": "admin", "password": "admin"}).encode()
    headers = {"Content-Type": "application/json"}
    endpoint = "/rest/auth"
    status, _, body, elapsed = fetch(endpoint, method="POST", headers=headers, data=payload)
    print(f"[INFO] auth endpoint {endpoint}: status={status}, time={elapsed:.3f}s")
    if status in (200, 201):
        data = json.loads(body)
        print(f"[OK] authenticated via {endpoint}, token present={bool(data.get('token'))}")
        return data
    print("[WARN] could not authenticate via /rest/auth")
    return None


def test_rest_contexts_with_token():
    auth = test_rest_login()
    if not auth or "token" not in auth:
        print("[SKIP] no token, skipping authenticated context test")
        return
    headers = {"Authorization": f"Bearer {auth['token']}"}
    status, _, body, elapsed = fetch("/rest/v1/contexts/users.admin", headers=headers)
    print(f"[INFO] /rest/v1/contexts/users.admin with token: status={status}, time={elapsed:.3f}s")
    assert status == 200, f"authenticated contexts request returned {status}"
    print("[OK] authenticated REST context request works")


def test_dashboard_url():
    status, _, body, elapsed = fetch("/web/dashboards/users.admin.dashboards.default")
    assert status in (200, 302, 401), f"dashboard URL status {status}"
    print(f"[OK] dashboard direct URL status={status}, time={elapsed:.3f}s")


def test_log_errors():
    if not LOG_PATH.exists():
        print("[SKIP] server.log not found")
        return []
    text = LOG_PATH.read_text(encoding="utf-8", errors="ignore")
    errors = [line for line in text.splitlines() if " ERROR " in line or " FATAL " in line]
    print(f"[INFO] found {len(errors)} ERROR/FATAL lines in server.log")
    for line in errors[:10]:
        print(f"  {line[:200]}")
    return errors


if __name__ == "__main__":
    print("=" * 60)
    print("RatioT SCADA UI/UX automated smoke tests")
    print("=" * 60)
    test_public_config()
    test_static_assets()
    test_login_page()
    test_rest_auth_required()
    test_rest_login()
    test_rest_contexts_with_token()
    test_dashboard_url()
    test_log_errors()
    print("=" * 60)
    print("Smoke tests completed")
