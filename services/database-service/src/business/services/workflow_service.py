"""
Workflow Business Service.
Orchestrates complex business workflows across multiple services.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from ...domain.models.email_record import EmailRecord, EmailStatus
from ...domain.models.user import User, UserRole
from ...domain.models.report import Report, ReportType, ReportStatus
from .email_service import EmailService
from .report_service import ReportService
from .user_service import UserService


class WorkflowService:
    """
    Workflow orchestration service.
    Coordinates complex business processes across multiple services.
    """
    
    def __init__(self, 
                 email_service: EmailService,
                 report_service: ReportService,
                 user_service: UserService,
                 logger: Optional[logging.Logger] = None):
        self._email_service = email_service
        self._report_service = report_service
        self._user_service = user_service
        self._logger = logger or logging.getLogger(__name__)
    
    async def process_daily_email_workflow(self, user: User) -> Dict[str, Any]:
        """
        Execute the daily email processing workflow.
        
        Args:
            user: User executing the workflow
            
        Returns:
            Workflow execution results
        """
        self._logger.info(f"Starting daily email workflow for user: {user.username}")
        
        # Check authorization
        if not await self._user_service.authorize_user(user, UserRole.USER):
            raise ValueError("User not authorized for email processing")
        
        workflow_results = {
            "started_at": datetime.now(),
            "user": user.username,
            "emails_processed": 0,
            "reports_generated": 0,
            "errors": [],
            "status": "running"
        }
        
        try:
            # Step 1: Get email statistics
            email_stats = await self._email_service.get_email_statistics()
            workflow_results["email_stats"] = email_stats
            
            # Step 2: Process any pending emails
            # In a real system, we'd get pending emails from repository
            # For demo, we'll simulate processing
            pending_count = email_stats.get("count_received", 0)
            if pending_count > 0:
                self._logger.info(f"Processing {pending_count} pending emails")
                # Simulate bulk processing
                workflow_results["emails_processed"] = pending_count
            
            # Step 3: Generate daily report
            report = await self._report_service.create_email_summary_report(
                created_by=user,
                title=f"Daily Email Summary - {datetime.now().strftime('%Y-%m-%d')}",
                description="Automated daily email processing summary",
                email_criteria={"status": "processed"}
            )
            
            # Generate the report content
            generated_report = await self._report_service.generate_report(report)
            workflow_results["reports_generated"] = 1
            workflow_results["report_id"] = str(generated_report.id)
            
            # Step 4: Archive old emails
            archived_count = await self._email_service.archive_old_emails(days_old=30)
            workflow_results["emails_archived"] = archived_count
            
            workflow_results["status"] = "completed"
            workflow_results["completed_at"] = datetime.now()
            
            self._logger.info("Daily email workflow completed successfully")
            
        except Exception as e:
            workflow_results["status"] = "failed"
            workflow_results["errors"].append(str(e))
            workflow_results["failed_at"] = datetime.now()
            self._logger.error(f"Daily email workflow failed: {e}")
            raise
        
        return workflow_results
    
    async def process_bulk_import_workflow(self, 
                                         user: User, 
                                         email_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute bulk email import workflow.
        
        Args:
            user: User executing the workflow
            email_data_list: List of email data dictionaries
            
        Returns:
            Workflow execution results
        """
        self._logger.info(f"Starting bulk import workflow for {len(email_data_list)} emails")
        
        # Check authorization for bulk operations
        if not await self._user_service.authorize_user(user, UserRole.ADMIN):
            raise ValueError("User not authorized for bulk import operations")
        
        workflow_results = {
            "started_at": datetime.now(),
            "user": user.username,
            "total_emails": len(email_data_list),
            "imported": 0,
            "failed": 0,
            "errors": [],
            "status": "running"
        }
        
        try:
            # Process emails in batches
            batch_size = 50  # Process in batches to avoid memory issues
            for i in range(0, len(email_data_list), batch_size):
                batch = email_data_list[i:i + batch_size]
                self._logger.debug(f"Processing batch {i//batch_size + 1}")
                
                for email_data in batch:
                    try:
                        await self._email_service.import_email(email_data)
                        workflow_results["imported"] += 1
                    except Exception as e:
                        workflow_results["failed"] += 1
                        workflow_results["errors"].append(f"Email {email_data.get('message_id', 'unknown')}: {str(e)}")
            
            # Generate import summary report
            if workflow_results["imported"] > 0:
                report = await self._report_service.create_email_summary_report(
                    created_by=user,
                    title=f"Bulk Import Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    description=f"Imported {workflow_results['imported']} emails",
                    email_criteria={"status": "received"}
                )
                
                generated_report = await self._report_service.generate_report(report)
                workflow_results["report_id"] = str(generated_report.id)
            
            workflow_results["status"] = "completed"
            workflow_results["completed_at"] = datetime.now()
            
            self._logger.info(f"Bulk import workflow completed: {workflow_results['imported']} imported, {workflow_results['failed']} failed")
            
        except Exception as e:
            workflow_results["status"] = "failed"
            workflow_results["errors"].append(f"Workflow error: {str(e)}")
            workflow_results["failed_at"] = datetime.now()
            self._logger.error(f"Bulk import workflow failed: {e}")
            raise
        
        return workflow_results
    
    async def process_report_generation_workflow(self, 
                                               user: User,
                                               report_type: ReportType,
                                               criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute report generation workflow.
        
        Args:
            user: User requesting the report
            report_type: Type of report to generate
            criteria: Report criteria and filters
            
        Returns:
            Workflow execution results
        """
        self._logger.info(f"Starting report generation workflow: {report_type.value}")
        
        workflow_results = {
            "started_at": datetime.now(),
            "user": user.username,
            "report_type": report_type.value,
            "status": "running"
        }
        
        try:
            # Create report based on type
            title = f"{report_type.value.title()} Report - {datetime.now().strftime('%Y-%m-%d')}"
            description = f"Generated {report_type.value} report with custom criteria"
            
            report = await self._report_service.create_email_summary_report(
                created_by=user,
                title=title,
                description=description,
                email_criteria=criteria
            )
            
            # Set the correct report type
            report.report_type = report_type
            
            # Generate the report
            generated_report = await self._report_service.generate_report(report)
            
            # Get report statistics
            stats = await self._report_service.get_report_statistics(generated_report)
            
            workflow_results.update({
                "status": "completed",
                "completed_at": datetime.now(),
                "report_id": str(generated_report.id),
                "file_path": generated_report.file_path,
                "statistics": stats
            })
            
            self._logger.info(f"Report generation workflow completed: {generated_report.id}")
            
        except Exception as e:
            workflow_results["status"] = "failed"
            workflow_results["error"] = str(e)
            workflow_results["failed_at"] = datetime.now()
            self._logger.error(f"Report generation workflow failed: {e}")
            raise
        
        return workflow_results
    
    async def process_maintenance_workflow(self, user: User) -> Dict[str, Any]:
        """
        Execute system maintenance workflow.
        
        Args:
            user: Admin user executing maintenance
            
        Returns:
            Workflow execution results
        """
        self._logger.info("Starting maintenance workflow")
        
        # Check admin authorization
        if not await self._user_service.authorize_user(user, UserRole.ADMIN):
            raise ValueError("User not authorized for maintenance operations")
        
        workflow_results = {
            "started_at": datetime.now(),
            "user": user.username,
            "tasks_completed": [],
            "status": "running"
        }
        
        try:
            # Task 1: Archive old emails (90+ days)
            archived_count = await self._email_service.archive_old_emails(days_old=90)
            workflow_results["tasks_completed"].append(f"Archived {archived_count} old emails")
            
            # Task 2: Generate system statistics
            email_stats = await self._email_service.get_email_statistics()
            workflow_results["tasks_completed"].append("Generated system statistics")
            workflow_results["system_stats"] = email_stats
            
            # Task 3: Generate maintenance report
            report = await self._report_service.create_email_summary_report(
                created_by=user,
                title=f"System Maintenance Report - {datetime.now().strftime('%Y-%m-%d')}",
                description="Automated system maintenance summary",
                email_criteria={}
            )
            
            generated_report = await self._report_service.generate_report(report)
            workflow_results["tasks_completed"].append("Generated maintenance report")
            workflow_results["report_id"] = str(generated_report.id)
            
            workflow_results["status"] = "completed"
            workflow_results["completed_at"] = datetime.now()
            
            self._logger.info("Maintenance workflow completed successfully")
            
        except Exception as e:
            workflow_results["status"] = "failed"
            workflow_results["error"] = str(e)
            workflow_results["failed_at"] = datetime.now()
            self._logger.error(f"Maintenance workflow failed: {e}")
            raise
        
        return workflow_results
