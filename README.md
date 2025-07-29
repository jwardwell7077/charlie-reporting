# Charlie Reporting

A modern, enterprise-grade microservices platform for email-based CSV data processing and Excel report generation. Transforming from Windows desktop automation to production-ready distributed architecture.

## 🚀 Project Status: Phase 1 Complete ✅

**Current Phase**: Testing & API Framework (Phase 2)  
**Overall Progress**: Foundation established, business logic implemented, moving to full microservices API implementation

### **Recent Achievements**

- ✅ **Phase 1 Business Logic**: Complete CSV transformation and Excel report generation services
- ✅ **WSL Development Environment**: Permanent setup with 80+ enterprise packages  
- ✅ **Microservices Architecture**: Service structure established with clean separation of concerns
- ✅ **VS Code Integration**: Optimized workspace with automated development tasks

## 📚 Documentation & Project Wiki

### **🏃‍♂️ [Sprint Reviews & Progress Tracking](/docs/sprint-reviews/)**

- **[Latest: Phase 1 Review & Phase 2 Planning](/docs/sprint-reviews/2025-07-28-phase1-review.md)** *(July 28, 2025)*
- Regular sprint retrospectives with technical achievements and learning outcomes
- Comprehensive project milestone tracking and decision documentation

### **📋 [Project Wiki & Milestones](/docs/project-wiki/)**

- **[Project Overview & Navigation](/docs/project-wiki/README.md)**: Complete documentation system
- **[Phase Tracking & Success Metrics](/docs/project-wiki/milestones.md)**: Detailed milestone progress
- **[Architecture Documentation](/docs/project-wiki/README.md#architecture-docs)**: Technical design and patterns

## 🏗️ Architecture Overview

### **Microservices Design** *(5 Services)*

```
┌──────────────────┐    ┌────────────────────┐    ┌────────────────────┐
│ Outlook Relay    │────│    Database        │────│  Report Generator  │
│ Service (8080)   │    │   Service (8081)   │    │   Service (8083)   │
└──────────────────┘    └────────────────────┘    └────────────────────┘
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
                ┌─────────────────────────────────┐
                │        Scheduler Service        │
                │          (8082)                 │
                └─────────────────────────────────┘
                                  │
                ┌─────────────────────────────────┐
                │        Email Service            │
                │          (8084)                 │
                └─────────────────────────────────┘
```

### **Technology Stack**

- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic
- **Testing**: pytest, coverage, black, flake8
- **Development**: WSL2, VS Code, automated task workflow
- **Deployment**: Docker, Docker Compose → Kubernetes (planned)
- **Monitoring**: Prometheus, Grafana (planned)

## Features

- **Enterprise Microservices Architecture**: 5 independent services with REST APIs
- **Production-Ready Patterns**: Health checks, monitoring, error handling, retry logic
- **Developer Experience**: Comprehensive VS Code integration with automated workflows
- **Cross-Platform**: WSL2 development with Windows Outlook integration
- **Comprehensive Testing**: pytest framework with coverage reporting
- **Modern Configuration**: TOML-based config with environment-specific settings

## Authors & Credits

- Jonathan Wardwell
- GitHub Copilot (AI code assistant)
- Prompt inspiration: GPT-4o

## License

MIT License (see LICENSE file)

## Quick Start

### **Development Environment Setup**

```bash
# Clone and setup (WSL2/Linux recommended)
git clone https://github.com/jwardwell7077/charlie-reporting.git
cd charlie-reporting

# Create virtual environment (WSL2/Linux paths)
python -m venv .venv
source .venv/bin/activate  # Linux/WSL2
# .venv\Scripts\activate   # Windows (if needed)

# Install all dependencies
pip install -r requirements-unified.txt
```

### **VS Code Development Workflow**

The project includes comprehensive VS Code integration with automated tasks:

```bash
# Available VS Code Tasks (Ctrl+Shift+P → "Tasks: Run Task")
1. "Install Requirements"           # Install/update all dependencies
2. "Run Integration Tests"          # Execute full test suite
3. "Run Unit Tests (pytest)"       # Run pytest with coverage
4. "Test Report Generator Phase 1" # Validate Phase 1 business logic
5. "Run Outlook Relay Service"     # Start email service (Port 8080)
6. "Run Report Generator Service"   # Start report service (Port 8083)
7. "Check Dependencies"             # Validate environment setup
8. "Format Code (Black)"           # Auto-format all Python code
```

### **Phase 1 Business Logic Demo**

```bash
# Run Phase 1 implementation demo
python services/report-generator/src/main_phase1.py

# Or use VS Code task: "Test Report Generator Phase 1"
```

### **Testing & Quality**

```bash
# Run comprehensive test suite
python -m pytest -v --tb=short tests/

# Check code coverage
python -m pytest --cov=services --cov-report=html

# Format code
python -m black .

# Or use VS Code tasks for all quality checks
```

## Project Structure

```
charlie-reporting/
├── services/                    # 🏗️ Microservices architecture
│   ├── outlook-relay/          # Email fetching and sending service
│   ├── database-service/       # Data storage and query service  
│   ├── scheduler-service/      # Job scheduling and orchestration
│   ├── report-generator/       # ✅ Phase 1 complete: Excel report generation
│   ├── email-service/          # Outbound email templating service
│   └── shared/                 # Common utilities and base classes
├── .vscode/                    # ✅ WSL-optimized development configuration
│   ├── settings.json           # Python interpreter and workspace settings
│   ├── tasks.json              # 8 automated development tasks
│   └── launch.json             # 5 debug configurations
├── tests/                      # 🧪 Comprehensive test suite (pytest)
├── docs/                       # 📚 Project wiki and documentation
│   ├── sprint-reviews/         # Regular progress tracking
│   └── project-wiki/           # Architecture and milestone documentation
├── config/                     # TOML configuration files
├── src/                        # Legacy source (being migrated to services/)
└── requirements-unified.txt    # All dependencies (80+ packages)
```

## Quickstart

1. Clone the repo and create a virtual environment:

   ```sh
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. Edit `config/config.toml` to match your data and reporting needs.
3. Run the main pipeline:

   ```sh
   python src/main.py
   ```

4. Run tests:

   ```sh
   python -m pytest --maxfail=3 --disable-warnings -v
   ```

## Project Structure

```
charlie-reporting/
├── services/           # Service-based architecture
│   ├── common/         # Shared utilities
│   ├── email_service/  # Email fetching service
│   ├── db_service/     # Database storage and query service
│   ├── report_service/ # Report generation service
│   └── main.py         # Entry point
├── src/                # Legacy source code
├── config/             # TOML config
├── tests/              # Unit tests & sample data
├── docs/               # Documentation
├── .vscode/            # VS Code settings
├── requirements.txt    # Python dependencies
├── pyproject.toml      # Build system & metadata
├── README.md           # This file
├── LICENSE             # MIT License
└── .gitignore
```

## Extending

- Add new report types or data sources by subclassing and updating the config.
- All config and column mapping is TOML-based for clarity and future DB integration.

---

*Built with ❤️ by Jonathan Wardwell, Copilot, and GPT-4o inspiration.*

# charlie-reporting
