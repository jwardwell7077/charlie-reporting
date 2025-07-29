# Charlie Reporting - Project Wiki

Welcome to the Charlie Reporting project wiki! This documentation system tracks our journey from a Windows desktop automation tool to a full-scale enterprise microservices architecture.

## 📚 Documentation Structure

### 🏃‍♂️ [Sprint Reviews](/docs/sprint-reviews/)
Track development progress, achievements, and learnings through regular sprint retrospectives.

### 📋 [Project Milestones](#project-milestones)
Major achievement tracking and phase completion status.

### 🏗️ [Architecture Documentation](#architecture-docs)
Technical architecture, design decisions, and system blueprints.

### 📈 [Development Metrics](#development-metrics)
Code quality, performance benchmarks, and technical debt tracking.

---

## 🎯 Project Milestones

### ✅ **Phase 1: Foundation & Business Logic** *(Completed: July 28, 2025)*
- **Business Logic Services**: CSV transformation and Excel report generation
- **WSL Development Environment**: Permanent virtual environment setup
- **VS Code Integration**: Optimized workspace with task automation
- **Testing Infrastructure**: pytest framework foundation
- **Service Architecture**: Microservices structure established

**📊 Sprint Review**: [Phase 1 Review & Phase 2 Planning](/docs/sprint-reviews/2025-07-28-phase1-review.md)

### 🚧 **Phase 2: Testing & API Framework** *(In Progress)*
- **Test Suite Migration**: Legacy tests to pytest framework
- **Code Coverage**: Comprehensive testing metrics
- **REST API Implementation**: FastAPI service endpoints
- **Integration Testing**: Cross-service communication validation

### 📅 **Phase 3: Service Implementation** *(Planned)*
- **All 5 Services**: Complete microservices implementation
- **Database Integration**: SQLAlchemy and data persistence
- **Service Discovery**: HTTP client and communication patterns
- **Error Handling**: Comprehensive resilience patterns

### 📅 **Phase 4: Orchestration** *(Planned)*
- **Scheduler Service**: Automated workflow orchestration
- **Web Dashboard**: Real-time monitoring and control
- **Job Management**: Scheduling, retry logic, error recovery
- **End-to-End Integration**: Complete automated pipeline

### 📅 **Phase 5: Production** *(Planned)*
- **Docker Deployment**: Containerized service stack
- **Monitoring & Logging**: Observability infrastructure
- **Performance Optimization**: Resource usage and scaling
- **Documentation Complete**: Full production deployment guides

---

## 🏗️ Architecture Documentation {#architecture-docs}

### **System Overview**
Charlie Reporting is a microservices-based email automation platform that transforms CSV data into formatted Excel reports through a distributed service architecture.

### **Core Services Architecture**
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

### **Technical Documentation**
- **📋 [Implementation Roadmap](/implementation_roadmap.md)**: 8-week development plan
- **🏢 [Enterprise Architecture](/enterprise_architecture.md)**: Production patterns and practices
- **🔧 [Microservices Design](/microservices_architecture.md)**: Service boundaries and APIs
- **📊 [Project Structure](/project_structure.md)**: Code organization and templates

### **Design Decisions**
- **Technology Stack**: Python, FastAPI, SQLAlchemy, Docker
- **Development Environment**: WSL2 for cross-platform compatibility
- **Testing Strategy**: pytest with comprehensive coverage
- **Deployment**: Docker Compose → Kubernetes progression

---

## 📈 Development Metrics {#development-metrics}

### **Code Quality Status**
- **Test Coverage**: Target 85%+ (Current: Foundation established)
- **Code Formatting**: Black + flake8 integration ✅
- **Type Safety**: Pydantic models with validation ✅
- **Documentation**: Comprehensive architectural docs ✅

### **Performance Benchmarks**
- **CSV Processing**: Target < 30 seconds for daily files
- **Excel Generation**: Target < 2 minutes for complete reports
- **API Response Time**: Target < 2 seconds for 95th percentile
- **Service Startup**: Target < 10 seconds per service

### **Technical Debt Tracking**
- **Legacy Code Migration**: src/ → services/ structure complete
- **Configuration Management**: TOML-based config system ✅
- **Environment Setup**: WSL development environment stable ✅
- **Testing Framework**: pytest migration in progress

---

## 🎯 Current Sprint Focus

### **Active Work Items**
1. **Test Suite Migration**: Converting legacy tests to pytest framework
2. **Code Coverage Setup**: Integration with VS Code development workflow
3. **API Framework**: FastAPI service template creation
4. **Performance Baselines**: Establishing benchmark metrics

### **Key Decisions Pending**
- Database selection (SQLite vs PostgreSQL for development)
- Service communication patterns (HTTP vs message queue)
- Deployment strategy (Docker Compose vs Kubernetes timeline)
- Monitoring solution (Prometheus vs alternative)

---

## 📖 Quick Navigation

### **For Developers**
- **🏁 [Getting Started](/README.md#quickstart)**: Setup and first run
- **🧪 [Testing Guide](/tests/README.md)**: Test execution and development
- **⚙️ [Configuration](/config/)**: Service and environment settings
- **🔧 [VS Code Setup](/.vscode/)**: Development environment configuration

### **For Architecture Review**
- **📋 [Sprint Reviews](/docs/sprint-reviews/)**: Progress and decision tracking
- **🏗️ [Architecture Patterns](/enterprise_architecture.md)**: Enterprise design principles
- **📊 [Service APIs](/docs/api/)**: REST endpoint documentation
- **🚀 [Deployment](/docs/deployment/)**: Production deployment guides

### **For Project Management**
- **🎯 [Project Milestones](#project-milestones)**: Phase completion tracking
- **📈 [Development Metrics](#development-metrics)**: Quality and performance indicators
- **🔄 [Sprint Planning](/docs/sprint-reviews/)**: Regular progress reviews
- **💡 [Technical Decisions](/docs/decisions/)**: Architecture decision records

---

## 🤝 Contributing

This project follows a structured development approach with regular sprint reviews and comprehensive documentation. All major decisions and progress are tracked through:

1. **Sprint Reviews**: Bi-weekly progress documentation
2. **Architecture Decisions**: Technical choice documentation
3. **Code Quality**: Automated testing and formatting
4. **Performance Tracking**: Benchmark and optimization metrics

---

*Wiki maintained by: Jon Wardwell with GitHub Copilot assistance*  
*Last updated: July 28, 2025*  
*Project repository: [charlie-reporting](https://github.com/jwardwell7077/charlie-reporting)*
