Single Entrypoint Policy
=========================

This service intentionally uses exactly one runtime entrypoint:

  src/main.py

Removed legacy / experimental mains (kept out of version control):

- main_phase1.py (prototype business logic demo)
- main_clean.py (service abstraction draft)
- main_new.py (empty scaffold)

Rationale:

- Avoid confusion about which script to run / deploy.
- Ensure logging, dependency wiring, and FastAPI app startup are centralized.
- Simplify packaging, Dockerfile CMD, and process supervision.

If you need a throwaway experiment, prefer creating it under `scripts/` or a temporary branch.

Guard Rails:

- CI/lint can optionally forbid adding new top-level files matching `main_*.py`.
- Consider adding a pre-commit hook with a simple grep check.

To launch the service (dev):
  python -m services.report-generator.src.main

Or via uvicorn (explicit):
  uvicorn services.report-generator.src.interface.app:app --reload

Do not reintroduce duplicate mains; update `main.py` if new startup behavior is required.
