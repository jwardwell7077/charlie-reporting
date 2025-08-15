# Variable Naming Standards for Report-Generator Service

## Overview

This document defines the variable naming conventions for the report-generator service to ensure consistency, readability, and PEP 8 compliance.

## Core Principles

1. **snake_case for all variables, functions, and methods**
2. **PascalCase for classes**
3. **UPPER_CASE for constants**
4. **Descriptive names over abbreviations**
5. **Consistent naming patterns**

## Variable Naming Rules

### 1. Basic Variables

- Use `snake_case` for all variable names
- Use descriptive names that clearly indicate purpose
- Avoid single letters except for loop counters

```python
# ✅ CORRECT
csv_files = []
transformation_results = []
processing_time = 15.5
user_config = {}
file_path = Path("data.csv")

# ❌ INCORRECT
csvfiles = []
transformationresults = []
processingtime = 15.5
userconfig = {}
filepath = Path("data.csv")
```

### 2. File and Path Variables

```python
# ✅ CORRECT
input_file_path = Path("input.csv")
output_directory = Path("output/")
temp_file_name = "temp_data.csv"
archive_path = Path("archive/")
excel_file_name = "report.xlsx"

# ❌ INCORRECT
inputfilepath = Path("input.csv")
outputdirectory = Path("output/")
tempfilename = "temp_data.csv"
archivepath = Path("archive/")
excelfilename = "report.xlsx"
```

### 3. Collection Variables

```python
# ✅ CORRECT
discovered_files = []
matched_files = []
failed_files = []
transformation_results = []
error_messages = []
config_settings = {}
archived_files = []

# ❌ INCORRECT
discoveredfiles = []
matchedfiles = []
failedfiles = []
transformationresults = []
errormessages = []
configsettings = {}
archivedfiles = []
```

### 4. Time and Date Variables

```python
# ✅ CORRECT
processing_time = 15.5
start_time = time.time()
end_time = time.time()
created_at = datetime.now()
completed_at = datetime.now()
processing_duration = 30.2

# ❌ INCORRECT
processingtime = 15.5
starttime = time.time()
endtime = time.time()
createdat = datetime.now()
completedat = datetime.now()
processingduration = 30.2
```

### 5. Configuration Variables

```python
# ✅ CORRECT
config_dict = {}
transform_config = TransformationConfig()
excel_config = {}
database_config = {}
logging_config = {}

# ❌ INCORRECT
configdict = {}
transformconfig = TransformationConfig()
excelconfig = {}
databaseconfig = {}
loggingconfig = {}
```

### 6. ID and Reference Variables

```python
# ✅ CORRECT
task_id = str(uuid.uuid4())
correlation_id = "req-123"
request_id = "req-456"
file_id = "file-789"
user_id = "user-101"

# ❌ INCORRECT
taskid = str(uuid.uuid4())
correlationid = "req-123"
requestid = "req-456"
fileid = "file-789"
userid = "user-101"
```

### 7. Status and Result Variables

```python
# ✅ CORRECT
task_status = "completed"
processing_result = ProcessingResult()
validation_result = {}
success_count = 5
failure_count = 2
error_message = "Processing failed"

# ❌ INCORRECT
taskstatus = "completed"
processingresult = ProcessingResult()
validationresult = {}
successcount = 5
failurecount = 2
errormessage = "Processing failed"
```

### 8. Service and Component Variables

```python
# ✅ CORRECT
csv_service = CSVTransformationService()
excel_service = ExcelReportService()
file_manager = FileManager()
config_manager = ConfigManager()
metrics_collector = MetricsCollector()

# ❌ INCORRECT
csvservice = CSVTransformationService()
excelservice = ExcelReportService()
filemanager = FileManager()
configmanager = ConfigManager()
metricscollector = MetricsCollector()
```

## Class Naming Rules

### 1. Class Names (PascalCase)

```python
# ✅ CORRECT
class ReportProcessingService:
class CSVTransformationService:
class ExcelReportService:
class ConfigManagerImpl:
class StructuredLoggerImpl:

# ❌ INCORRECT
class reportprocessingservice:
class csvtransformationservice:
class excelreportservice:
class configmanagerimpl:
class structuredloggerimpl:
```

### 2. Interface Names

```python
# ✅ CORRECT
class IConfigManager:
class ILogger:
class IMetricsCollector:
class IDirectoryProcessor:
class ICSVTransformer:

# ❌ INCORRECT
class iconfigmanager:
class ilogger:
class imetricscollector:
class idirectoryprocessor:
class icsvtransformer:
```

## Function and Method Naming

### 1. Function Names (snake_case)

```python
# ✅ CORRECT
def process_csv_files():
def transform_data():
def generate_excel_report():
def validate_configuration():
def archive_processed_files():

# ❌ INCORRECT
def processCsvFiles():
def transformData():
def generateExcelReport():
def validateConfiguration():
def archiveProcessedFiles():
```

### 2. Async Function Names

```python
# ✅ CORRECT
async def process_directory():
async def transform_csv_file():
async def generate_report():
async def save_excel_file():

# ❌ INCORRECT
async def processDirectory():
async def transformCsvFile():
async def generateReport():
async def saveExcelFile():
```

## Constants

### 1. Module-Level Constants (UPPER_CASE)

```python
# ✅ CORRECT
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
DEFAULT_TIMEOUT = 30
SUPPORTED_FORMATS = ["csv", "xlsx"]
ERROR_RETRY_COUNT = 3

# ❌ INCORRECT
max_file_size = 100 * 1024 * 1024
default_timeout = 30
supported_formats = ["csv", "xlsx"]
error_retry_count = 3
```

## Common Patterns to Fix

### 1. Concatenated Names → Underscore Names

```python
# ❌ INCORRECT → ✅ CORRECT
csvfiles → csv_files
configdict → config_dict
processingtime → processing_time
taskid → task_id
errorcount → error_count
successrate → success_rate
archivepath → archive_path
outputfile → output_file
inputdata → input_data
resultset → result_set
```

### 2. Camel Case → Snake Case

```python
# ❌ INCORRECT → ✅ CORRECT
fileName → file_name
filePath → file_path
configData → config_data
errorMessage → error_message
startTime → start_time
endTime → end_time
```

## Documentation Integration

### 1. Add to .copilot-context.md

```markdown
## Variable Naming Standards
- All variables use snake_case (e.g., csv_files, processing_time)
- Classes use PascalCase (e.g., ReportProcessingService)
- Constants use UPPER_CASE (e.g., MAX_FILE_SIZE)
- See docs/NAMING_STANDARDS.md for complete guidelines
```

### 2. Code Review Checklist

- [ ] All variables use snake_case
- [ ] No concatenated variable names (e.g., csvfiles)
- [ ] Class names use PascalCase
- [ ] Function names use snake_case
- [ ] Constants use UPPER_CASE

## Tools and Validation

### 1. Flake8 Configuration

```ini
[flake8]
# Variable naming is enforced by our standards
# Focus on F821 (undefined name) and F841 (unused variable)
```

### 2. Automated Checks

Run this command to find naming violations:

```bash
flake8 --config=.flake8 --ignore=C901 . | grep -E "F821|F841"
```

## Migration Strategy

1. **Phase 1**: Fix F821/F841 violations (undefined/unused variables)
2. **Phase 2**: Standardize concatenated names to snake_case
3. **Phase 3**: Validate all new code follows standards
4. **Phase 4**: Add pre-commit hooks for enforcement

## Examples by File Type

### Business Logic Files

```python
# services/csv_transformer.py
transformation_config = TransformationConfig()
input_file_path = Path("data.csv")
processing_results = []
```

### Infrastructure Files

```python
# infrastructure/config/config_manager.py
config_cache = {}
csv_rules_cache = {}
config_file_path = Path("config.toml")
```

### API Files

```python
# interface/rest/reports.py
task_storage = {}
processing_request = ProcessingRequest()
background_tasks = BackgroundTasks()
```

This standard ensures consistency, readability, and PEP 8 compliance across the entire report-generator service.
