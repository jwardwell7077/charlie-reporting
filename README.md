# Charlie Reporting System

A modern microservices-based reporting system for processing CSV data and generating Excel reports.

**🎯 Portfolio Project**: This demonstrates enterprise-grade microservices architecture, professional development practices, and legacy system modernization.

## 📖 **Project Documentation**

- **[Development Diary](docs/development-diary.md)**: Complete journey from desktop app to microservices architecture
- **[Final Deliverable](docs/deliverables/phase-2-final-deliverable.md)**: Portfolio-ready project summary and employment value
- **[Architecture Documentation](docs/architecture/)**: Technical design and implementation details
- **[Sprint Reviews](docs/sprint-reviews/)**: Professional project management and progress tracking

## 🚀 Quick Start

```bash
# Run the main application
python3 run.py

# Run tests across all services
python3 scripts/test_runner.py

# Start development services
python3 scripts/start_dev_services.py
```

## 📁 Project Structure

├── services/              # Microservices
│   ├── report_generator/   # CSV processing & Excel generation
│   ├── email-service/      # Email processing
│   ├── outlook-relay/      # Outlook integration
│   ├── database-service/   # Data persistence
│   └── scheduler-service/  # Task scheduling
│
├── shared/                # Shared utilities & libraries
│   ├── config_manager.py   # Configuration management
│   ├── logging_utils.py    # Logging utilities
│   └── tests/             # Shared test utilities
│
├── scripts/               # Management & utility scripts
│   ├── test_runner.py     # Service test runner
│   └── start_dev_services.py
│
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   ├── architecture/     # System architecture docs
│   └── migration/        # Migration guides
│
├── tools/                 # Development & setup tools
│   ├── setup/            # Environment setup scripts
│   └── development/      # Development utilities
│
├── archive/               # Historical & deprecated files
│   ├── migration/        # Migration artifacts
│   ├── deprecated/       # Deprecated code
│   └── debug/           # Debug scripts
│
├── config/               # Configuration files
├── demo/                 # Demo data & scripts
├── logs/                 # Application logs
└── legacy_backup/        # Backup of migrated code

## 🏗️ Architecture

This system follows a modern microservices architecture:

- **Report Generator Service**: Core CSV processing and Excel generation
- **Email Service**: Email fetching and processing
- **Outlook Relay**: Outlook/Exchange integration
- **Database Service**: Data persistence and retrieval
- **Scheduler Service**: Task scheduling and automation

## 🧪 Testing

```bash
# Run all tests
python3 scripts/test_runner.py

# Run tests for specific service
python3 scripts/test_runner.py --service report_generator

# Run specific test types
python3 scripts/test_runner.py --type unit
python3 scripts/test_runner.py --type integration
```

## 📚 Documentation

- [API Documentation](docs/api/)
- [Architecture Overview](docs/architecture/)
- [Migration Guide](docs/migration/)
- [Development Setup](tools/setup/)

## 🛠️ Development

See [tools/development/](tools/development/) for development setup and utilities.

## 📈 Status

✅ Phase 2 Complete - Microservices architecture fully implemented
✅ Legacy code migration completed
✅ Test suite reorganized into service-specific tests
✅ Root directory cleanup completed
