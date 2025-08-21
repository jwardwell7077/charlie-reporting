#!/usr/bin/env python3
"""
Run multiple development servers (FastAPI) for local work.

Services launched (by default):
- SharePoint Simulator API      -> http://127.0.0.1:8001 (module: sharepoint_sim.server:app)
- DB Service API                -> http://127.0.0.1:8002 (module: db_service_api:app)
- Scheduler Control API         -> http://127.0.0.1:8003 (module: scheduler_api:app)

Usage examples:
  python scripts/run_dev_servers.py              # start all
  python scripts/run_dev_servers.py --sim        # only simulator
  python scripts/run_dev_servers.py --db --sched # db + scheduler

Press Ctrl-C to stop all.
"""
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, cast
import socket
from pathlib import Path
import toml


@dataclass
class Service:
    name: str
    target: str  # uvicorn module:app
    port: int


DEFAULT_HOST = "127.0.0.1"


def load_dev_config() -> Dict[str, object]:
    cfg_path = Path.cwd() / "config" / "dev_servers.toml"
    if not cfg_path.exists():
        return {}
    try:
        return toml.load(cfg_path)
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to parse {cfg_path}: {exc}", file=sys.stderr)
        raise SystemExit(1)


def build_services_from_config(cfg: Dict[str, object]) -> Tuple[Dict[str, Service], str, List[str]]:
    sec_obj = cfg.get("dev_servers")
    section = cast(Dict[str, object], sec_obj) if isinstance(sec_obj, dict) else {}

    host_val = section.get("host")
    host = host_val if isinstance(host_val, str) and host_val else DEFAULT_HOST

    sp_val = section.get("sim_port")
    sim_port = sp_val if isinstance(sp_val, int) and sp_val > 0 else 8001

    dp_val = section.get("db_port")
    db_port = dp_val if isinstance(dp_val, int) and dp_val > 0 else 8002

    tp_val = section.get("sched_port")
    sched_port = tp_val if isinstance(tp_val, int) and tp_val > 0 else 8003

    run_list_val = section.get("run")
    run_list: List[str] = []
    if isinstance(run_list_val, list):
        for item in run_list_val:
            if isinstance(item, str) and item in ("sim", "db", "sched"):
                run_list.append(item)

    services: Dict[str, Service] = {
        "sim": Service(name="SharePoint Simulator", target="sharepoint_sim.server:app", port=sim_port),
        "db": Service(name="DB Service API", target="db_service_api:app", port=db_port),
        "sched": Service(name="Scheduler API", target="scheduler_api:app", port=sched_port),
    }
    return services, host, run_list


def ensure_uvicorn_available() -> None:
    try:
        import uvicorn as _uvicorn
        _ = getattr(_uvicorn, "__version__", None)
    except Exception as exc:  # noqa: BLE001
        msg = (
            "uvicorn is required to run dev servers. Install it in your environment, e.g.:\n"
            "  pip install uvicorn[standard]\n"
            f"Current interpreter: {sys.executable}\n"
        )
        print(msg, file=sys.stderr)
        raise SystemExit(1) from exc


def check_port_free(host: str, port: int) -> bool:
    """Return True if host:port is available on TCP."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def ensure_db_path_writable() -> None:
    """Ensure the SQLite DB file path is writable in CWD."""
    db_file = Path.cwd() / "db_service.sqlite3"
    try:
        if not db_file.exists():
            # Try creating an empty file then remove (uvicorn worker will create its own)
            db_file.touch(exist_ok=True)
            db_file.unlink(missing_ok=True)
        else:
            # Try opening for append
            with db_file.open("a", encoding="utf-8"):
                pass
    except Exception as exc:  # noqa: BLE001
        print(f"DB preflight failed: Cannot write {db_file}: {exc}", file=sys.stderr)
        raise SystemExit(1)


def spawn(service: Service, host: str) -> subprocess.Popen[bytes]:
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        service.target,
        "--reload",
        "--host",
    host,
        "--port",
        str(service.port),
    ]
    env = os.environ.copy()
    env.setdefault("UVICORN_WORKERS", "1")
    print(f"Starting {service.name} on http://127.0.0.1:{service.port} ...")
    return subprocess.Popen(cmd, env=env)


def main(argv: List[str] | None = None) -> int:
    ensure_uvicorn_available()
    cfg = load_dev_config()
    SERVICES, host_from_cfg, run_from_cfg = build_services_from_config(cfg)

    parser = argparse.ArgumentParser(description="Run local dev servers")
    parser.add_argument("--sim", action="store_true", help="Run SharePoint Simulator API")
    parser.add_argument("--db", action="store_true", help="Run DB Service API")
    parser.add_argument("--sched", action="store_true", help="Run Scheduler Control API")
    parser.add_argument("--host", help="Bind host (overrides config)")
    args = parser.parse_args(argv)

    host = args.host or host_from_cfg or DEFAULT_HOST

    to_run: List[Service]
    selected = [k for k in ("sim", "db", "sched") if getattr(args, k)]
    if selected:
        to_run = [SERVICES[k] for k in selected]
    else:
        default_run = run_from_cfg or ["sim", "db", "sched"]
        to_run = [SERVICES[k] for k in default_run]

    procs: List[subprocess.Popen[bytes]] = []

    def shutdown_all(signum: int, frame: Optional[object]) -> None:
        print("\nShutting down dev servers...")
        for p in procs:
            try:
                p.terminate()
            except Exception:
                pass
        for p in procs:
            try:
                p.wait(timeout=10)
            except Exception:
                try:
                    p.kill()
                except Exception:
                    pass
        sys.exit(0)

    # Handle Ctrl-C and SIGTERM
    signal.signal(signal.SIGINT, shutdown_all)
    signal.signal(signal.SIGTERM, shutdown_all)

    # Preflight checks per selected service
    for svc in to_run:
        if not check_port_free(host, svc.port):
            print(
                f"Port {svc.port} is not available for {svc.name}.\nEnsure nothing else is running on http://{host}:{svc.port}.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        if svc is SERVICES.get("db"):
            ensure_db_path_writable()

    # Spawn
    for svc in to_run:
        procs.append(spawn(svc, host))

    try:
        # Wait for any process to exit
        while True:
            rcodes = [p.poll() for p in procs]
            if any(r is not None for r in rcodes):
                break
            signal.pause()
    except KeyboardInterrupt:
        shutdown_all(signal.SIGINT, None)  # type: ignore[arg-type]

    # If one exited, bring down the rest
    shutdown_all(signal.SIGTERM, None)  # type: ignore[arg-type]
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
