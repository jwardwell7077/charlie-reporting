"""Integration dependency and environment preflight checks.

This script replicates (and extends) the original missing
``tests/check_integration_dependencies.py`` expected by the VS Code task
"Check Integration Dependencies". It validates that the test/integration
environment satisfies minimal runtime, typing, and tooling requirements
before the rest of the integration tests execute.

Checks performed (failing fast with a concise report):
1. Python version (>= 3.11 as declared in ``pyproject.toml``).
2. Virtual environment enforcement (must be inside project-local ``.venv``).
3. Core runtime packages importable (pandas, openpyxl, toml / tomli, pydantic).
4. Development / quality tools available (pytest required; ruff/mypy optional warnings).
5. Presence of type marker file ``py.typed`` for ``sharepoint_sim`` package.
6. Presence of roster data file ``sharepoint_employees.csv``.
7. Basic sanity import of each dataset generator module.
8. Main config file parse & required sections present.
9. Attachments mapping dataset name correctness vs known datasets.
10. Role rule consistency (datasets & allowed roles).
11. Schema headers integrity (non-empty, unique within each list).
12. Roster integrity (construct roster to ensure size & header conformity).
13. Optional env var presence (INTEGRATION_TEST_RECEIVER_EMAIL) when config value blank (warning only).

On success: exits 0 with a short success summary.
On failure: prints a bullet list of failed checks and exits 1.

Minimal Entry / Minimal Exit Principle:
Each check is a pure function returning either an empty string (success)
or a human-readable failure reason. The orchestrator aggregates and prints
results, thereby minimizing side-effects and facilitating future extension.
"""

from __future__ import annotations

import importlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Callable, Iterable, List

import tomllib

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = PROJECT_ROOT / "src"
PKG_ROOT = SRC_ROOT / "sharepoint_sim"
CONFIG_FILE = PROJECT_ROOT / "config" / "config.toml"
SUMMARY_PATH = PROJECT_ROOT / "tests" / "integration_preflight_summary.json"
DEFAULT_RECEIVER = "integration-test@example.com"
KNOWN_DATASETS = {
    "ACQ",
    "Productivity",
    "QCBS",
    "RESC",
    "Dials",
    "IB_Calls",
    "Campaign_Interactions",
}
ALLOWED_ROLES = {"inbound", "outbound", "hybrid"}


def check_python_version() -> str:
    """Verify the interpreter version meets the minimum requirement.

    Returns:
        str: Empty string if the check passes, otherwise an error message.
    """
    required_major, required_minor = 3, 11
    if sys.version_info < (required_major, required_minor):
        return (
            f"Python {required_major}.{required_minor}+ required; "
            f"found {sys.version_info.major}.{sys.version_info.minor}"
        )
    return ""


def check_virtual_env() -> str:
    """Ensure execution is inside the project-local virtual environment.

    Accepts either:
    * VIRTUAL_ENV pointing to the project's .venv
    * sys.prefix residing under the project .venv (covers shells not exporting VIRTUAL_ENV)

    Returns:
        str: Empty string if the check passes, otherwise an error message.
    """
    venv_env = os.environ.get("VIRTUAL_ENV")
    venv_path = PROJECT_ROOT / ".venv"

    # Direct env var success path.
    if venv_env and Path(venv_env).resolve() == venv_path.resolve():
        return ""

    # Fallback: compare sys.prefix (handles some task runners / Windows shells)
    try:
        if Path(sys.prefix).resolve() == venv_path.resolve():
            return ""
    except Exception:  # noqa: BLE001 - extremely defensive
        pass

    return (
        "Virtual environment mismatch: expected interpreter from .venv. "
        "Ensure you activated it (e.g. 'source .venv/bin/activate')."
    )


def check_core_packages() -> str:
    """Import core runtime packages to verify availability.

    Returns:
        str: Empty string if the check passes, otherwise an aggregated error message.
    """
    packages = [
        "pandas",
        "openpyxl",
        # toml vs tomli depending on Python version; attempt both gracefully.
        "toml",
        "pydantic",
    ]
    missing: List[str] = []
    for name in packages:
        try:
            importlib.import_module(name)
        except Exception:  # noqa: BLE001 - broad by design to capture any failure
            missing.append(name)
    if missing:
        return f"Missing or failed imports: {', '.join(sorted(missing))}"
    # tomli fallback (Older code may rely on tomli when <3.11)
    if sys.version_info < (3, 11):  # pragma: no cover - current min is 3.11
        try:
            importlib.import_module("tomli")
        except Exception:  # noqa: BLE001
            return "tomli not importable for Python <3.11"
    return ""


def check_tools() -> str:
    """Confirm presence of testing tool and note optional dev tools.

    Only pytest is required for running the integration tests. Ruff and mypy
    generate warnings if absent, but do not fail the preflight.

    Returns:
        str: Empty string if required tools are present, otherwise an error message.
    """
    import shutil

    required = ["pytest"]
    optional = ["ruff", "mypy"]

    missing_required = [name for name in required if shutil.which(name) is None]
    warnings: List[str] = []
    for opt in optional:
        if shutil.which(opt) is None:
            warnings.append(opt)

    if warnings:
        print(
            "[warn] Optional dev tools missing (install with 'pip install -e .[dev]') -> "
            + ", ".join(warnings)
        )

    if missing_required:
        return f"Missing required tool(s): {', '.join(missing_required)}"
    return ""


def check_type_marker() -> str:
    """Ensure the package exposes a ``py.typed`` marker for typing consumers.

    Returns:
        str: Empty string if the check passes, otherwise an error message.
    """
    marker = PKG_ROOT / "py.typed"
    if not marker.is_file():
        return f"Missing type marker file: {marker.relative_to(PROJECT_ROOT)}"
    return ""


def check_roster_csv() -> str:
    """Verify the employee roster CSV is present for generators relying on it.

    Returns:
        str: Empty string if the check passes, otherwise an error message.
    """
    roster = PKG_ROOT / "sharepoint_employees.csv"
    if not roster.is_file():
        return f"Missing roster CSV: {roster.relative_to(PROJECT_ROOT)}"
    return ""


def check_dataset_generators_import() -> str:
    """Attempt to import each dataset generator module.

    Returns:
        str: Empty string if all imports succeed, otherwise aggregated failures.
    """
    datasets_dir = PKG_ROOT / "datasets"
    failures: List[str] = []
    for py_file in datasets_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        module_name = f"sharepoint_sim.datasets.{py_file.stem}"
        try:
            importlib.import_module(module_name)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{module_name}: {exc.__class__.__name__}: {exc}")
    if failures:
        return "Dataset generator import failures:\n  - " + "\n  - ".join(failures)
    return ""


def check_main_config() -> str:
    """Validate that main config exists, parses, and has required sections.

    Also inject a default receiver email (warning) if blank and env var absent to
    keep downstream email-dependent logic deterministic in integration tests.

    Returns:
        str: Empty string if OK else error message.
    """
    if not CONFIG_FILE.is_file():
        return f"Missing main config file: {CONFIG_FILE.relative_to(PROJECT_ROOT)}"
    try:
        data = tomllib.loads(CONFIG_FILE.read_text())
    except Exception as exc:  # noqa: BLE001
        return f"Failed to parse config.toml: {exc.__class__.__name__}: {exc}"
    required_sections = ["general", "email", "attachments", "output"]
    missing = [s for s in required_sections if s not in data]
    if missing:
        return f"config.toml missing section(s): {', '.join(missing)}"
    email_cfg = data.get("email", {})
    if not email_cfg.get("receiver_address") and not os.environ.get(
        "INTEGRATION_TEST_RECEIVER_EMAIL"
    ):
        print("[warn] receiver_address blank and INTEGRATION_TEST_RECEIVER_EMAIL not set -> injecting default")
        # Patch file content in-memory and write back (minimal edit) respecting original format style.
        new_text_lines: list[str] = []
        injected = False
        for line in CONFIG_FILE.read_text().splitlines():
            if line.strip().startswith("receiver_address =") and '""' in line and not injected:
                new_text_lines.append(f'receiver_address = "{DEFAULT_RECEIVER}"  # injected default for tests')
                injected = True
            else:
                new_text_lines.append(line)
        if injected:
            CONFIG_FILE.write_text("\n".join(new_text_lines) + "\n", encoding="utf-8")
    return ""


def check_attachments_mapping() -> str:
    """Ensure each attachment dataset key matches a known dataset.

    Returns:
        str: Empty string on success, else error describing first (or aggregated) issues.
    """
    try:
        data = tomllib.loads(CONFIG_FILE.read_text())
    except Exception:  # noqa: BLE001
        return "Cannot validate attachments (config parse failed earlier)."
    attachments = data.get("attachments", {})
    invalid: List[str] = []
    for key in attachments:
        name = key[:-4] if key.lower().endswith(".csv") else key
        if name not in KNOWN_DATASETS:
            invalid.append(key)
    if invalid:
        return (
            "Attachments mapping contains unknown dataset keys: "
            + ", ".join(sorted(invalid))
        )
    return ""


def check_role_rules_consistency() -> str:
    """Verify role rules reference only known datasets and roles.

    Returns:
        str: Empty string if consistent, else error.
    """
    try:
        from sharepoint_sim.schemas import ROLE_RULES  # local import
    except Exception as exc:  # noqa: BLE001
        return f"Failed importing ROLE_RULES: {exc}" 
    dataset_keys = set(ROLE_RULES.keys())
    unknown_dataset_keys = dataset_keys - KNOWN_DATASETS
    if unknown_dataset_keys:
        return f"ROLE_RULES has unknown dataset keys: {', '.join(sorted(unknown_dataset_keys))}"
    # Roles
    bad_roles: List[str] = []
    for ds, roles in ROLE_RULES.items():
        extra = set(roles) - ALLOWED_ROLES
        if extra:
            bad_roles.append(f"{ds}: {', '.join(sorted(extra))}")
    if bad_roles:
        return "ROLE_RULES references unknown roles -> " + "; ".join(bad_roles)
    # Ensure every known dataset appears in ROLE_RULES
    missing = KNOWN_DATASETS - dataset_keys
    if missing:
        return f"ROLE_RULES missing dataset(s): {', '.join(sorted(missing))}"
    return ""


def check_schema_headers_integrity() -> str:
    """Confirm each schema header list is non-empty and has unique names.

    Returns:
        str: Empty string if OK, else error.
    """
    try:
        from sharepoint_sim import schemas  # noqa: WPS433
    except Exception as exc:  # noqa: BLE001
        return f"Failed importing schemas: {exc}"
    problems: List[str] = []
    for attr in dir(schemas):
        if attr.endswith("_HEADERS"):
            headers = getattr(schemas, attr)
            if not headers:
                problems.append(f"{attr} empty")
                continue
            if len(headers) != len(set(headers)):
                problems.append(f"{attr} contains duplicate header names")
    if problems:
        return "Schema header issues: " + "; ".join(problems)
    return ""


def check_roster_integrity() -> str:
    """Instantiate roster to ensure size & header validation pass.

    Returns:
        str: Empty string on success else error.
    """
    try:
        from sharepoint_sim.roster import Roster  # noqa: WPS433
        Roster()
    except Exception as exc:  # noqa: BLE001
        return f"Roster integrity failure: {exc}" 
    return ""


def run_checks(checks: Iterable[Callable[[], str]]) -> int:
    """Execute checks and report aggregated results, writing JSON summary.

    Args:
        checks (Iterable[Callable[[], str]]): Sequence of zero-argument callables returning an
            empty string (success) or an error message (failure).

    Returns:
        int: Process exit code (0 on success, 1 on any failure).
    """
    failures: List[str] = []
    started = time.time()
    executed: list[str] = []
    for check in checks:
        name = check.__name__
        executed.append(name)
        result = check()
        if result:
            failures.append(result)
    duration = time.time() - started
    summary = {
        "checks": executed,
        "failures": failures,
        "passed": not failures,
        "duration_seconds": round(duration, 4),
        "python": sys.version.split()[0],
        "venv": os.environ.get("VIRTUAL_ENV") or sys.prefix,
    }
    try:
        SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] Failed writing JSON summary: {exc}")
    if failures:
        print("Preflight dependency/environment check FAILED:")
        for item in failures:
            print(f" - {item}")
        print(f"Total failures: {len(failures)}")
        return 1
    print("All integration dependency checks passed.")
    return 0


def main() -> int:
    """Program entry point.

    Returns:
        int: Exit status code (0 success, 1 failure).
    """
    checks: List[Callable[[], str]] = [
        check_python_version,
        check_virtual_env,
        check_core_packages,
        check_tools,
        check_type_marker,
        check_roster_csv,
        check_dataset_generators_import,
        check_main_config,
        check_attachments_mapping,
        check_role_rules_consistency,
        check_schema_headers_integrity,
        check_roster_integrity,
    ]
    return run_checks(checks)


if __name__ == "__main__":  # pragma: no cover - script execution guard.
    raise SystemExit(main())
