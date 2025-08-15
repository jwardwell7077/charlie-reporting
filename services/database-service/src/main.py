"""Backward compatibility module.

Delegates to packaged entrypoint.
"""
from .charlie_database_service.main import main  # type: ignore

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
