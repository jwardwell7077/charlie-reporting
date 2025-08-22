# Sprint Review – Lean Reporting Pipeline (v0.4.0)

Date: TBD (Tomorrow)
Duration: 30–45 min
Owner/Facilitator: You

Objectives

- Show end-to-end value: Sim → Scheduler → Consumer → DB → Report (CSV/XLSX)
- Review what shipped in v0.4.0 and key quality gates
- Capture feedback and identify next-sprint priorities

Agenda (timeboxed)

1) Context recap (3–5m)
   - Lean architecture with REST-only simulator boundary
   - DB Service API + Report Service API
   - Scheduler + Consumer ingestion flow

2) Live demo (10–15m)
   - Option A: One-click smoke
     - Ensure venv is set up (only once):
       - python3 -m venv .venv
       - .venv/bin/pip install -r requirements-unified.txt
     - Run: bash scripts/e2e_smoke.sh
     - Expected: services healthy, data generated, ingestion complete, report produced with non-zero rows
   - Option B: VS Code tasks (if preferred)
     - Run Simulator, DB API, Report API tasks
     - Run “Run E2E Once (Sim→Sched→Cons→Report)”
     - Show “Preflight Health Check” if needed

3) What’s in v0.4.0 (5m)
   - Report Service: CSV+XLSX generate/list/download; content-types handled
   - DB ingestion hardened against schema drift (recreate on ingest)
   - Simulator REST contract clarified; generate via query params
   - E2E scripts and managed smoke runner; tasks for local runs
   - Tests green locally; improved docs and diagrams

4) Quality gates (3–5m)
   - Unit/Integration: 100% passing in local run
   - E2E smoke: passes; report rows > 0
   - Style/type checks configured; pre-commit planned next

5) Metrics and artifacts (3–5m)
   - Test count and duration (pytest)
   - E2E smoke duration and key logs (_e2e_logs/)
   - Release notes summary (v0.4.0)

6) Feedback and Q&A (5–10m)
   - Usability of one-click scripts and tasks
   - Report output needs (columns, filters, formats)
   - Data volume and performance expectations

7) Next-sprint candidates (brief)
   - CI with pre-commit, lint/type/test, e2e marker
   - Contract tests + API examples
   - Bootstrap script and Makefile
   - Port checks and improved runbook

Appendix

- Key scripts:
  - scripts/e2e_smoke.sh
  - scripts/run_e2e_once.py
  - scripts/preflight_health.py
- Services:
  - src/sharepoint_sim/server.py → :8001
  - src/db_service_api.py → :8000
  - src/report_service_api.py → :8091
- VS Code tasks: .vscode/tasks.json (Run Simulator, DB API, Report API, E2E, Preflight)
