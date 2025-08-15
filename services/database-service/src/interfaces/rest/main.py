"""FastAPI application for database-service.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from ...business.services.email_service import EmailService
from ...business.services.user_service import UserService
from ...config.database import DatabaseConfig
from ...config.settings import DatabaseServiceConfig
from ...infrastructure.inmemory_repository import InMemoryEmailRepository
from ...infrastructure.persistence.database import DatabaseConnection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppState:
    db: DatabaseConnection | None = None
    email_service: EmailService | None = None
    user_service: UserService | None = None


state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    config = DatabaseServiceConfig()
    DatabaseConfig.from_service_config(config)
    state.db = DatabaseConnection(config)  # type: ignore[arg-type]
    await state.db.initialize()
    # Placeholder: repository wiring pending
    state.email_service = EmailService(
        email_repository=InMemoryEmailRepository(),  # type: ignore[arg-type]
        db_connection=state.db,  # type: ignore[arg-type]
    )
    # Expose on app.state for routers
    app.state.email_service = state.email_service  # type: ignore[attr-defined]
    state.user_service = UserService(
        db_connection=state.db
    )  # type: ignore[arg-type]
    try:
        yield
    finally:
        if state.db:
            await state.db.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Charlie Reporting - Database Service API",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers imported lazily to avoid circular issues
    from .routers import emails as emails_router  # noqa: F401
    from .routers import health as health_router  # noqa: F401
    app.include_router(health_router.router, prefix="/health", tags=["Health"])
    app.include_router(
        emails_router.router, prefix="/api/v1/emails", tags=["Emails"]
    )
    # Optional placeholder routers (syntactic stubs). Import guarded so
    # early development can proceed even if modules temporarily absent.
    try:  # pragma: no cover - defensive
        from .routers import reports as reports_router  # type: ignore
        app.include_router(
            reports_router.router, prefix="/api/v1/reports", tags=["Reports"]
        )
    except Exception:  # pragma: no cover
        logger.debug("Reports router not available yet")
    try:  # pragma: no cover - defensive
        from .routers import users as users_router  # type: ignore
        app.include_router(
            users_router.router, prefix="/api/v1/users", tags=["Users"]
        )
    except Exception:  # pragma: no cover
        logger.debug("Users router not available yet")

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:  # pragma: no cover - simple glue
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "details": exc.errors(),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:  # pragma: no cover
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Request Validation Error",
                "details": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:  # pragma: no cover
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal Server Error"},
        )

    # Pre-initialize minimal in-memory email service for tests that
    # construct AsyncClient without triggering lifespan.
    if not hasattr(app.state, "email_service"):
        app.state.email_service = EmailService(  # type: ignore[attr-defined]
            email_repository=InMemoryEmailRepository(),
            db_connection=None,  # type: ignore[arg-type]
        )
    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
