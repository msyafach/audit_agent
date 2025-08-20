#!/usr/bin/env python3
"""
Utility functions for the financial audit system
"""

import os
import glob
import json
import time
from typing import Dict, List, Tuple, Any
from pathlib import Path

def detect_all_companies(input_dir: str = "input") -> List[str]:
    """Detect all companies in the input directory"""
    
    balance_sheet_files = glob.glob(os.path.join(input_dir, '*_posisi_keuangan.txt'))
    companies = []
    
    for file in balance_sheet_files:
        filename = os.path.basename(file)
        company_name = filename.replace('_posisi_keuangan.txt', '')
        companies.append(company_name)
    
    return sorted(companies)

def load_financial_statements(input_dir: str = "input", company_name: str = None) -> Tuple[Dict[str, str], str]:
    """Load financial statements for specific company or auto-detect first one"""
    
    if company_name is None:
        companies = detect_all_companies(input_dir)
        if not companies:
            raise ValueError("No balance sheet files found with pattern 'COMPANY_posisi_keuangan.txt'")
        company_name = companies[0]
    
    files = {
        'neraca': os.path.join(input_dir, f'{company_name}_posisi_keuangan.txt'),
        'laba_rugi': os.path.join(input_dir, f'{company_name}_laba_rugi.txt'),
        'arus_kas': os.path.join(input_dir, f'{company_name}_arus_kas.txt')
    }
    
    statements = {}
    missing_files = []
    
    for key, filepath in files.items():
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                statements[key] = f.read()
            print(f"✅ Loaded: {os.path.basename(filepath)}")
        else:
            print(f"❌ Missing: {os.path.basename(filepath)}")
            missing_files.append(os.path.basename(filepath))
    
    if missing_files:
        print(f"\n⚠️  Expected files for company '{company_name}':")
        for file_type, filename in [
            ('Balance Sheet', f'{company_name}_posisi_keuangan.txt'),
            ('Income Statement', f'{company_name}_laba_rugi.txt'),
            ('Cash Flow Statement', f'{company_name}_arus_kas.txt')
        ]:
            print(f"   - {filename} ({file_type})")
    
    return statements, company_name

def save_audit_results(results: Dict[str, Any], company: str, 
                      output_dir: str = "results", system_type: str = "audit") -> str:
    """Save audit results to JSON file"""
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Generate filename
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f'{company}_{system_type}_results.json'
    filepath = os.path.join(output_dir, filename)
    
    # Save results
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return filepath

def clean_json_response(content: str) -> str:
    """Clean and extract JSON from model response"""
    
    content = content.strip()
    
    # Remove markdown code blocks
    if content.startswith('```json'):
        content = content[7:-3]
    elif content.startswith('```'):
        content = content[3:-3]
    
    # Extract JSON from content if needed
    start = content.find('{')
    end = content.rfind('}') + 1
    
    if start != -1 and end != -1:
        content = content[start:end]
    
    return content.strip()

def parse_json_safely(content: str) -> Dict[str, Any]:
    """Safely parse JSON with error handling"""
    
    try:
        cleaned = clean_json_response(content)
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        print(f"🔍 Content preview: {content[:200]}...")
        
        # Return minimal valid structure
        return {
            "laporan_posisi_keuangan": {
                "aset": {
                    "total_aset": {
                        "nama_akun": "Total Aset",
                        "nilai_tercatat": 0,
                        "nilai_perhitungan": 0,
                        "selisih": 0,
                        "status": "ERROR - JSON parsing failed"
                    }
                },
                "error_info": {
                    "error_type": "JSON parsing failed",
                    "error_message": str(e),
                    "raw_content_preview": content[:500]
                }
            }
        }

def validate_financial_data_structure(data: Dict[str, Any]) -> bool:
    """Validate that financial data has expected structure"""
    
    if not isinstance(data, dict):
        return False
    
    # Check for main financial statement section
    if 'laporan_posisi_keuangan' not in data:
        return False
    
    posisi = data['laporan_posisi_keuangan']
    if not isinstance(posisi, dict):
        return False
    
    # Check for asset section
    if 'aset' in posisi:
        aset = posisi['aset']
        if isinstance(aset, dict):
            # Look for at least one asset item with required fields
            for key, value in aset.items():
                if isinstance(value, dict) and 'nilai_tercatat' in value:
                    return True
    
    return False

def extract_numerical_values(data: Dict[str, Any]) -> List[float]:
    """Extract all numerical values from nested financial data"""
    
    values = []
    
    def extract_recursive(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ['nilai_tercatat', 'nilai_perhitungan', 'total_aset', 'total_liabilitas_ekuitas']:
                    try:
                        values.append(float(value))
                    except (ValueError, TypeError):
                        pass
                else:
                    extract_recursive(value)
        elif isinstance(obj, list):
            for item in obj:
                extract_recursive(item)
    
    extract_recursive(data)
    return values

def format_currency(amount: float) -> str:
    """Format currency amount for display"""
    return f"{amount:,.0f}"

def calculate_percentage_difference(value1: float, value2: float) -> float:
    """Calculate percentage difference between two values"""
    if value2 == 0:
        return 100.0 if value1 != 0 else 0.0
    return abs(value1 - value2) / value2 * 100

def print_audit_summary(results: Dict[str, Any], company: str):
    """Print a formatted summary of audit results"""
    
    print(f"\n{'='*60}")
    print(f"AUDIT SUMMARY FOR {company}")
    print(f"{'='*60}")
    
    # Extract metadata
    metadata_keys = [key for key in results.keys() if 'metadata' in key.lower()]
    
    if metadata_keys:
        metadata = results[metadata_keys[0]]
        print(f"🎯 System: {metadata.get('system_type', 'Unknown')}")
        print(f"🏢 Company: {company}")
        print(f"📊 Consensus: {metadata.get('consensus_quality', 'Unknown')}")
        print(f"🔄 Retries: {metadata.get('total_retries', 0)}")
        print(f"⏰ Timestamp: {metadata.get('audit_timestamp', 'Unknown')}")
        
        if 'mathematical_precision' in metadata:
            print(f"🧮 Precision: {metadata['mathematical_precision']}")
    
    # Extract main audit results
    audit_data = results.get("audit_footing_laporan_keuangan", {})
    
    if 'laporan_posisi_keuangan' in audit_data:
        posisi = audit_data['laporan_posisi_keuangan']
        
        # Balance sheet summary
        if 'aset' in posisi:
            aset = posisi['aset']
            if 'total_aset' in aset:
                total_aset = aset['total_aset']
                if isinstance(total_aset, dict) and 'nilai_tercatat' in total_aset:
                    print(f"💰 Total Assets: {format_currency(total_aset['nilai_tercatat'])}")
                    
                    status = total_aset.get('status', 'Unknown')
                    print(f"📈 Status: {status}")
        
        # Balance check
        if 'balancing' in posisi:
            balancing = posisi['balancing']
            status = balancing.get('status', 'Unknown')
            print(f"⚖️  Balance: {status}")
    
    print(f"{'='*60}")

class DebugLogger:
    """Simple debug logger for the audit system"""
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
    
    def log(self, message: str, level: str = "INFO"):
        if self.enabled:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")
    
    def debug(self, message: str):
        self.log(message, "DEBUG")
    
    def info(self, message: str):
        self.log(message, "INFO")
    
    def warning(self, message: str):
        self.log(message, "WARNING")
    
    def error(self, message: str):
        self.log(message, "ERROR")