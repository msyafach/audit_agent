#!/usr/bin/env python3
"""
Security Check Script for Financial Audit System
Verifies that no sensitive data is exposed in the codebase
"""

import os
import re
import glob
from typing import List, Tuple

class SecurityChecker:
    """Security vulnerability checker"""
    
    def __init__(self):
        self.sensitive_patterns = {
            'api_keys': [
                r'AIza[A-Za-z0-9_-]{35}',  # Google API keys
                r'sk-[A-Za-z0-9]{48}',      # OpenAI API keys
                r'xoxb-[0-9]{13}-[0-9]{13}-[A-Za-z0-9]{24}',  # Slack bot tokens
            ],
            'hardcoded_secrets': [
                r'password\s*=\s*[\'"][^\'"\s]+[\'"]',
                r'secret\s*=\s*[\'"][^\'"\s]+[\'"]',
                r'token\s*=\s*[\'"][^\'"\s]+[\'"]',
            ],
            'suspicious_hardcoded': [
                r'[\'"][A-Za-z0-9]{32,}[\'"]',  # Long random strings
            ]
        }
        
        self.exclude_patterns = [
            r'\.git/',
            r'__pycache__/',
            r'\.pyc$',
            r'security_check\.py$',  # Exclude this file itself
            r'\.env\.example$',      # Template files are OK
        ]
    
    def should_exclude_file(self, filepath: str) -> bool:
        """Check if file should be excluded from scanning"""
        for pattern in self.exclude_patterns:
            if re.search(pattern, filepath):
                return True
        return False
    
    def scan_file(self, filepath: str) -> List[Tuple[str, int, str, str]]:
        """Scan a single file for security issues"""
        issues = []
        
        if self.should_exclude_file(filepath):
            return issues
            
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                # Check each category of patterns
                for category, patterns in self.sensitive_patterns.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            # Mask the sensitive part
                            masked_line = line[:match.start()] + '***REDACTED***' + line[match.end():]
                            issues.append((filepath, line_num, category, masked_line.strip()))
                            
        except Exception as e:
            print(f"⚠️  Error scanning {filepath}: {e}")
            
        return issues
    
    def scan_directory(self, directory: str = ".") -> List[Tuple[str, int, str, str]]:
        """Scan entire directory for security issues"""
        all_issues = []
        
        # Get all Python files and config files
        file_patterns = [
            "**/*.py",
            "**/*.json",
            "**/*.yaml", 
            "**/*.yml",
            "**/*.env*",
            "**/*.md",
            "**/*.txt"
        ]
        
        files_to_scan = []
        for pattern in file_patterns:
            files_to_scan.extend(glob.glob(os.path.join(directory, pattern), recursive=True))
        
        # Remove duplicates
        files_to_scan = list(set(files_to_scan))
        
        print(f"🔍 Scanning {len(files_to_scan)} files for security issues...")
        
        for filepath in files_to_scan:
            issues = self.scan_file(filepath)
            all_issues.extend(issues)
            
        return all_issues
    
    def generate_report(self, issues: List[Tuple[str, int, str, str]]) -> None:
        """Generate security report"""
        
        print("\n" + "="*80)
        print("🛡️  SECURITY SCAN REPORT")
        print("="*80)
        
        if not issues:
            print("✅ NO SECURITY ISSUES FOUND!")
            print("\n🎉 Your codebase appears to be secure.")
            print("📝 Remember to:")
            print("   - Keep API keys in environment variables")
            print("   - Never commit .env files")
            print("   - Use .env.example for templates")
            return
        
        print(f"❌ FOUND {len(issues)} SECURITY ISSUES:")
        print()
        
        # Group by category
        by_category = {}
        for filepath, line_num, category, line_content in issues:
            if category not in by_category:
                by_category[category] = []
            by_category[category].append((filepath, line_num, line_content))
        
        for category, category_issues in by_category.items():
            print(f"🚨 {category.upper()}:")
            for filepath, line_num, line_content in category_issues:
                print(f"   📁 {filepath}:{line_num}")
                print(f"   📝 {line_content}")
                print()
        
        print("🔧 RECOMMENDED ACTIONS:")
        print("1. Remove hardcoded secrets and API keys")
        print("2. Use environment variables or .env files")
        print("3. Add sensitive files to .gitignore")
        print("4. Review and fix each issue above")

def main():
    """Main security check function"""
    
    print("🔐 FINANCIAL AUDIT SYSTEM - SECURITY CHECK")
    print("="*50)
    
    checker = SecurityChecker()
    issues = checker.scan_directory(".")
    checker.generate_report(issues)
    
    return len(issues) == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)