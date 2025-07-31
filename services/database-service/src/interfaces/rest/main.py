"""
FastAPI application for database service REST API.
Provides RESTful endpoints for email, user, and report management.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from ...config.settings import DatabaseServiceConfig
from ...config.database import DatabaseConfig
from ...infrastructure.persistence.database import DatabaseConnection
from ...business.services.email_service import EmailService
from ...business.services.user_service import UserService
from ...business.services.report_service import ReportService
from ...business.services.workflow_service import WorkflowService
from ...domain.repositories.email_repository import EmailRepository
from ...infrastructure.persistence.mappers import EmailRecordMapper

from .routers import emails, users, reports, health

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseServiceAPI:
    """Database Service API application wrapper"""
    
    def __init__(self, config: DatabaseServiceConfig):
        self.config = config
        self.db_connection: DatabaseConnection = None
        self.email_service: EmailService = None
        self.user_service: UserService = None
        self.report_service: ReportService = None
        self.workflow_service: WorkflowService = None
    
    async def initialize(self):
        """Initialize database connection and services"""
        try:
            # Initialize database
            db_config = DatabaseConfig(
                database_url=self.config.database_url,
                database_pool_size=self.config.database_pool_size,
                environment=getattr(self.config, 'environment', 'development')
            )
            
            self.db_connection = DatabaseConnection(db_config)
            await self.db_connection.initialize()
            
            # Initialize repositories
            email_mapper = EmailRecordMapper()
            email_repository = EmailRepository(self.db_connection, email_mapper)
            
            # Initialize business services
            self.email_service = EmailService(email_repository)
            self.user_service = UserService()  # TODO: Add user repository
            self.report_service = ReportService()  # TODO: Add report repository
            self.workflow_service = WorkflowService(
                self.email_service, 
                self.report_service
            )
            
            logger.info("Database service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            raise
    
    async def shutdown(self):
        """Cleanup resources"""
        if self.db_connection:
            await self.db_connection.close()
        logger.info("Database service shutdown complete")


# Global service instance
service: DatabaseServiceAPI = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global service
    
    # Startup
    config = DatabaseServiceConfig()
    service = DatabaseServiceAPI(config)
    await service.initialize()
    
    # Store services in app state for dependency injection
    app.state.email_service = service.email_service
    app.state.user_service = service.user_service
    app.state.report_service = service.report_service
    app.state.workflow_service = service.workflow_service
    
    yield
    
    # Shutdown
    await service.shutdown()


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="Charlie Reporting - Database Service API",
        description="REST API for email, user, and report data management",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health.router, prefix="/health", tags=["Health"])
    app.include_router(emails.router, prefix="/api/v1/emails", tags=["Emails"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
    
    # Global exception handlers
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "details": exc.errors(),
                "message": "The provided data is invalid"
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Request Validation Error",
                "details": exc.errors(),
                "message": "The request data is invalid"
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
