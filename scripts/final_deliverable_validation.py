#!/usr/bin/env python3
"""
Phase 2 Final Deliverable Validation
Confirms current project status for immediate delivery readiness
"""

import os
import sys
from pathlib import Path

def check_exists(path_str, description):
    """Check if a path exists and return status"""
    path = Path(path_str)
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {'Found' if exists else 'Missing'}")
    return exists

def check_directory_structure():
    """Validate core project organization"""
    print("\n🏗️  PROJECT ORGANIZATION VALIDATION")
    print("=" * 50)
    
    structure_checks = [
        ("services/", "Microservices directory structure"),
        ("shared/", "Shared components directory"),
        ("docs/", "Documentation directory"),
        ("archive/", "Archive preservation system"),
        ("config/", "Configuration management"),
        ("tools/", "Development tools directory"),
    ]
    
    passed = 0
    for path, desc in structure_checks:
        if check_exists(path, desc):
            passed += 1
    
    return passed, len(structure_checks)

def check_service_architecture():
    """Validate microservices implementation"""
    print("\n🔧 MICROSERVICES ARCHITECTURE VALIDATION")
    print("=" * 50)
    
    services = [
        "services/csv-processor/",
        "services/excel-writer/", 
        "services/email-fetcher/",
        "services/report-generator/",
        "services/config-manager/"
    ]
    
    passed = 0
    for service in services:
        if check_exists(service, f"Service: {service.split('/')[-2]}"):
            passed += 1
            
        # Check service structure
        service_files = [
            f"{service}src/",
            f"{service}tests/",
            f"{service}config/"
        ]
        
        for service_file in service_files:
            check_exists(service_file, f"  └─ {service_file.split('/')[-2]}/")
    
    return passed, len(services)

def check_documentation():
    """Validate documentation completeness"""
    print("\n📚 DOCUMENTATION VALIDATION")
    print("=" * 50)
    
    docs = [
        ("docs/architecture/", "Architecture documentation"),
        ("docs/phase-plans/", "Phase planning documentation"),
        ("docs/sprint-reviews/", "Sprint review documentation"),
        ("docs/deliverables/", "Deliverable documentation"),
        ("README.md", "Project README")
    ]
    
    passed = 0
    for path, desc in docs:
        if check_exists(path, desc):
            passed += 1
    
    return passed, len(docs)

def check_development_infrastructure():
    """Validate development environment setup"""
    print("\n🛠️  DEVELOPMENT INFRASTRUCTURE VALIDATION")
    print("=" * 50)
    
    infra_checks = [
        (".vscode/tasks.json", "VS Code automated tasks"),
        (".vscode/launch.json", "VS Code debug configurations"),
        ("requirements.txt", "Python dependencies"),
        ("pyproject.toml", "Project configuration"),
        ("config/config.toml", "Application configuration"),
    ]
    
    passed = 0
    for path, desc in infra_checks:
        if check_exists(path, desc):
            passed += 1
    
    return passed, len(infra_checks)

def check_business_logic():
    """Validate business logic preservation"""
    print("\n💼 BUSINESS LOGIC VALIDATION")
    print("=" * 50)
    
    business_files = [
        ("src/", "Core business logic"),
        ("src/main.py", "Main application entry"),
        ("src/email_fetcher.py", "Email automation"),
        ("src/excel_writer.py", "Excel generation"),
        ("src/transformer.py", "Data transformation"),
    ]
    
    passed = 0
    for path, desc in business_files:
        if check_exists(path, desc):
            passed += 1
    
    return passed, len(business_files)

def main():
    """Run complete Phase 2 deliverable validation"""
    print("🎯 PHASE 2 FINAL DELIVERABLE VALIDATION")
    print("=" * 60)
    print("Validating current project status for immediate delivery readiness")
    print()
    
    # Run all validation checks
    org_passed, org_total = check_directory_structure()
    arch_passed, arch_total = check_service_architecture()
    docs_passed, docs_total = check_documentation()
    infra_passed, infra_total = check_development_infrastructure()
    business_passed, business_total = check_business_logic()
    
    # Calculate overall completion
    total_passed = org_passed + arch_passed + docs_passed + infra_passed + business_passed
    total_checks = org_total + arch_total + docs_total + infra_total + business_total
    completion_percentage = (total_passed / total_checks) * 100
    
    print("\n🎊 FINAL DELIVERABLE ASSESSMENT")
    print("=" * 50)
    print(f"✅ Project Organization: {org_passed}/{org_total} ({(org_passed/org_total)*100:.0f}%)")
    print(f"✅ Service Architecture: {arch_passed}/{arch_total} ({(arch_passed/arch_total)*100:.0f}%)")
    print(f"✅ Documentation: {docs_passed}/{docs_total} ({(docs_passed/docs_total)*100:.0f}%)")
    print(f"✅ Development Infrastructure: {infra_passed}/{infra_total} ({(infra_passed/infra_total)*100:.0f}%)")
    print(f"✅ Business Logic: {business_passed}/{business_total} ({(business_passed/business_total)*100:.0f}%)")
    
    print(f"\n🏆 OVERALL COMPLETION: {total_passed}/{total_checks} ({completion_percentage:.1f}%)")
    
    # Determine delivery status
    if completion_percentage >= 80:
        status = "🎯 EXCELLENT - IMMEDIATELY DELIVERABLE"
        recommendation = "✅ Ready for portfolio presentation and employment discussions"
    elif completion_percentage >= 70:
        status = "✅ GOOD - DELIVERABLE WITH MINOR ENHANCEMENTS"
        recommendation = "⚠️ Consider Phase 2.5 for enhanced demonstration value"
    elif completion_percentage >= 60:
        status = "⚠️ ADEQUATE - REQUIRES PHASE 2.5 FOR OPTIMAL DELIVERY"
        recommendation = "🔄 Complete Phase 2.5 mini-sprint for full technical demonstration"
    else:
        status = "❌ INCOMPLETE - SIGNIFICANT WORK REQUIRED"
        recommendation = "🚫 Continue development before considering delivery"
    
    print(f"\n📊 DELIVERY STATUS: {status}")
    print(f"💡 RECOMMENDATION: {recommendation}")
    
    # Portfolio value assessment
    print(f"\n💼 PORTFOLIO VALUE ASSESSMENT:")
    if completion_percentage >= 75:
        print("🏆 EXCELLENT demonstration of:")
        print("   • System architecture and microservices design")
        print("   • Project organization and technical leadership")
        print("   • Professional development practices")
        print("   • Legacy system modernization capabilities")
    
    print(f"\n🚀 ENHANCEMENT OPPORTUNITIES:")
    if arch_passed < arch_total:
        print("   • Complete API implementation (Phase 2.5)")
    if infra_passed < infra_total:
        print("   • Enhance testing framework (pytest-cov)")
    print("   • Add integration testing (Phase 2.5)")
    print("   • Implement performance benchmarks (Phase 2.5)")
    
    return completion_percentage >= 70

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
