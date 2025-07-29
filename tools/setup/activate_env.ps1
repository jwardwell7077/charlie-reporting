# activate_env.ps1
# Activate the virtual environment and run commands

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Command
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPath = Join-Path $ScriptDir ".venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"

# Check if virtual environment exists
if (-not (Test-Path $PythonExe)) {
    Write-Error "Virtual environment not found at $VenvPath"
    Write-Host "Please create virtual environment first:"
    Write-Host "  python -m venv .venv"
    Write-Host "  .venv\Scripts\Activate.ps1"
    Write-Host "  pip install -r requirements.txt"
    exit 1
}

# Activate virtual environment
if (Test-Path $ActivateScript) {
    & $ActivateScript
    Write-Host "Virtual environment activated: $VenvPath" -ForegroundColor Green
} else {
    Write-Warning "Activation script not found, setting Python path directly"
    $env:PATH = "$VenvPath\Scripts;$env:PATH"
}

# Set environment variables
$env:PYTHONPATH = "$ScriptDir\src;$ScriptDir\tests"

# Load .env file if it exists
$EnvFile = Join-Path $ScriptDir ".env"
if (Test-Path $EnvFile) {
    Write-Host "Loading environment variables from .env" -ForegroundColor Blue
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "env:$name" -Value $value
            Write-Host "  Set $name" -ForegroundColor DarkGray
        }
    }
}

# Run command if provided
if ($Command.Count -eq 0) {
    Write-Host "Virtual environment ready. Python path: $PythonExe" -ForegroundColor Green
    Write-Host "You can now run Python commands or integration tests."
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  python tests/run_integration_tests.py"
    Write-Host "  python tests/check_integration_dependencies.py"
    Write-Host "  python -m pytest tests/"
} else {
    $CommandString = $Command -join " "
    Write-Host "Running: $CommandString" -ForegroundColor Yellow
    
    # Execute the command
    if ($Command[0] -eq "python") {
        & $PythonExe $Command[1..($Command.Count-1)]
    } else {
        & $Command[0] $Command[1..($Command.Count-1)]
    }
}
