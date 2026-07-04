---
layout: default
---
{% raw %}
# Security Audit Findings — MedMinder

**Date**: 2026-07-04 04:12
**Scope**: Full monorepo codebase audit (Python/Flask, gRPC, shell scripts, JS/HTML)
**Methodology**: Source code review, static analysis (ruff w/ bandit rules), dependency audit, secret scanning, attack surface mapping

---

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| Critical | 5 | Direct exploitation without any prerequisite conditions |
| High     | 8 | Significant risk requiring partial access or chaining |
| Medium   | 7 | Moderate risk; information disclosure or hardening gaps |
| Low      | 4 | Minor issues; best-practice violations |
| **Total** | **24** | |

---

## Attack Surface

```
┌─────────────────────────────────────────────────────────────┐
│                      ATTACK SURFACE                          │
├─────────────────────────────────────────────────────────────┤
│ 1. Web API (Flask)        ──── all endpoints unauthenticated│
│ 2. WebSockets             ──── no auth, broadcasts all data │
│ 3. gRPC (Arduino CLI)     ──── cleartext, no auth           │
│ 4. UDS Socket (BMS)       ──── world-writable (0o666)       │
│ 5. File upload            ──── no size/content validation   │
│ 6. Session cookies        ──── weak secret, no security opts│
│ 7. Subprocess cmd exec    ──── partially user-controlled    │
│ 8. Config files           ──── TOML/env var parsing         │
│ 9. Network exposure       ──── binds 0.0.0.0 by default    │
│ 10. CDN resources         ──── no SRI hash verification     │
└─────────────────────────────────────────────────────────────┘
```

---

## Critical Findings

### C1 — CWE-306: Missing Authentication — All Endpoints Public

- **CWE**: CWE-306 (Missing Authentication for Critical Function)
- **Locations**: All route files across medminder_dash/, arduino_dash/, arduino_sketch_tools/
  - medminder_dash/.../html_routes.py
  - medminder_dash/.../api_routes.py
  - arduino_sketch_tools/.../routes.py
- **Description**: There is **zero authentication** on any route. No login page, no session auth, no API keys, no bearer tokens. Every endpoint — medicine CRUD, sketch compile/upload, board management, admin panel — is fully public.
- **Impact**: Any unauthenticated attacker can:
  - Read, create, update, delete all medicine schedules
  - Upload arbitrary Arduino sketches
  - Trigger sketch compilation and upload to physical hardware
  - View/modify all system configuration
- **Remediation**: Implement mandatory authentication (Flask-Login, OAuth2 Proxy, or HTTP Basic Auth at reverse proxy). Apply `@login_required` decorators to all routes. Use separate API keys for programmatic access.

---

### C2 — CWE-798: Hardcoded Default Secret Key — Session Forgery

- **CWE**: CWE-798 (Use of Hardcoded Credentials)
- **Locations**:
  - medminder_dash/.../app.py:121
  - arduino_dash/.../app.py:80
- **Code**: `app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")`
- **Description**: The Flask secret key falls back to `"dev-secret"` if the environment variable is unset. Flask's signed session cookies can be trivially forged when the secret is known or guessable.
- **Impact**: An attacker can forge session cookies, impersonate any session state (including "admin" board selections, uploaded sketch identities), leading to privilege escalation and data manipulation.
- **Remediation**: Replace with a cryptographically random key generated at deployment. Remove the fallback default and fail hard if `FLASK_SECRET_KEY` is not set:
  ```python
  app.secret_key = os.environ["FLASK_SECRET_KEY"]
  ```
  Generate with: `python3 -c "import secrets; print(secrets.token_hex(32))"`

---

### C3 — CWE-319: Cleartext gRPC Communication — No TLS

- **CWE**: CWE-319 (Cleartext Transmission of Sensitive Information)
- **Locations**:
  - grpc_client/.../arduino_grpc/client.py:64 — `grpc.insecure_channel(self.daemon)`
  - board_manager/.../daemon_manager.py:288 — `grpc.insecure_channel(...)`
- **Description**: All gRPC connections to the Arduino CLI daemon use `grpc.insecure_channel()` with no TLS encryption or authentication. Communication occurs in cleartext, including sketch source code upload paths and board credentials.
- **Impact**: A man-in-the-middle attacker on the local network can intercept, modify, or replay all gRPC commands sent to the Arduino CLI daemon — including script compilation and firmware uploads.
- **Remediation**: Configure gRPC with TLS credentials using `grpc.secure_channel()`. Generate and deploy certificates. Use `grpc.ssl_channel_credentials()`.

---

### C4 — CWE-352: No CSRF Protection on Any Mutation Endpoint

- **CWE**: CWE-352 (Cross-Site Request Forgery)
- **Locations**: All POST/PUT/DELETE endpoints in html_routes.py and api_routes.py
- **Description**: Except for the `/medicines/generate-hpp` and `/medicines/sync-from-hpp` confirm-token mechanism, **no CSRF protection exists**. Flask-WTF's CSRF protection is not implemented. HTMX requests carry no anti-CSRF tokens.
- **Impact**: An attacker can trick a logged-in user's browser into performing any state-changing operation: adding/deleting medicines, uploading sketches, triggering firmware compiles/uploads.
- **Remediation**: Use Flask-WTF's `CSRFProtect` extension. Include CSRF tokens in all HTMX requests. For the JSON API, validate `X-CSRF-Token` headers or use `SameSite=Strict` cookies combined with strict origin validation.

---

### C5 — CWE-276: World-Writable UDS Socket

- **CWE**: CWE-276 (Incorrect Default Permissions)
- **Location**: board_manager/.../service.py:273
- **Code**: `os.chmod(path, 0o666)`
- **Description**: The Unix Domain Socket for Board Manager Service is created with **world-readable and world-writable** permissions (`0o666`). Any user on the system can connect to this socket and issue commands.
- **Impact**: Local privilege escalation — any unprivileged local user can send arbitrary pub/sub commands to the Board Manager Service, including spawning board workers, triggering compiles/uploads, and reading board state.
- **Remediation**: Restrict socket permissions to the owning user only (`0o600` or `0o770`) and ensure only the Flask application user has access. Use filesystem ACLs if multiple processes need access:
  ```python
  os.chmod(path, 0o600)
  ```

---

## High Findings

### H1 — CWE-22: Insufficient Path Traversal Protection in Sketch Deletion

- **CWE**: CWE-22 (Path Traversal)
- **Locations**:
  - medminder_dash/.../api_routes.py:441-465 — `api_sketch_delete()`
  - medminder_dash/.../html_routes.py:967-998 — `html_sketch_delete()`
- **Description**: While `os.path.normpath()` and `.startswith(norm_base)` exist, the deletion uses `os.path.dirname(norm_path)` for `shutil.rmtree()`, which could resolve to a parent directory in edge cases.
- **Remediation**: After path normalization, ensure `os.path.dirname(norm_path)` also stays within `norm_base`.

### H2 — CWE-20: IP+UserAgent as User Identity — Trivially Spoofable

- **CWE**: CWE-20 (Improper Input Validation)
- **Locations**: medminder_dash/.../api_routes.py, html_routes.py, sketch_management.py
- **Description**: Upload registry uses `(request.remote_addr, User-Agent)` as the unique user identity. Both are trivially spoofable. Users behind NAT share the same IP.
- **Remediation**: Implement proper session-based or token-based authentication.

### H3 — CWE-502: User-Controlled Upload of Arduino Sketches

- **CWE**: CWE-502 (Deserialization of Untrusted Data)
- **Locations**: medminder_dash/.../api_routes.py, html_routes.py
- **Description**: Users can upload arbitrary files compiled and uploaded to hardware. No sandboxing or content validation.
- **Remediation**: Run sketch compilation in a sandboxed environment. Implement content validation and size limits.

### H4 — CWE-918: Subprocess Injection in Daemon Management

- **CWE**: CWE-78 / CWE-918
- **Locations**: board_manager/.../daemon_manager.py, boot.py
- **Description**: Port values from config are passed to shell tools (`fuser`, `ss`, `lsof`). While currently validated, config loading could accept malformed values.
- **Remediation**: Prefer Python-native port checking (`psutil`). Strict type validation.

### H5 — CWE-862: No Authorization for API Endpoints

- **CWE**: CWE-862 (Missing Authorization)
- **Locations**: All `@app.route` definitions
- **Description**: No user roles, no permissions checks, no board ownership validation. Any user can manage any board or medicine schedule.
- **Remediation**: Implement role-based access control (RBAC) with board ownership validation.

### H6 — CWE-1004: No Session Security Flags

- **CWE**: CWE-1004 (Sensitive Cookie Without HttpOnly/Secure)
- **Locations**: Both app.py files — no session configuration
- **Remediation**: Set `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_SAMESITE="Lax"`.

### H7 — CWE-400: No Rate Limiting on API Endpoints

- **CWE**: CWE-400 (Uncontrolled Resource Consumption)
- **Locations**: All API endpoints
- **Description**: No rate limiting. Attackers can flood endpoints for DoS, disk space exhaustion, or subprocess resource exhaustion.
- **Remediation**: Implement Flask-Limiter with per-endpoint limits. Restrict upload file sizes.

---

## Medium Findings

### M1 — CWE-79: XSS in WebSocket Broadcasted HTML
- **Locations**: medminder_dash/.../pubsub.py, extension.py
- HTML constructed via string concatenation with board event data. Port values and topic names not escaped.
- **Remediation**: Use `markupsafe.escape()` on all user-controlled data before constructing HTML.

### M2 — CWE-209: Exception Information Leakage
- **Locations**: api_routes.py, html_routes.py
- Exception messages returned directly in HTTP responses, leaking internal paths and state.
- **Remediation**: Log exceptions server-side. Return generic error messages to clients.

### M3 — CWE-754: Broad Except Blocks Swallowing Errors
- **Locations**: 12+ `except Exception: pass` blocks across settings.py, board_detector.py, board_worker.py, daemon_manager.py, udev_monitor.py
- Silently ignores errors, hiding connection failures, permission errors, and data corruption.
- **Remediation**: Replace with `logger.exception()` at minimum. Only catch specific exception types.

### M4 — CWE-312: Sensitive Information in Logs
- **Locations**: board_manager/.../boot.py, daemon_manager.py
- Full command-line arguments including paths logged at INFO level.
- **Remediation**: Redact sensitive paths and arguments from logs.

### M5 — CWE-770: Unrestricted File Upload Size
- **Location**: medminder_dash/.../api_routes.py
- Sketch file uploads have no size limits.
- **Remediation**: Set `MAX_CONTENT_LENGTH` in Flask config.

### M6 — CWE-306: No WebSocket Authentication
- **Location**: medminder_dash/.../html_routes.py
- `/ws/board-events` accepts any connection without authentication.
- **Remediation**: Validate authentication when establishing WebSocket connections.

### M7 — CWE-330: Weak Confirm-Token Validation
- **Location**: medminder_dash/.../html_routes.py
- Confirm-token mechanism depends on already-weak session secret.
- **Remediation**: Fix session secret key (C2) first. Consider server-side token storage.

---

## Low Findings

### L1 — CWE-477: Use of Deprecated `datetime.utcnow()`
- **Locations**: api_routes.py, html_routes.py, app.py
- Replace with `datetime.now(timezone.utc)`.

### L2 — CWE-200: Binding to All Interfaces (0.0.0.0)
- **Locations**: `__main__.py`, `gunicorn_conf.py`
- Default to `127.0.0.1`, require explicit opt-in for external binding.

### L3 — CWE-319: No HTTPS in Production Config
- **Location**: `gunicorn_conf.py`
- TLS must be terminated at the reverse proxy; no enforcement or documentation.

### L4 — CWE-1104: Ruff Static Analysis Cleanliness Issues
- 578 linting errors including 6 security (S) errors.
- Address S-category warnings in CI.

---

## Multi-User and Internet-Facing Risk Assessment

### Current Design Assumption

The codebase was architected as a **single-user, local-network application**. This is evident from:
- No authentication or authorization mechanisms anywhere in the code
- IP+UserAgent tuple used as a user identity proxy (works for one person on one machine)
- No CSRF protection (acceptable for single-user localhost)
- HTTP-only by default (no TLS)
- World-writable UDS socket (assumes single-user workstation)
- No session security flags (assumes trusted network)

### Risk Level by Deployment Model

| Deployment Model | Risk Level | Justification |
|-----------------|------------|---------------|
| Single-user, `localhost` only | **Low** | No network attack surface exposed. The 5 critical issues (no auth, weak secret, no CSRF, world-writable socket, cleartext gRPC) are all local-only and require prior system access to exploit. |
| Single-user, LAN-only (e.g. home network, firewall) | **Medium** | All 5 critical issues become exploitable by anyone on the same network. gRPC cleartext enables MITM. No auth means any LAN user can access all endpoints. The world-writable UDS socket is still local-only. |
| Multi-user LAN (e.g. office, shared workspace) | **High** | The IP+UserAgent identity mechanism fails completely (users behind NAT share IPs). No authorization means users can access each other's data. No CSRF protection makes browser-based attacks trivially successful. |
| Internet-facing (e.g. cloud deployment, public VPN) | **Critical** | Every finding becomes directly exploitable. An attacker anywhere in the world can: delete all medicine schedules, upload malicious sketches, compile/upload to physical hardware, intercept gRPC traffic, forge session cookies, and perform CSRF-driven attacks. |

### Blast Radius by Attack Vector

| Attack Vector | Blast Radius | Worst Case |
|---------------|-------------|------------|
| Unauthenticated API | All data and hardware | Delete all medicine schedules; upload malicious firmware to all connected Arduino boards |
| Session forgery (weak secret) | All state | Impersonate any session; bypass all confirm-token mechanisms |
| Cleartext gRPC | All compiled/uploaded sketches | MITM sketch source code; inject malicious firmware during upload |
| CSRF (no tokens) | All state-changing operations | Attackers can trick a user's browser into destroying all data |
| World-writable socket | Local system | Unprivileged users control the board manager service |
| No rate limiting | System availability | Resource exhaustion DoS; disk space exhaustion from unlimited uploads |
| Broad except blocks | System integrity | Silent data corruption; undetected partial failures |
| No input validation | Sketch pipeline | Malicious sketch content sent to hardware; path traversal deleting parent directories |

### Mitigation Priority

1. **Authentication** (C1) — prerequisite for all other controls; without it no authorization, CSRF, or rate limiting can be effective
2. **Strong secret key** (C2) — fixes session integrity; required for confirm-token and CSRF token security
3. **CSRF protection** (C4) — protects browsers of users who do have sessions
4. **UDS socket permissions** (C5) — simple one-line fix with high impact
5. **gRPC TLS** (C3) — protects all inter-process communication
6. **Rate limiting** (H7) — prevents resource exhaustion
7. **Path traversal fix** (H1) — prevents directory deletion outside upload base
8. **Authentication for identity** (H2/H5) — replaces IP+UserAgent with proper user identity
9. **Session security flags** (H6) — hardening
10. **WebSocket auth** (M6) — prevents unauthenticated monitoring

---

## Top Remediation Priorities

1. Implement authentication (Flask-Login + OIDC/Basic Auth)
2. Generate strong secret key — replace dev-secret default
3. Add CSRF protection across all state-changing endpoints
4. Restrict UDS socket permissions — change `0o666` to `0o600`
5. Add TLS to gRPC channels — use `grpc.secure_channel()`
6. Fix path traversal protections in sketch deletion
7. Add rate limiting and upload size limits
8. Remove bare `except: pass` blocks — add error logging
9. Harden session cookies — set HttpOnly, Secure, SameSite
10. Add Subresource Integrity for CDN-loaded scripts

{% endraw %}
