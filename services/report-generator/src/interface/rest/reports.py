"""Report Generator API Routes
FastAPI routes using business services with proper layered architecture
"""
import json
import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ...business.models.report import Report, ReportSheet

# Import business services
from ...business.services.csv_transformer import CSVTransformationService
from ...business.services.excel_service import ExcelReportService

# Router instance
router = APIRouter()

# Pydantic models for API


class ReportRequest(BaseModel):
    files: list[str]
    output_format: str = "xlsx"
    template: str | None = None
    filters: dict[str, Any] | None = None


class ProcessingStatus(BaseModel):
    task_id: str
    status: str  # queued, processing, completed, failed
    progress: int
    message: str
    created_at: datetime
    completed_at: datetime | None = None
    output_file: str | None = None


class TransformationConfig(BaseModel):
    group_by: list[str]
    aggregations: dict[str, str]
    filters: dict[str, Any] | None = None
    sort_by: list[str] | None = None

# Dependencies for business services


def get_csv_transformer() -> CSVTransformationService:
    """Dependency injection for CSV transformation service"""
    return CSVTransformationService()


def get_excel_service() -> ExcelReportService:
    """Dependency injection for Excel service"""
    return ExcelReportService()

# In-memory task storage (would be database in production)
task_storage = {}


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "report - generator",
        "timestamp": datetime.now().isoformat(),
        "active_tasks": len([t for t in task_storage.values() if t.status in ["queued", "processing"]])
    }


@router.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Charlie Reporting - Report Generator",
        "version": "2.0.0",
        "architecture": "layered_microservice",
        "endpoints": {
            "health": "/health",
            "process": "/process",
            "status": "/status/{task_id}",
            "download": "/download/{task_id}",
            "transform": "/transform",
            "validate": "/validate - files",
            "list_tasks": "/tasks"
        }
    }


@router.post("/process", response_model=ProcessingStatus)
async def process_csv_files(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    csv_service: CSVTransformationService = Depends(get_csv_transformer),
    excel_service: ExcelReportService = Depends(get_excel_service)
):
    """Process CSV files and generate Excel reports using business services"""
    task_id = str(uuid.uuid4())

    # Create initial task status
    task_status = ProcessingStatus(
        task_id=task_id,
        status="queued",
        progress=0,
        message="Task queued for processing",
        created_at=datetime.now()
    )

    task_storage[task_id] = task_status

    # Start background processing
    background_tasks.add_task(
        process_files_background,
        task_id,
        request,
        csv_service,
        excel_service
    )

    return task_status


async def process_files_background(
    task_id: str,
    request: ReportRequest,
    csv_service: CSVTransformationService,
    excel_service: ExcelReportService
):
    """Background task for file processing using business services"""
    try:
        # Update status to processing
        task_storage[task_id].status = "processing"
        task_storage[task_id].message = "Starting CSV processing"
        task_storage[task_id].progress = 10

        # Create transformation rules from request
        attachment_config = {
            "ACQ.csv": {
                "columns": ["Agent", "Date", "Acquisitions", "Revenue", "Campaign"],
                "sheet_name": "Acquisitions"
            },
            "Dials.csv": {
                "columns": ["Agent", "Date", "Dials", "Connects", "Campaign"],
                "sheet_name": "Dial_Activity"
            }
        }

        rules = csv_service.create_transformation_rules(attachment_config)

        task_storage[task_id].progress = 30
        task_storage[task_id].message = "Processing CSV files"

        # Process each file using business service
        transformation_results = []
        for file_path in request.files:
            if os.path.exists(file_path):
                result = csv_service.transform_csv_file(
                    file_path=file_path,
                    rules=rules,
                    date_filter=request.filters.get('date') if request.filters else None,
                    hour_filter=request.filters.get('hour') if request.filters else None
                )
                transformation_results.append(result)

        task_storage[task_id].progress = 60
        task_storage[task_id].message = "CSV processing complete, creating report"

        # Create report domain object
        report_sheets = []
        for result in transformation_results:
            if result.success and result.transformed_data is not None:
                sheet = ReportSheet(
                    name=result.sheet_name or "Data",
                    data=result.transformed_data,
                    columns=list(result.transformed_data.columns)
                )
                report_sheets.append(sheet)

        report = Report(
            name=f"report_{task_id}",
            sheets=report_sheets,
            template=request.template or "default",
            created_at=datetime.now()
        )

        task_storage[task_id].progress = 80
        task_storage[task_id].message = "Generating Excel report"

        # Generate Excel using business service
        output_filename = f"report_{task_id}.{request.output_format}"
        excel_path = excel_service.create_excel_file(
            report=report,
            output_path=output_filename
        )

        task_storage[task_id].progress = 100
        task_storage[task_id].status = "completed"
        task_storage[task_id].message = "Report generated successfully"
        task_storage[task_id].completedat = datetime.now()
        task_storage[task_id].outputfile = output_filename

    except Exception as e:
        task_storage[task_id].status = "failed"
        task_storage[task_id].message = f"Processing failed: {str(e)}"
        task_storage[task_id].completedat = datetime.now()


@router.get("/status/{task_id}", response_model=ProcessingStatus)
async def get_processing_status(task_id: str):
    """Get processing status for a task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")

    return task_storage[task_id]


@router.get("/download/{task_id}")
async def download_report(task_id: str):
    """Download generated report"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_storage[task_id]

    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")

    if not task.output_file:
        raise HTTPException(status_code=404, detail="Output file not found")

    # In production, return actual file
    return JSONResponse({
        "download_url": f"/files/{task.output_file}",
        "file_name": task.output_file,
        "task_id": task_id,
        "message": "File ready for download"
    })


@router.post("/transform")
async def transform_csv_data(
    file: UploadFile = File(...),
    config: str | None = None,
    csv_service: CSVTransformationService = Depends(get_csv_transformer)
):
    """Transform CSV data using business service"""
    try:
        if not file.file_name or not file.file_name.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")

        # Parse transformation config
        transformconfig = None
        if config:
            try:
                config_dict = json.loads(config)
                transform_config = TransformationConfig(**config_dict)
            except (json.JSONDecodeError, ValueError) as e:
                raise HTTPException(status_code=400, detail=f"Invalid config: {str(e)}")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Create basic transformation rules
            rules = csv_service.create_transformation_rules({
                file.file_name: {
                    "columns": [],  # Will be auto - detected
                    "sheet_name": Path(file.file_name).stem
                }
            })

            # Transform using business service
            result = csv_service.transform_csv_file(
                file_path=temp_file_path,
                rules=rules
            )

            if not result.success:
                raise HTTPException(status_code=400, detail=f"Transformation failed: {result.error_message}")

            df = result.transformed_data

            # Apply additional transformations if config provided
            if transform_config and df is not None:
                # Apply filters
                if transform_config.filters:
                    for column, value in transform_config.filters.items():
                        if column in df.columns:
                            df = df[df[column] == value]

                # Apply grouping and aggregation
                if transform_config.group_by and transform_config.aggregations:
                    df = df.groupby(transform_config.group_by).agg(transform_config.aggregations).reset_index()

                # Apply sorting
                if transform_config.sort_by:
                    existingsort_cols = [col for col in transform_config.sort_by if col in df.columns]
                    if existing_sort_cols:
                        df = df.sort_values(existing_sort_cols)

            # Convert to response format
            return {
                "total_rows": len(df) if df is not None else 0,
                "columns": list(df.columns) if df is not None else [],
                "sample_data": df.head(10).to_dict('records') if df is not None else [],
                "transformation_applied": transform_config is not None,
                "message": "CSV processing completed using business service"
            }

        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transformation failed: {str(e)}")


@router.post("/validate - files")
async def validate_csv_files(
    files: list[UploadFile] = File(...),
    csv_service: CSVTransformationService = Depends(get_csv_transformer)
):
    """Validate CSV files using business service"""
    try:
        validationresults = []

        for file in files:
            if not file.file_name:
                continue

            # Save file temporarily for validation
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                content = await file.read()
                temp_file.write(content)
                tempfile_path = temp_file.name

            try:
                # Use business service for validation
                validation = csv_service.validate_csv_file(temp_file_path)
                validation_results.append({
                    "file_name": file.file_name,
                    "valid": validation.get("is_valid", False),
                    "errors": validation.get("errors", []),
                    "warnings": validation.get("warnings", []),
                    "row_count": validation.get("row_count", 0),
                    "column_count": validation.get("column_count", 0)
                })
            finally:
                # Clean up
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        # Summary statistics
        validcount = sum(1 for r in validation_results if r.get('valid', False))

        return {
            "total_files": len(validation_results),
            "valid_files": valid_count,
            "invalid_files": len(validation_results) - valid_count,
            "validation_results": validation_results,
            "overall_status": "valid" if valid_count == len(validation_results) else "has_issues"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/tasks")
async def list_tasks(status: str | None = None, limit: int = 50):
    """List all tasks with optional status filter"""
    tasks = list(task_storage.values())

    if status:
        tasks = [t for t in tasks if t.status == status]

    # Sort by creation time (newest first)
    tasks.sort(key=lambda x: x.created_at, reverse=True)

    # Limit results
    tasks = tasks[:limit]

    return {
        "tasks": tasks,
        "total": len(tasks),
        "status_filter": status
    }


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task and its associated files"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_storage[task_id]

    # Don't delete active tasks
    if task.status in ["queued", "processing"]:
        raise HTTPException(status_code=400, detail="Cannot delete active task")

    # Remove from storage
    del task_storage[task_id]

    return {"message": f"Task {task_id} deleted successfully"}


@router.get("/metrics")
async def get_service_metrics():
    """Get service performance metrics"""
    tasks = list(task_storage.values())

    totaltasks = len(tasks)
    completedtasks = len([t for t in tasks if t.status == "completed"])
    failedtasks = len([t for t in tasks if t.status == "failed"])
    activetasks = len([t for t in tasks if t.status in ["queued", "processing"]])

    metrics = {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "failed_tasks": failed_tasks,
        "active_tasks": active_tasks,
        "success_rate": completed_tasks / total_tasks if total_tasks > 0 else 0.0,
        "uptime": "service_running",
        "processed_files": completed_tasks,
        "memory_usage": "monitoring_available"
    }

    # Calculate average processing time for completed tasks
    completedtasks_with_time = [t for t in tasks if t.status == "completed" and t.completed_at]
    if completed_tasks_with_time:
        processing_times = [
            (t.completed_at - t.created_at).total_seconds()
            for t in completed_tasks_with_time
        ]
        metrics["average_processing_time"] = sum(processing_times) / len(processing_times)
    else:
        metrics["average_processing_time"] = 0.0

    return metrics
