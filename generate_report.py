#!/usr/bin/env python3
"""
Simple script to generate executive audit report
"""

import sys
import os
from report_generator import generate_executive_report

def main():
    """Generate executive audit report"""
    
    print("📊 GENERATING EXECUTIVE AUDIT REPORT")
    print("=" * 50)
    
    # Check if results directory exists
    results_dir = "results"
    if not os.path.exists(results_dir):
        print(f"❌ Results directory '{results_dir}' not found!")
        print("💡 Run an audit first: uv run python audit_system.py")
        return
    
    # Check for audit files
    import glob
    audit_files = glob.glob(os.path.join(results_dir, "*audit_results.json"))
    audit_files.extend(glob.glob(os.path.join(results_dir, "*triple_agent_results.json")))
    
    if not audit_files:
        print(f"❌ No audit result files found in '{results_dir}'!")
        print("💡 Run an audit first to generate data")
        return
    
    print(f"✅ Found {len(audit_files)} audit result files")
    
    # Generate report
    report_path = generate_executive_report(results_dir)
    
    if report_path:
        print(f"\n🎉 SUCCESS!")
        print(f"📄 Executive Report: {os.path.basename(report_path)}")
        print(f"📁 Full Path: {os.path.abspath(report_path)}")
        
        # Show file size
        file_size = os.path.getsize(report_path)
        print(f"📊 File Size: {file_size/1024:.1f} KB")
        
        print(f"\n💼 REPORT FEATURES:")
        print(f"   ✓ Executive Summary with Risk Assessment")
        print(f"   ✓ Individual Company Analysis")  
        print(f"   ✓ Key Financial Metrics")
        print(f"   ✓ Audit Trail & Methodology")
        print(f"   ✓ Professional PDF Format")
        
        print(f"\n📖 TO VIEW: Open the PDF file with any PDF reader")
        
    else:
        print(f"❌ Report generation failed!")
        print(f"💡 Check for errors above and try again")

if __name__ == "__main__":
    main()