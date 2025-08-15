#!/usr/bin/env python3
"""Report-Generator Service Flake8 Compliance Script
Systematically fixes common flake8 violations in the report-generator service.
"""

import re
from pathlib import Path


class ReportGeneratorCompliance:
    """Fix flake8 violations in report-generator service."""
    
    def __init__(self, service_root: str):
        self.service_root = Path(service_root)
        self.files_fixed = 0
        self.fixes_applied = 0
        
    def run_compliance_fix(self):
        """Run comprehensive compliance fix."""
        print("🔧 Starting Report-Generator Service Flake8 Compliance...")
        print(f"Service root: {self.service_root}")
        
        # Get all Python files in the service
        python_files = list(self.service_root.glob("**/*.py"))
        print(f"Found {len(python_files)} Python files")
        
        for py_file in python_files:
            try:
                with open(py_file, encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                fixed_content = self.fix_file_content(content, py_file)
                
                if fixed_content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    self.files_fixed += 1
                    print(f"Fixed: {py_file.relative_to(self.service_root)}")
                    
            except Exception as e:
                print(f"Error processing {py_file}: {e}")
        
        print(f"\nCompleted: {self.files_fixed} files fixed, {self.fixes_applied} violations corrected")
        
    def fix_file_content(self, content: str, file_path: Path) -> str:
        """Apply common fixes to file content."""
        # Fix common variable naming issues
        content = self.fix_variable_naming(content)
        
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            # Fix trailing whitespace (W291, W293)
            if line.rstrip() != line:
                line = line.rstrip()
                self.fixes_applied += 1
            
            # Fix blank line contains whitespace (W293)
            if line.strip() == '' and line != '':
                line = ''
                self.fixes_applied += 1
            
            # Fix shebang spacing
            if line.startswith('#!/usr / bin / env'):
                line = line.replace('#!/usr / bin / env', '#!/usr/bin/env')
                self.fixes_applied += 1
            
            new_lines.append(line)
        
        # Ensure file ends with newline (W292)
        if new_lines and new_lines[-1] != '':
            new_lines.append('')
            self.fixes_applied += 1
        
        return '\n'.join(new_lines)
    
    def fix_variable_naming(self, content: str) -> str:
        """Fix common variable naming issues."""
        # Common F821/F841 fixes
        fixes = {
            'successcount': 'success_count',
            'totalchecks': 'total_checks', 
            'validationscore': 'validation_score',
            'configdata': 'config_data',
            'formattedbytes': 'formatted_bytes',
            'workbookbytes': 'workbook_bytes',
            'inputstream': 'input_stream',
            'maxlength': 'max_length',
            'csvrules': 'csv_rules',
            'rulesconfig': 'rules_config',
            'csvrule': 'csv_rule',
        }
        
        for wrong, correct in fixes.items():
            # Only replace whole words to avoid partial matches
            content = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, content)
            if wrong in content and wrong != correct:
                self.fixes_applied += 1
        
        return content


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    service_root = script_dir.parent / 'services' / 'report-generator'
    
    if not service_root.exists():
        print(f"Service directory not found: {service_root}")
        return
    
    fixer = ReportGeneratorCompliance(str(service_root))
    fixer.run_compliance_fix()


if __name__ == "__main__":
    main()
