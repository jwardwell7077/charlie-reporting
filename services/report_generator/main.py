"""
FastAPI service for CSV data transformation and Excel report generation
Core business logic microservice for Phase 2 implementation
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
from pathlib import Path
import uuid
import asyncio
import json
from datetime import datetime
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Import our enhanced processors
from csv_processor import CSVProcessor
from excel_generator import ExcelGenerator

app = FastAPI(
    title="Charlie Reporting - Report Generator",
    description="Microservice for CSV processing and Excel report generation",
    version="2.0.0",  # Updated for Phase 2
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize processors (would load from config in production)
DEFAULT_CONFIG = {
    'attachment_rules': {
        'ACQ.csv': {
            'columns': ['Agent', 'Date', 'Acquisitions', 'Revenue', 'Campaign'],
            'sheet_name': 'Acquisitions'
        },
        'Dials.csv': {
            'columns': ['Agent', 'Date', 'Dials', 'Connects', 'Campaign'],
            'sheet_name': 'Dial_Activity'
        },
        'Productivity.csv': {
            'columns': ['Agent', 'Date', 'Hours_Worked', 'Tasks_Completed', 'Quality_Score'],
            'sheet_name': 'Productivity'
        }
    }
}

csv_processor = CSVProcessor(DEFAULT_CONFIG)
excel_generator = ExcelGenerator()

# Data models
class ReportRequest(BaseModel):
    files: List[str]
    output_format: str = "xlsx"
    template: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    
class ProcessingStatus(BaseModel):
    task_id: str
    status: str  # queued, processing, completed, failed
    progress: int
    message: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    output_file: Optional[str] = None

class TransformationConfig(BaseModel):
    group_by: List[str]
    aggregations: Dict[str, str]
    filters: Optional[Dict[str, Any]] = None
    sort_by: Optional[List[str]] = None

# In-memory task storage (would be database in production)
task_storage = {}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "report-generator",
        "timestamp": datetime.now().isoformat(),
        "active_tasks": len([t for t in task_storage.values() if t.status in ["queued", "processing"]])
    }

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Charlie Reporting - Report Generator",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "process": "/process",
            "status": "/status/{task_id}",
            "download": "/download/{task_id}",
            "transform": "/transform",
            "list_tasks": "/tasks"
        }
    }

@app.post("/process", response_model=ProcessingStatus)
async def process_csv_files(request: ReportRequest, background_tasks: BackgroundTasks):
    """Process CSV files and generate Excel reports"""
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
    background_tasks.add_task(process_files_background, task_id, request)
    
    return task_status

async def process_files_background(task_id: str, request: ReportRequest):
    """Background task for file processing using integrated business logic"""
    try:
        # Update status to processing
        task_storage[task_id].status = "processing"
        task_storage[task_id].message = "Starting CSV processing"
        task_storage[task_id].progress = 10
        
        # Process CSV files using our migrated business logic
        processed_data = await csv_processor.process_csv_files(
            file_paths=request.files,
            date_filter=request.filters.get('date') if request.filters else None,
            hour_filter=request.filters.get('hour') if request.filters else None
        )
        
        task_storage[task_id].progress = 50
        task_storage[task_id].message = "CSV processing complete, generating Excel report"
        
        # Generate Excel report using our migrated business logic
        output_filename = f"report_{task_id}.{request.output_format}"
        template = request.template if request.template else "default"
        
        excel_path = await excel_generator.generate_report(
            report_data=processed_data,
            filename=output_filename,
            template=template
        )
        
        task_storage[task_id].progress = 90
        task_storage[task_id].message = "Finalizing report"
        
        # Complete the task
        if excel_path:
            task_storage[task_id].status = "completed"
            task_storage[task_id].progress = 100
            task_storage[task_id].message = "Report generated successfully"
            task_storage[task_id].completed_at = datetime.now()
            task_storage[task_id].output_file = output_filename
        else:
            raise Exception("Failed to generate Excel report")
        
    except Exception as e:
        task_storage[task_id].status = "failed"
        task_storage[task_id].message = f"Processing failed: {str(e)}"
        task_storage[task_id].completed_at = datetime.now()

@app.get("/status/{task_id}", response_model=ProcessingStatus)
async def get_processing_status(task_id: str):
    """Get processing status for a task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_storage[task_id]

@app.get("/download/{task_id}")
async def download_report(task_id: str):
    """Download generated report"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_storage[task_id]
    
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    if not task.output_file:
        raise HTTPException(status_code=404, detail="Output file not found")
    
    # In a real implementation, return the actual file
    return JSONResponse({
        "download_url": f"/files/{task.output_file}",
        "filename": task.output_file,
        "task_id": task_id,
        "message": "File ready for download"
    })

@app.post("/transform")
async def transform_csv_data(
    file: UploadFile = File(...),
    config: Optional[str] = None  # JSON string of TransformationConfig
):
    """Transform CSV data with custom configuration using integrated business logic"""
    try:
        if not file.filename or not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        # Parse transformation config
        transform_config = None
        if config:
            try:
                config_dict = json.loads(config)
                transform_config = TransformationConfig(**config_dict)
            except (json.JSONDecodeError, ValueError) as e:
                raise HTTPException(status_code=400, detail=f"Invalid config: {str(e)}")
        
        # Save uploaded file temporarily
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Use our integrated CSV processor
        processed_data = await csv_processor.process_csv_files([temp_file_path])
        
        # Apply additional transformations if config provided
        result_data = {}
        for sheet_name, df_list in processed_data.items():
            df = df_list[0] if df_list else pd.DataFrame()
            
            if transform_config:
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
                    existing_sort_cols = [col for col in transform_config.sort_by if col in df.columns]
                    if existing_sort_cols:
                        df = df.sort_values(existing_sort_cols)
            
            result_data[sheet_name] = df
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        # Convert to response format
        response_data = {}
        total_rows = 0
        for sheet_name, df in result_data.items():
            total_rows += len(df)
            response_data[sheet_name] = {
                "rows": len(df),
                "columns": list(df.columns),
                "sample_data": df.head(10).to_dict('records')
            }
        
        return {
            "total_rows": total_rows,
            "sheets": response_data,
            "transformation_applied": transform_config is not None,
            "message": "CSV processing completed using integrated business logic"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transformation failed: {str(e)}")

@app.get("/tasks")
async def list_tasks(status: Optional[str] = None, limit: int = 50):
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

@app.delete("/tasks/{task_id}")
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

@app.get("/metrics")
async def get_service_metrics():
    """Get service performance metrics"""
    tasks = list(task_storage.values())
    
    metrics = {
        "total_tasks": len(tasks),
        "completed_tasks": len([t for t in tasks if t.status == "completed"]),
        "failed_tasks": len([t for t in tasks if t.status == "failed"]),
        "active_tasks": len([t for t in tasks if t.status in ["queued", "processing"]]),
        "success_rate": 0.0
    }
    
    if metrics["total_tasks"] > 0:
        metrics["success_rate"] = metrics["completed_tasks"] / metrics["total_tasks"]
    
    # Calculate average processing time for completed tasks
    completed_tasks = [t for t in tasks if t.status == "completed" and t.completed_at]
    if completed_tasks:
        processing_times = [
            (t.completed_at - t.created_at).total_seconds() 
            for t in completed_tasks
        ]
        metrics["average_processing_time"] = sum(processing_times) / len(processing_times)
    else:
        metrics["average_processing_time"] = 0.0
    
    return metrics

@app.post("/process-incremental")
async def process_incremental_data(
    files: List[UploadFile] = File(...),
    date_str: str = None,
    hour_str: str = None
):
    """Process incremental hourly data using integrated business logic"""
    try:
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        if not hour_str:
            hour_str = datetime.now().strftime('%H%M')
        
        # Save uploaded files temporarily
        temp_files = []
        for file in files:
            if not file.filename or not file.filename.endswith('.csv'):
                continue
            
            temp_path = f"/tmp/{file.filename}"
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            temp_files.append(temp_path)
        
        # Process using integrated business logic
        processed_data = await csv_processor.process_csv_files(
            file_paths=temp_files,
            date_filter=date_str,
            hour_filter=hour_str
        )
        
        # Generate incremental Excel report
        excel_path = await excel_generator.generate_incremental_report(
            report_data=processed_data,
            date_str=date_str,
            hour_str=hour_str
        )
        
        # Clean up temp files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
        if excel_path:
            return {
                "status": "completed",
                "message": f"Incremental report generated for {date_str} {hour_str}",
                "output_file": os.path.basename(excel_path),
                "processed_files": len(temp_files),
                "date": date_str,
                "hour": hour_str
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate incremental report")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Incremental processing failed: {str(e)}")

@app.post("/validate-files")
async def validate_csv_files(files: List[UploadFile] = File(...)):
    """Validate CSV files using integrated business logic"""
    try:
        validation_results = []
        
        for file in files:
            if not file.filename:
                continue
                
            # Save file temporarily for validation
            temp_path = f"/tmp/{file.filename}"
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Use integrated validation
            validation = await csv_processor.validate_csv_structure(temp_path)
            validation['filename'] = file.filename
            validation_results.append(validation)
            
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
        # Summary statistics
        valid_count = sum(1 for r in validation_results if r.get('valid', False))
        
        return {
            "total_files": len(validation_results),
            "valid_files": valid_count,
            "invalid_files": len(validation_results) - valid_count,
            "validation_results": validation_results,
            "overall_status": "valid" if valid_count == len(validation_results) else "has_issues"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@app.get("/processing-stats")
async def get_processing_statistics(file_paths: List[str] = None):
    """Get processing statistics using integrated business logic"""
    try:
        if not file_paths:
            # Return general stats from task storage
            return {
                "message": "No files provided for analysis",
                "active_tasks": len([t for t in task_storage.values() if t.status in ["queued", "processing"]]),
                "completed_tasks": len([t for t in task_storage.values() if t.status == "completed"]),
                "failed_tasks": len([t for t in task_storage.values() if t.status == "failed"])
            }
        
        # Get detailed stats for provided files
        stats = await csv_processor.get_processing_stats(file_paths)
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats calculation failed: {str(e)}")

@app.get("/excel-info/{filename}")
async def get_excel_file_info(filename: str):
    """Get information about generated Excel files"""
    try:
        file_info = await excel_generator.get_file_info(filename)
        return file_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File info retrieval failed: {str(e)}")

@app.post("/cleanup-old-files")
async def cleanup_old_excel_files(days_old: int = 30):
    """Clean up old Excel files"""
    try:
        cleaned_files = await excel_generator.cleanup_old_files(days_old)
        return {
            "message": f"Cleanup completed",
            "files_cleaned": len(cleaned_files),
            "cleaned_files": cleaned_files,
            "days_old_threshold": days_old
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
