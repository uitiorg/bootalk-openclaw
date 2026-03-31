# Sentry Triage Runbook (Pipeline Entry, Mandatory)

> This is the **first rule document** for Sentry triage.
> For every incoming Sentry hook (`created`/`unresolved`), read this file first and follow it strictly.

---

## 0) Mandatory preflight (every hook)

1. Read this file fully before classification.
2. Fetch Sentry API originals:
   - `/api/0/issues/{issue_id}/`
   - `/api/0/issues/{issue_id}/events/latest/`
3. Never classify from webhook payload only.

If required evidence is missing, do **not** close as noise.

---

## 1) Core policy

- 404/500/AuthRequired/Legacy FAIL-string are **not noise by default**.
- Environment proof first (host + release + tags + breadcrumbs).
- API-related issues must cross-check all 4 repos:
  - `~/Bootalk/frontend-monorepo`
  - `~/Bootalk/btalk2.1_backend`
  - `~/Bootalk/legacy-service`
  - `~/Bootalk/bootalk-amplify`
- If transient 여부가 불확실하면, 추가 증거를 수집한 뒤 판단한다.

---

## 2) Environment gate (hard rule)

### 2.1 Production-like environment
Treat as production-like when evidence matches host/release/runtime such as:
- `bootalk.co.kr`, `api.bootalk.co.kr`
- production release lineage
- production runtime tags/breadcrumbs

### 2.2 Development-like environment
Treat as development-like when evidence includes:
- `dev.*`, `api-dev.*`, `localhost`
- Lambda names ending `-dev`, simulator/local build tags
- staging/dev runtime indicators

### 2.3 GitHub activity policy by environment (hard)
- **Production-like issues:** GitHub activity allowed per action policy below.
- **Development-like issues:**
  - **Do NOT create GitHub PR**
  - **Do NOT create GitHub issue**
  - Keep all handling internal to triage records + Sentry state only.

This rule has priority over generic actionable flow.

---

## 3) Transient vs actionable decision gate

### A. Mark transient/duplicate only with explicit evidence
Examples:
- deploy/cache transition signatures,
- fixed lineage fingerprint match,
- expected auth/session-expiry behavior with no product regression,
- non-prod/dev-only context.

### B. Keep actionable/open when any is true
- reproducible on current production release,
- user-impacting behavior remains unhandled,
- endpoint contract mismatch unresolved,
- confidence is insufficient.

When in doubt: keep open + collect more evidence.

---

## 4) Deep verification tools (read-only only)

### 4.1 Production DB verification (optional, when needed for confidence)
If 판단 정확도를 위해 DB 검증이 필요하면:
- Credentials source: `~/.claude/credentials`
- Access method: `python3 + pymysql`
- **Read-only only**: `SELECT` queries only
- **Forbidden**: `INSERT/UPDATE/DELETE/DDL` and any write/delete operation

Rules:
1. Never print raw credentials.
2. Prefer read-only session mode before queries.
3. If write/delete seems required, do not execute; leave work to PR/GitHub issue (production issues only).

### 4.2 DynamoDB / bootalk-amplify verification
For `bootalk-amplify` or DynamoDB-related lineages:
- Use AWS CLI read queries for evidence collection.
- Correlate Lambda/AppSync/DynamoDB evidence with Sentry breadcrumbs/tags.
- No destructive AWS operation in triage flow.

---

## 5) Action policy

### 5.1 Production-like + actionable verdict (`actionable/*`)
Default required flow:
1. Implement fix in `/tmp` worktree (never repo root).
2. Commit + open PR (allowed repos only).
3. Resolve Sentry (`inNextRelease=true`; fallback `resolved(now)` if needed).
4. Record in both ledgers:
   - `memory/sentry/incidents-YYYY-MM.jsonl`
   - `memory/pr-history.md`

### 5.2 Branch targeting rule (hard)
- **Never target `main` directly.**
- Use feature branch from integration branch (default: `develop`) and PR back to integration branch.
- If `develop` is absent, use a non-main integration branch and document the reason in summary.

### 5.3 Development-like issues (hard override)
Regardless of actionable/transient classification:
- No GitHub PR creation
- No GitHub issue creation
- Allowed actions:
  - keep_open / resolve on Sentry based on evidence
  - internal records only (`incidents JSONL`, `pr-history.md`)

### 5.4 Exception flow (production-like only)
If immediate fix is unsafe/unavailable:
1. Keep issue open (or justified temporary status).
2. Create GitHub issue with evidence and next steps.
3. Record why PR was not created.

---

## 6) Repo boundaries

- PR allowed:
  - `uitiorg/frontend-monorepo`
  - `uitiorg/legacy-service`
  - `uitiorg/bootalk-amplify`
  - `uitiorg/btalk2.1_backend`
- Never PR to:
  - `uitiorg/bootalk_web`
  - `uitiorg/bootalk_app`
  - `uitiorg/bootalk_admin`

---

## 7) Worktree-first safety

- Always edit in `/tmp` worktree.
- On patch failure:
  1. re-read target file,
  2. split hunks,
  3. retry up to 3 times,
  4. if still failing, report exact blocked hunk/path/line.
- Always cleanup: `worktree remove` + `worktree prune`.

---

## 8) Required records (always)

For every investigated issue:
1. Append one-line JSON to `memory/sentry/incidents-YYYY-MM.jsonl`.
2. Append/update `memory/pr-history.md`.

`pr-history.md` must include:
- issue ID / event ID
- environment proof
- classification + rationale
- checked repos
- GitHub action status (`PR created` / `GitHub blocked by dev-policy` / `Issue created`)
- Sentry resolution action (`inNextRelease` vs `resolved(now)` fallback)

---

## 9) Final summary format

- Issue: `<issueId> (<shortId>, <project>)`
- Event: `<eventId>`
- Environment proof: `<host/release/tag/url/breadcrumb evidence>`
- Classification: `<lineageKey> | <verdict>`
- Verification: `issue/latest-event + 4repo + (DB/AWS if used)`
- Action: `<fix+PR+resolve OR keep_open/resolve + githubActivity=none(dev-policy), 기록 완료 여부>`

Write in Korean, concise and evidence-heavy.

---

## 10) Hard prohibitions

- No webhook-only classification.
- No direct writes/deletes to production DB.
- No destructive AWS operations.
- No silent skip of `pr-history.md` updates.
- No repo-root hot edits when worktree is required.
- No direct targeting of `main` branch.
- No GitHub PR/issue activity for development-like issues.
