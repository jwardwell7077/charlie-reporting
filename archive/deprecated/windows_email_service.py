"""
Windows Email Service - REST API Server
---------------------------------------
A Windows service that exposes Outlook email functionality via REST API.
Runs on Windows with Outlook installed, serves requests from cross - platform clients.

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
import platform

# Windows - specific imports (only available on Windows)
if platform.system() == "Windows":
    try:
        import win32com.client
        HAS_WIN32 = True
    except ImportError:
        HAS_WIN32 = False
else:
    HAS_WIN32 = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Windows Email Service",
    description="REST API for Outlook email fetching",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Configuration


class Config:
    API_KEY = os.getenv("EMAIL_SERVICE_API_KEY", "default - dev - key")
    OUTPUTDIR = Path(os.getenv("EMAIL_SERVICE_OUTPUT_DIR", "C:/EmailService / Output"))
    OUTLOOK_TIMEOUT = int(os.getenv("EMAIL_SERVICE_TIMEOUT", "30"))

    def __init__(self):
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

config = Config()

# Pydantic models


class EmailFilter(BaseModel):
    sender: Optional[List[str]] = []
    subject_contains: Optional[List[str]] = []


class AttachmentRule(BaseModel):
    columns: Optional[List[str]] = []


class FetchRequest(BaseModel):
    date: str
    start_hour: Optional[int] = None
    end_hour: Optional[int] = None
    filters: Optional[EmailFilter] = EmailFilter()
    attachment_rules: Optional[Dict[str, AttachmentRule]] = {}


class FetchRecentRequest(BaseModel):
    hours: int
    filters: Optional[EmailFilter] = EmailFilter()
    attachment_rules: Optional[Dict[str, AttachmentRule]] = {}


class FetchResponse(BaseModel):
    success: bool
    processed_emails: int
    downloaded_attachments: int
    files: List[Dict[str, Any]]
    message: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    outlook_connected: bool
    version: str
    platform: str


class AccountInfo(BaseModel):
    email: str
    display_name: str
    is_default: bool


class AccountsResponse(BaseModel):
    accounts: List[AccountInfo]

# Security dependency


def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != config.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return credentials.credentials

# Outlook service class


class OutlookService:
    def __init__(self):
        self.outlook = None
        self.namespace = None
        self.connect()

    def connect(self):
        """Connect to Outlook application"""
        if not HAS_WIN32:
            raise RuntimeError("Win32 COM not available - this service must run on Windows")

        try:
            self.outlook = win32com.client.Dispatch('Outlook.Application')
            self.namespace = self.outlook.GetNamespace('MAPI')
            logger.info("Successfully connected to Outlook")
        except Exception as e:
            logger.error(f"Failed to connect to Outlook: {e}")
            raise

    def is_connected(self) -> bool:
        """Check if Outlook connection is healthy"""
        try:
            if self.outlook and self.namespace:
                # Try to access default folder as a health check
                self.namespace.GetDefaultFolder(6)  # Inbox
                return True
        except Exception:
    pass
        return False

    def get_accounts(self) -> List[AccountInfo]:
        """Get list of available Outlook accounts"""
        try:
            accounts = []
            default_inbox = self.namespace.GetDefaultFolder(6)

            # Try to get all accounts
            session = self.namespace.Session
            if hasattr(session, 'Accounts'):
                for account in session.Accounts:
                    accounts.append(AccountInfo(
                        email=account.SmtpAddress,
                        display_name=account.DisplayName,
                        is_default=False  # We'll mark default separately
                    ))

            # Mark default account if available
            if accounts:
                accounts[0].isdefault = True

            return accounts
        except Exception as e:
            logger.error(f"Error getting accounts: {e}")
            return []

    def fetch_emails(self, request: FetchRequest) -> FetchResponse:
        """Fetch emails based on request parameters"""
        try:
            # Parse target date
            target_date = datetime.strptime(request.date, '%Y-%m-%d').date()

            # Set time boundaries
            if request.start_hour is not None and request.end_hour is not None:
                starttime = datetime.combine(target_date, datetime.min.time()).replace(hour=request.start_hour)
                endtime = datetime.combine(target_date, datetime.min.time()).replace(hour=request.end_hour, minute=59, second=59)
            else:
                starttime = datetime.combine(target_date, datetime.min.time())
                endtime = datetime.combine(target_date, datetime.max.time())

            logger.info(f"Fetching emails from {start_time} to {end_time}")

            # Get inbox and process messages
            inbox = self.namespace.GetDefaultFolder(6)
            messages = inbox.Items
            messages.Sort('[ReceivedTime]', True)

            processedemails = 0
            downloadedattachments = 0
            files = []

            for msg in messages:
                try:
                    # Get email received time
                    receivedtime = msg.ReceivedTime
                    if hasattr(received_time, 'date'):
                        receiveddt = received_time
                    else:
                        receiveddt = datetime.fromisoformat(str(received_time))

                    # Check if email is within timeframe
                    if not (start_time <= received_dt <= end_time):
                        continue

                    # Check filters
                    if not self.matches_filters(msg, request.filters):
                        continue

                    processed_emails += 1

                    # Process attachments
                    for attachment in msg.Attachments:
                        if attachment.FileName.endswith('.csv'):
                            # Check if this file matches our rules
                            if attachment.FileName in request.attachment_rules:
                                timestamp = received_dt.strftime('%Y-%m-%d_%H%M')
                                filename_base = attachment.FileName.replace('.csv', '')
                                newfilename = f"{filename_base}__{timestamp}.csv"

                                filepath = config.OUTPUT_DIR / new_filename
                                attachment.SaveAsFile(str(file_path))

                                files.append({
                                    "filename": new_filename,
                                    "size": file_path.stat().st_size,
                                    "timestamp": received_dt.isoformat()
                                })
                                downloaded_attachments += 1

                                logger.info(f"Saved attachment: {new_filename}")

                except Exception as e:
                    logger.error(f"Error processing email: {e}")
                    continue

            return FetchResponse(
                success=True,
                processed_emails=processed_emails,
                downloaded_attachments=downloaded_attachments,
                files=files,
                message=f"Successfully processed {processed_emails} emails"
            )

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def fetch_recent_emails(self, request: FetchRecentRequest) -> FetchResponse:
        """Fetch emails from recent hours"""
        cutofftime = datetime.now() - timedelta(hours=request.hours)

        # Convert to date - based request
        fetchrequest = FetchRequest(
            date=cutoff_time.strftime('%Y-%m-%d'),
            filters=request.filters,
            attachment_rules=request.attachment_rules
        )

        # For simplicity, this fetches the whole day and filters by time
        # In production, you'd want more sophisticated time filtering
        return self.fetch_emails(fetch_request)

    def matches_filters(self, msg, filters: EmailFilter) -> bool:
        """Check if email matches the provided filters"""
        try:
            # Check sender filter
            if filters.sender:
                senderemail = getattr(msg, 'SenderEmailAddress', '')
                if any(sender not in sender_email for sender in filters.sender):
                    return False

            # Check subject filter
            if filters.subject_contains:
                subject = getattr(msg, 'Subject', '')
                if any(keyword not in subject for keyword in filters.subject_contains):
                    return False

            return True
        except Exception as e:
            logger.error(f"Error checking filters: {e}")
            return False

# Initialize Outlook service
outlookservice = None


@app.on_event("startup")
async def startup_event():
    global outlook_service
    try:
        outlookservice = OutlookService()
        logger.info("Email service started successfully")
    except Exception as e:
        logger.error(f"Failed to start email service: {e}")
        outlookservice = None

# API Routes


@app.get("/", response_model=dict)
async def root():
    return {"message": "Windows Email Service API", "version": "1.0.0"}


@app.get("/api / health", response_model=HealthResponse)
async def health_check():
    outlookconnected = outlook_service is not None and outlook_service.is_connected()
    return HealthResponse(
        status="healthy" if outlook_connected else "unhealthy",
        outlook_connected=outlook_connected,
        version="1.0.0",
        platform=platform.system()
    )


@app.get("/api / status")
async def get_status():
    return {
        "current_operation": "idle",
        "last_fetch": datetime.now().isoformat(),
        "service_uptime": "N / A"  # TODO: Track actual uptime
    }


@app.get("/api / accounts", response_model=AccountsResponse)
async def get_accounts(api_key: str = Depends(verify_api_key)):
    if not outlook_service:
        raise HTTPException(status_code=503, detail="Outlook service not available")

    accounts = outlook_service.get_accounts()
    return AccountsResponse(accounts=accounts)


@app.post("/api / emails / fetch", response_model=FetchResponse)
async def fetch_emails(request: FetchRequest, api_key: str = Depends(verify_api_key)):
    if not outlook_service:
        raise HTTPException(status_code=503, detail="Outlook service not available")

    return outlook_service.fetch_emails(request)


@app.post("/api / emails / fetch - recent", response_model=FetchResponse)
async def fetch_recent_emails(request: FetchRecentRequest, api_key: str = Depends(verify_api_key)):
    if not outlook_service:
        raise HTTPException(status_code=503, detail="Outlook service not available")

    return outlook_service.fetch_recent_emails(request)


@app.get("/api / files")
async def list_files(api_key: str = Depends(verify_api_key)):
    files = []
    for file_path in config.OUTPUT_DIR.glob("*.csv"):
        stat = file_path.stat()
        files.append({
            "filename": file_path.name,
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
        })

    return {"files": files}


@app.get("/api / files/{filename}")
async def download_file(filename: str, api_key: str = Depends(verify_api_key)):
    filepath = config.OUTPUT_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='text / csv'
    )

# Development server


if __name__ == "__main__":
    logger.info("Starting Windows Email Service...")
    uvicorn.run(
        "email_service:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )