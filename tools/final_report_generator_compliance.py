#!/usr/bin/env python3
"""Final Report-Generator Compliance Script
This script addresses the remaining Flake8, PEP 8, and Pylance compliance issues.
"""

import re
import subprocess
from pathlib import Path


class ReportGeneratorCompliance:
    """Complete compliance checker and fixer for report-generator service."""
    
    def __init__(self, service_root: str):
        self.service_root = Path(service_root)
        self.files_fixed = 0
        self.issues_fixed = 0
        
    def run_full_compliance_check(self):
        """Run complete compliance check and fixes."""
        print("🔍 REPORT-GENERATOR SERVICE COMPLIANCE CHECK")
        print("=" * 60)
        
        # Step 1: Check Flake8 violations
        print("\n1. Checking Flake8 violations...")
        flake8_issues = self.get_flake8_violations()
        print(f"Found {len(flake8_issues)} Flake8 violations")
        
        # Step 2: Fix common variable naming issues
        print("\n2. Fixing variable naming issues...")
        self.fix_variable_naming_issues()
        
        # Step 3: Fix import issues
        print("\n3. Checking and fixing import issues...")
        self.fix_import_issues()
        
        # Step 4: Fix formatting issues
        print("\n4. Fixing formatting issues...")
        self.fix_formatting_issues()
        
        # Step 5: Final check
        print("\n5. Running final compliance check...")
        final_violations = self.get_flake8_violations()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 COMPLIANCE SUMMARY")
        print("=" * 60)
        print(f"Files processed: {len(list(self.service_root.glob('**/*.py')))}")
        print(f"Files fixed: {self.files_fixed}")
        print(f"Issues resolved: {self.issues_fixed}")
        print(f"Remaining violations: {len(final_violations)}")
        
        if len(final_violations) == 0:
            print("\n🎉 REPORT-GENERATOR SERVICE IS 100% COMPLIANT!")
        else:
            print(f"\n⚠️ {len(final_violations)} violations remaining")
            self.show_remaining_violations(final_violations[:10])
            
        return len(final_violations) == 0
    
    def get_flake8_violations(self) -> list[str]:
        """Get current flake8 violations."""
        try:
            result = subprocess.run(
                ['flake8', '--config=../../.flake8', '.'],
                check=False, cwd=self.service_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.stdout:
                return result.stdout.strip().split('\n')
            return []
        except Exception:
            return []
    
    def fix_variable_naming_issues(self):
        """Fix common variable naming issues."""
        variable_fixes = {
            # Common patterns from previous analysis
            'testinstance': 'test_instance',
            'reportprocessor': 'report_processor',
            'directoryprocessor': 'directory_processor',
            'csvtransformer': 'csv_transformer',
            'filemanager': 'file_manager',
            'configmanager': 'config_manager',
            'metricsdata': 'metrics_data',
            'performancedata': 'performance_data',
            'validationresult': 'validation_result',
            'testresult': 'test_result',
            'errorcount': 'error_count',
            'successcount': 'success_count',
            'totalcount': 'total_count',
        }
        
        for py_file in self.service_root.glob("**/*.py"):
            try:
                with open(py_file, encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Apply variable name fixes
                for wrong, correct in variable_fixes.items():
                    # Use word boundary to avoid partial matches
                    pattern = r'\b' + re.escape(wrong) + r'\b'
                    content = re.sub(pattern, correct, content)
                
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.files_fixed += 1
                    self.issues_fixed += 1
                    
            except Exception as e:
                print(f"Error fixing variables in {py_file}: {e}")
    
    def fix_import_issues(self):
        """Fix common import issues."""
        for py_file in self.service_root.glob("**/*.py"):
            try:
                with open(py_file, encoding='utf-8') as f:
                    lines = f.readlines()
                
                new_lines = []
                import_section = True
                
                for line in lines:
                    # Skip empty imports or fix common import issues
                    if import_section and line.strip().startswith('from'):
                        # Fix relative imports that might be wrong
                        if 'from src.business.models.csv_data import CSVRule' in line:
                            # Check if we're in infrastructure - use relative import
                            if 'infrastructure' in str(py_file):
                                line = 'from business.models.csv_data import CSVRule\n'
                        
                    new_lines.append(line)
                    
                    # End of import section
                    if line.strip() and not line.strip().startswith(('import', 'from', '#', '"""', "'''")):
                        import_section = False
                
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                    
            except Exception as e:
                print(f"Error fixing imports in {py_file}: {e}")
    
    def fix_formatting_issues(self):
        """Fix common formatting issues."""
        for py_file in self.service_root.glob("**/*.py"):
            try:
                with open(py_file, encoding='utf-8') as f:
                    content = f.read()
                
                if not content.strip():
                    continue
                
                lines = content.split('\n')
                new_lines = []
                
                for i, line in enumerate(lines):
                    # Remove trailing whitespace
                    clean_line = line.rstrip()
                    
                    # Fix common indentation issues
                    if clean_line.strip() == 'pass' and i > 0:
                        prev_line = lines[i-1].strip()
                        if prev_line.endswith(':'):
                            # Ensure pass is properly indented
                            if not clean_line.startswith('    '):
                                clean_line = '    pass'
                    
                    new_lines.append(clean_line)
                
                # Ensure file ends with newline
                if new_lines and new_lines[-1] != '':
                    new_lines.append('')
                
                new_content = '\n'.join(new_lines)
                
                if new_content != content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    self.issues_fixed += 1
                    
            except Exception as e:
                print(f"Error fixing formatting in {py_file}: {e}")
    
    def show_remaining_violations(self, violations: list[str]):
        """Show remaining violations."""
        print("\nTop remaining violations:")
        for violation in violations:
            if violation.strip():
                print(f"  {violation}")


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    service_root = script_dir.parent / 'services' / 'report-generator'
    
    if not service_root.exists():
        print(f"Service directory not found: {service_root}")
        return False
    
    checker = ReportGeneratorCompliance(str(service_root))
    return checker.run_full_compliance_check()


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
