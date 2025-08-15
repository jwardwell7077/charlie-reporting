"""Workflow Business Service.
Orchestrates complex business workflows across multiple services.
"""

import logging
from datetime import datetime
from typing import Any

from ...domain.models.report import ReportType
from ...domain.models.user import User, UserRole
from .email_service import EmailService
from .report_service import ReportService
from .user_service import UserService


class WorkflowService:
    """Workflow orchestration service coordinating processes across layers."""

    def __init__(
        self,
        email_service: EmailService,
        report_service: ReportService,
        user_service: UserService,
        logger: logging.Logger | None = None,
    ):
        self._email_service = email_service
        self._report_service = report_service
        self._user_service = user_service
        self._logger = logger or logging.getLogger(__name__)

    async def process_daily_email_workflow(self, user: User) -> dict[str, Any]:
        """Execute the daily email processing workflow."""
        self._logger.info(
            "Starting daily email workflow for user: %s", user.username
        )

        if not await self._user_service.authorize_user(user, UserRole.USER):
            raise ValueError("User not authorized for email processing")

        workflow_results: dict[str, Any] = {
            "started_at": datetime.now(),
            "user": user.username,
            "emails_processed": 0,
            "reports_generated": 0,
            "errors": [],
            "status": "running",
        }

        try:
            email_stats = await self._email_service.get_email_statistics()
            workflow_results["email_stats"] = email_stats

            pending_count = email_stats.get("count_received", 0)
            if pending_count > 0:
                self._logger.info(
                    "Processing %d pending emails", pending_count
                )
                workflow_results["emails_processed"] = pending_count

            report = await self._report_service.create_email_summary_report(
                created_by=user,
                title=(
                    "Daily Email Summary - "
                    f"{datetime.now().strftime('%Y-%m-%d')}"
                ),
                description="Automated daily email processing summary",
                email_criteria={"status": "processed"},
            )
            generated_report = await self._report_service.generate_report(
                report
            )
            workflow_results["reports_generated"] = 1
            workflow_results["report_id"] = str(generated_report.id)

            archived_count = await self._email_service.archive_old_emails(
                days_old=30
            )
            workflow_results["emails_archived"] = archived_count

            workflow_results["status"] = "completed"
            workflow_results["completed_at"] = datetime.now()
            self._logger.info(
                "Daily email workflow completed successfully"
            )
        except Exception as e:  # noqa: BLE001
            workflow_results["status"] = "failed"
            workflow_results.setdefault("errors", []).append(str(e))
            workflow_results["failed_at"] = datetime.now()
            self._logger.error(
                "Daily email workflow failed: %s", e, exc_info=True
            )
            raise
        return workflow_results

    async def process_bulk_import_workflow(
        self, user: User, email_data_list: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Execute bulk email import workflow."""
        self._logger.info(
            "Starting bulk import workflow for %d emails", len(email_data_list)
        )

        if not await self._user_service.authorize_user(user, UserRole.ADMIN):
            raise ValueError(
                "User not authorized for bulk import operations"
            )

        workflow_results: dict[str, Any] = {
            "started_at": datetime.now(),
            "user": user.username,
            "total_emails": len(email_data_list),
            "imported": 0,
            "failed": 0,
            "errors": [],
            "status": "running",
        }

        try:
            batch_size = 50
            for i in range(0, len(email_data_list), batch_size):
                batch = email_data_list[i : i + batch_size]  # noqa: E203
                self._logger.debug(
                    "Processing batch %d", i // batch_size + 1
                )
                for email_data in batch:
                    try:
                        await self._email_service.import_email(email_data)
                        workflow_results["imported"] += 1
                    except Exception as e:  # noqa: BLE001
                        workflow_results["failed"] += 1
                        workflow_results["errors"].append(
                            "Email "
                            f"{email_data.get('message_id', 'unknown')}: "
                            f"{e}"
                        )

            if workflow_results["imported"] > 0:
                report = await (
                    self._report_service.create_email_summary_report(
                        created_by=user,
                        title=(
                            "Bulk Import Summary - "
                            f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
                        ),
                        description=(
                            f"Imported {workflow_results['imported']} emails"
                        ),
                        email_criteria={"status": "received"},
                    )
                )
                generated_report = await self._report_service.generate_report(
                    report
                )
                workflow_results["report_id"] = str(generated_report.id)

            workflow_results["status"] = "completed"
            workflow_results["completed_at"] = datetime.now()
            self._logger.info(
                "Bulk import workflow completed: %d imported, %d failed",
                workflow_results["imported"],
                workflow_results["failed"],
            )
        except Exception as e:  # noqa: BLE001
            workflow_results["status"] = "failed"
            workflow_results.setdefault("errors", []).append(
                f"Workflow error: {e}"
            )
            workflow_results["failed_at"] = datetime.now()
            self._logger.error(
                "Bulk import workflow failed: %s", e, exc_info=True
            )
            raise
        return workflow_results

    async def process_report_generation_workflow(
        self,
        user: User,
        report_type: ReportType,
        criteria: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute report generation workflow."""
        self._logger.info(
            "Starting report generation workflow: %s", report_type.value
        )

        workflow_results: dict[str, Any] = {
            "started_at": datetime.now(),
            "user": user.username,
            "report_type": report_type.value,
            "status": "running",
        }

        try:
            title = (
                f"{report_type.value.title()} Report - "
                f"{datetime.now().strftime('%Y-%m-%d')}"
            )
            description = (
                f"Generated {report_type.value} report with custom criteria"
            )
            report = await self._report_service.create_email_summary_report(
                created_by=user,
                title=title,
                description=description,
                email_criteria=criteria,
                report_type=report_type,
            )
            generated_report = await self._report_service.generate_report(
                report
            )
            stats = await self._report_service.get_report_statistics(
                generated_report
            )
            workflow_results.update(
                {
                    "status": "completed",
                    "completed_at": datetime.now(),
                    "report_id": str(generated_report.id),
                    "file_path": generated_report.file_path,
                    "statistics": stats,
                }
            )
            self._logger.info(
                "Report generation workflow completed: %s",
                generated_report.id,
            )
        except Exception as e:  # noqa: BLE001
            workflow_results["status"] = "failed"
            workflow_results["error"] = str(e)
            workflow_results["failed_at"] = datetime.now()
            self._logger.error(
                "Report generation workflow failed: %s", e, exc_info=True
            )
            raise
        return workflow_results

    async def process_maintenance_workflow(
        self, user: User
    ) -> dict[str, Any]:
        """Execute system maintenance workflow."""
        self._logger.info("Starting maintenance workflow")

        if not await self._user_service.authorize_user(user, UserRole.ADMIN):
            raise ValueError(
                "User not authorized for maintenance operations"
            )

        workflow_results: dict[str, Any] = {
            "started_at": datetime.now(),
            "user": user.username,
            "tasks_completed": [],
            "status": "running",
        }

        try:
            archived_count = await self._email_service.archive_old_emails(
                days_old=90
            )
            workflow_results["tasks_completed"].append(
                f"Archived {archived_count} old emails"
            )

            email_stats = await self._email_service.get_email_statistics()
            workflow_results["tasks_completed"].append(
                "Generated system statistics"
            )
            workflow_results["system_stats"] = email_stats

            report = await self._report_service.create_email_summary_report(
                created_by=user,
                title=(
                    "System Maintenance Report - "
                    f"{datetime.now().strftime('%Y-%m-%d')}"
                ),
                description="Automated system maintenance summary",
                email_criteria={},
            )
            generated_report = await self._report_service.generate_report(
                report
            )
            workflow_results["tasks_completed"].append(
                "Generated maintenance report"
            )
            workflow_results["report_id"] = str(generated_report.id)

            workflow_results["status"] = "completed"
            workflow_results["completed_at"] = datetime.now()
            self._logger.info(
                "Maintenance workflow completed successfully"
            )
        except Exception as e:  # noqa: BLE001
            workflow_results["status"] = "failed"
            workflow_results["error"] = str(e)
            workflow_results["failed_at"] = datetime.now()
            self._logger.error(
                "Maintenance workflow failed: %s", e, exc_info=True
            )
            raise
        return workflow_results
