"""Legacy shim kept temporarily to redirect to packaged entrypoint.

Will be removed once all scripts use `python -m outlook_relay.main`.
"""
from __future__ import annotations

import asyncio

from outlook_relay.main import main  # re-export

if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())