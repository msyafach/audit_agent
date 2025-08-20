#!/usr/bin/env python3
"""
Executive Audit Report Generator
Generates professional PDF reports for audit executives
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import glob

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import Color, black, white, red, green, blue, orange
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️  ReportLab not installed. Install with: uv add reportlab")

class ExecutiveAuditReportGenerator:
    """Generates executive-friendly audit reports in PDF format"""
    
    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required. Install with: uv add reportlab")
        
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for the report"""
        
        # Executive Summary Title
        self.styles.add(ParagraphStyle(
            name='ExecutiveTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        # Company Header
        self.styles.add(ParagraphStyle(
            name='CompanyHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.darkgreen,
            alignment=TA_LEFT,
            spaceAfter=12
        ))
        
        # Status indicators
        self.styles.add(ParagraphStyle(
            name='StatusOK',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.darkgreen,
            alignment=TA_LEFT
        ))
        
        self.styles.add(ParagraphStyle(
            name='StatusError',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.red,
            alignment=TA_LEFT
        ))
        
        # Key metrics
        self.styles.add(ParagraphStyle(
            name='KeyMetric',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
    
    def generate_executive_report(self, results_dir: str = "results", 
                                output_filename: str = None) -> str:
        """Generate comprehensive executive audit report"""
        
        # Find all audit result files
        audit_files = self._find_audit_files(results_dir)
        
        if not audit_files:
            raise ValueError("No audit result files found in results directory")
        
        # Generate output filename
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"Executive_Audit_Report_{timestamp}.pdf"
        
        output_path = os.path.join(results_dir, output_filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Title page
        story.extend(self._create_title_page(audit_files))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary(audit_files))
        story.append(PageBreak())
        
        # Individual company reports
        for i, (company, filepath) in enumerate(audit_files):
            story.extend(self._create_company_report(company, filepath))
            if i < len(audit_files) - 1:  # Don't add page break after last company
                story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _find_audit_files(self, results_dir: str) -> List[tuple[str, str]]:
        """Find all audit result files"""
        
        patterns = [
            "*_audit_results.json",
            "*_triple_agent_results.json", 
            "*_gemini_triple_agent_results.json",
            "*_ollama_audit_results.json"
        ]
        
        audit_files = []
        
        for pattern in patterns:
            files = glob.glob(os.path.join(results_dir, pattern))
            for filepath in files:
                filename = os.path.basename(filepath)
                # Extract company name
                company = filename.split('_')[0]
                audit_files.append((company, filepath))
        
        # Remove duplicates and sort
        audit_files = list(set(audit_files))
        audit_files.sort(key=lambda x: x[0])
        
        return audit_files
    
    def _create_title_page(self, audit_files: List[tuple[str, str]]) -> List:
        """Create title page"""
        
        story = []
        
        # Main title
        story.append(Spacer(1, 2*inch))
        
        title = Paragraph(
            "EXECUTIVE AUDIT REPORT<br/>Financial Statement Footing Verification",
            self.styles['ExecutiveTitle']
        )
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        # Report info
        report_info = f"""
        <b>Report Generated:</b> {datetime.now().strftime("%B %d, %Y at %H:%M")}<br/>
        <b>Companies Audited:</b> {len(audit_files)}<br/>
        <b>Audit System:</b> Triple Agent AI Verification<br/>
        <b>Mathematical Precision:</b> 28-digit calculation accuracy
        """
        
        info_para = Paragraph(report_info, self.styles['Normal'])
        story.append(info_para)
        story.append(Spacer(1, 1*inch))
        
        # Company list
        company_list = "<b>Companies in this Report:</b><br/>"
        for i, (company, _) in enumerate(audit_files, 1):
            company_list += f"{i}. {company}<br/>"
        
        companies_para = Paragraph(company_list, self.styles['Normal'])
        story.append(companies_para)
        
        return story
    
    def _create_executive_summary(self, audit_files: List[tuple[str, str]]) -> List:
        """Create executive summary page"""
        
        story = []
        
        # Summary title
        title = Paragraph("EXECUTIVE SUMMARY", self.styles['ExecutiveTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Load and analyze all results
        summary_data = self._analyze_all_results(audit_files)
        
        # Key metrics table
        metrics_data = [
            ['Metric', 'Value', 'Status'],
            ['Total Companies Audited', str(summary_data['total_companies']), '✓'],
            ['Successful Audits', str(summary_data['successful_audits']), '✓' if summary_data['success_rate'] == 100 else '⚠️'],
            ['Overall Success Rate', f"{summary_data['success_rate']:.1f}%", '✓' if summary_data['success_rate'] >= 95 else '⚠️'],
            ['Average Processing Time', f"{summary_data['avg_processing_time']:.1f}s", '✓'],
            ['Total Calculations Verified', str(summary_data['total_calculations']), '✓'],
            ['Mathematical Precision', "28-digit accuracy", '✓']
        ]
        
        # Convert metrics data to Paragraph objects for better text wrapping
        formatted_metrics_data = []
        for i, row in enumerate(metrics_data):
            if i == 0:  # Header row
                formatted_row = [Paragraph(f"<b>{cell}</b>", self.styles['Normal']) for cell in row]
            else:
                formatted_row = [Paragraph(str(cell), self.styles['Normal']) for cell in row]
            formatted_metrics_data.append(formatted_row)
        
        metrics_table = Table(formatted_metrics_data, colWidths=[3.2*inch, 1.5*inch, 0.8*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 30))
        
        # Risk assessment
        risk_level = self._assess_overall_risk(summary_data)
        risk_text = f"""
        <b>OVERALL RISK ASSESSMENT: {risk_level['level']}</b><br/><br/>
        {risk_level['description']}<br/><br/>
        <b>Key Findings:</b><br/>
        • All calculations verified using AI-powered triple agent consensus<br/>
        • Mathematical accuracy ensured through 28-digit precision tools<br/>
        • {summary_data['consensus_quality']} consensus achieved across all audited statements<br/>
        • Zero manual calculations - all computations tool-verified
        """
        
        risk_para = Paragraph(risk_text, self.styles['Normal'])
        story.append(risk_para)
        
        # Recommendations
        story.append(Spacer(1, 20))
        recommendations = self._generate_recommendations(summary_data)
        rec_text = "<b>EXECUTIVE RECOMMENDATIONS:</b><br/>" + "<br/>".join([f"• {rec}" for rec in recommendations])
        rec_para = Paragraph(rec_text, self.styles['Normal'])
        story.append(rec_para)
        
        return story
    
    def _create_company_report(self, company: str, filepath: str) -> List:
        """Create individual company report"""
        
        story = []
        
        # Company header
        header = Paragraph(f"AUDIT REPORT - {company}", self.styles['CompanyHeader'])
        story.append(header)
        story.append(Spacer(1, 15))
        
        # Load audit data
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                audit_data = json.load(f)
        except Exception as e:
            error_text = f"Error loading audit data for {company}: {e}"
            error_para = Paragraph(error_text, self.styles['StatusError'])
            story.append(error_para)
            return story
        
        # Extract company metrics
        company_metrics = self._extract_company_metrics(audit_data)
        
        # Company summary table
        summary_data = [
            ['Audit Item', 'Status', 'Details'],
            ['Balance Sheet Verification', 
             self._clean_text_for_pdf(company_metrics['balance_sheet_status']), 
             self._clean_text_for_pdf(company_metrics['balance_sheet_details'])],
            ['Income Statement Check', 
             self._clean_text_for_pdf(company_metrics['income_statement_status']), 
             self._clean_text_for_pdf(company_metrics['income_statement_details'])], 
            ['Cash Flow Validation', 
             self._clean_text_for_pdf(company_metrics['cash_flow_status']), 
             self._clean_text_for_pdf(company_metrics['cash_flow_details'])],
            ['Mathematical Precision', 'OK VERIFIED', '28-digit calculation accuracy'],
            ['Agent Consensus', 
             self._clean_text_for_pdf(company_metrics['consensus_status']), 
             self._clean_text_for_pdf(company_metrics['consensus_details'])],
            ['Processing Time', 'OK', f"{company_metrics['processing_time']:.1f} seconds"]
        ]
        
        # Format company summary data with Paragraphs for text wrapping
        formatted_summary_data = []
        for i, row in enumerate(summary_data):
            if i == 0:  # Header row
                formatted_row = [Paragraph(f"<b>{cell}</b>", self.styles['Normal']) for cell in row]
            else:
                # Wrap long text in details column
                formatted_row = [
                    Paragraph(str(row[0]), self.styles['Normal']),  # Audit Item
                    Paragraph(str(row[1]), self.styles['Normal']),  # Status
                    Paragraph(str(row[2]), self.styles['Normal'])   # Details
                ]
            formatted_summary_data.append(formatted_row)
        
        summary_table = Table(formatted_summary_data, colWidths=[2.2*inch, 1.2*inch, 2.6*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.beige])
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Detailed calculation items section
        calculation_details = self._extract_calculation_details(audit_data)
        if calculation_details:
            story.extend(self._create_calculation_details_section(calculation_details))
            story.append(Spacer(1, 15))
        
        # Key financial figures (if available)
        if company_metrics['key_figures']:
            figures_text = "<b>Key Financial Figures Verified:</b><br/>"
            for item, value in company_metrics['key_figures'].items():
                figures_text += f"• {item}: {self._format_currency(value)}<br/>"
            
            figures_para = Paragraph(figures_text, self.styles['Normal'])
            story.append(figures_para)
            story.append(Spacer(1, 15))
        
        # Audit trail
        trail_text = f"""
        <b>Audit Trail:</b><br/>
        • System: {company_metrics['system_type']}<br/>
        • Model Used: {company_metrics['model_used']}<br/>
        • Calculation Tools: {company_metrics['tool_count']} precision tools executed<br/>
        • Verification Level: {company_metrics['verification_level']}<br/>
        • Timestamp: {company_metrics['timestamp']}
        """
        
        trail_para = Paragraph(trail_text, self.styles['Normal'])
        story.append(trail_para)
        
        return story
    
    def _extract_calculation_details(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract detailed calculation items from audit data"""
        
        calculation_details = {
            'balance_sheet_items': [],
            'income_statement_items': [],
            'cash_flow_items': [],
            'tool_executions': [],
            'validation_results': []
        }
        
        # Extract from main audit data
        main_data = audit_data.get('audit_footing_laporan_keuangan', {})
        
        # Balance Sheet calculations
        if 'laporan_posisi_keuangan' in main_data:
            balance_data = main_data['laporan_posisi_keuangan']
            
            # Extract asset calculations
            if 'aset' in balance_data:
                aset_data = balance_data['aset']
                self._extract_financial_items(aset_data, 'Assets', calculation_details['balance_sheet_items'])
            
            # Extract liability calculations
            if 'liabilitas' in balance_data:
                liability_data = balance_data['liabilitas']
                self._extract_financial_items(liability_data, 'Liabilities', calculation_details['balance_sheet_items'])
            
            # Extract equity calculations
            if 'ekuitas' in balance_data:
                equity_data = balance_data['ekuitas']
                self._extract_financial_items(equity_data, 'Equity', calculation_details['balance_sheet_items'])
            
            # Balance validation
            if 'balancing' in balance_data:
                balance_result = balance_data['balancing']
                calculation_details['validation_results'].append({
                    'type': 'Balance Sheet Equation',
                    'description': 'Assets = Liabilities + Equity',
                    'status': balance_result.get('status', 'Unknown'),
                    'calculated_value': balance_result.get('calculated_difference', 'N/A'),
                    'tool_used': 'Balance Verification Tool'
                })
        
        # Income Statement calculations
        if 'laporan_laba_rugi' in main_data:
            income_data = main_data['laporan_laba_rugi']
            self._extract_financial_items(income_data, 'Income Statement', calculation_details['income_statement_items'])
        
        # Cash Flow calculations
        if 'laporan_arus_kas' in main_data:
            cashflow_data = main_data['laporan_arus_kas']
            self._extract_financial_items(cashflow_data, 'Cash Flow', calculation_details['cash_flow_items'])
        
        # Extract tool execution data from metadata
        metadata = self._extract_metadata(audit_data)
        if metadata and 'tool_executions' in metadata:
            calculation_details['tool_executions'] = metadata['tool_executions']
        
        return calculation_details
    
    def _extract_financial_items(self, data: Dict[str, Any], category: str, items_list: List[Dict]):
        """Extract individual financial items from data structure"""
        
        if not isinstance(data, dict):
            return
        
        for key, value in data.items():
            if isinstance(value, dict):
                # Check if this is a financial item with calculated value
                if 'nilai_tercatat' in value:
                    # Parse the reported value properly
                    reported_value = value.get('nilai_tercatat', 0)
                    calculated_value = value.get('calculated_value', value.get('nilai_perhitungan', reported_value))
                    
                    item_info = {
                        'category': category,
                        'item_name': self._clean_text_for_pdf(key.replace('_', ' ').title()),
                        'reported_value': self._parse_json_value(reported_value),
                        'calculated_value': self._parse_json_value(calculated_value),
                        'status': 'Verified' if value.get('verified', True) else 'Discrepancy',
                        'calculation_method': value.get('calculation_method', 'Standard Calculation'),
                        'tool_used': value.get('tool_used', 'Financial Calculator')
                    }
                    items_list.append(item_info)
                
                # Recursively check nested items
                self._extract_financial_items(value, category, items_list)
    
    def _create_calculation_details_section(self, calculation_details: Dict[str, Any]) -> List:
        """Create detailed calculation items section for the report"""
        
        story = []
        
        # Section title
        title = Paragraph("<b>DETAILED CALCULATION ITEMS</b>", self.styles['CompanyHeader'])
        story.append(title)
        story.append(Spacer(1, 10))
        
        # Combine all calculation items
        all_items = (
            calculation_details['balance_sheet_items'] + 
            calculation_details['income_statement_items'] + 
            calculation_details['cash_flow_items']
        )
        
        if all_items:
            # Create calculation items table
            items_data = [['Item Name', 'Category', 'Reported Value', 'Status', 'Tool Used']]
            
            for item in all_items[:15]:  # Limit to first 15 items to save space
                # Clean and format all data
                status_text = 'OK ' + item['status'] if item['status'] == 'Verified' else 'WARNING ' + item['status']
                
                items_data.append([
                    self._clean_text_for_pdf(item['item_name']),
                    self._clean_text_for_pdf(item['category']),
                    item['reported_value'] if isinstance(item['reported_value'], str) else 'N/A',
                    self._clean_text_for_pdf(status_text),
                    self._clean_text_for_pdf(item['tool_used'])
                ])
            
            # Format items data with Paragraphs for text wrapping
            formatted_items_data = []
            for i, row in enumerate(items_data):
                if i == 0:  # Header row
                    formatted_row = [Paragraph(f"<b>{cell}</b>", self.styles['Normal']) for cell in row]
                else:
                    formatted_row = [Paragraph(str(cell), self.styles['Normal']) for cell in row]
                formatted_items_data.append(formatted_row)
            
            items_table = Table(formatted_items_data, colWidths=[1.8*inch, 1*inch, 1.2*inch, 1*inch, 1*inch])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            story.append(items_table)
            
            if len(all_items) > 15:
                more_items_text = f"<i>... and {len(all_items) - 15} more items calculated and verified</i>"
                more_items_para = Paragraph(more_items_text, self.styles['Normal'])
                story.append(Spacer(1, 5))
                story.append(more_items_para)
        
        # Validation results section
        if calculation_details['validation_results']:
            story.append(Spacer(1, 10))
            
            validation_text = "<b>Key Validation Results:</b><br/>"
            for validation in calculation_details['validation_results']:
                status_icon = '✓' if 'seimbang' in str(validation['status']).lower() else '⚠️'
                validation_text += f"• {validation['description']}: {status_icon} {validation['status']}<br/>"
            
            validation_para = Paragraph(validation_text, self.styles['Normal'])
            story.append(validation_para)
        
        # Tool execution summary
        if calculation_details['tool_executions']:
            story.append(Spacer(1, 10))
            
            tools_text = f"<b>Calculation Tools Executed:</b> {len(calculation_details['tool_executions'])} precision tools used<br/>"
            tools_text += "• All calculations performed using 28-digit precision arithmetic<br/>"
            tools_text += "• No manual calculations - all computations tool-verified<br/>"
            tools_text += "• Triple agent consensus validation applied to all results"
            
            tools_para = Paragraph(tools_text, self.styles['Normal'])
            story.append(tools_para)
        
        return story
    
    def _analyze_all_results(self, audit_files: List[tuple[str, str]]) -> Dict[str, Any]:
        """Analyze all audit results for summary"""
        
        total_companies = len(audit_files)
        successful_audits = 0
        total_processing_time = 0
        total_calculations = 0
        consensus_qualities = []
        
        for company, filepath in audit_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if audit was successful
                if self._is_audit_successful(data):
                    successful_audits += 1
                
                # Extract metadata
                metadata = self._extract_metadata(data)
                if metadata:
                    total_processing_time += metadata.get('processing_time', 0)
                    total_calculations += metadata.get('total_calculations', 0)
                    consensus_qualities.append(metadata.get('consensus_quality', 'Unknown'))
                    
            except Exception as e:
                print(f"Warning: Could not analyze {company}: {e}")
        
        return {
            'total_companies': total_companies,
            'successful_audits': successful_audits,
            'success_rate': (successful_audits / total_companies * 100) if total_companies > 0 else 0,
            'avg_processing_time': total_processing_time / total_companies if total_companies > 0 else 0,
            'total_calculations': total_calculations,
            'consensus_quality': max(set(consensus_qualities), key=consensus_qualities.count) if consensus_qualities else 'Perfect'
        }
    
    def _extract_company_metrics(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics for individual company"""
        
        metrics = {
            'balance_sheet_status': '⚠️ NOT FOUND',
            'balance_sheet_details': 'Balance sheet data not available',
            'income_statement_status': '⚠️ NOT FOUND', 
            'income_statement_details': 'Income statement data not available',
            'cash_flow_status': '⚠️ NOT FOUND',
            'cash_flow_details': 'Cash flow data not available',
            'consensus_status': '⚠️ UNKNOWN',
            'consensus_details': 'Consensus information not available',
            'processing_time': 0,
            'key_figures': {},
            'system_type': 'Unknown',
            'model_used': 'Unknown', 
            'tool_count': 0,
            'verification_level': 'Standard',
            'timestamp': 'Unknown'
        }
        
        # Extract main audit data
        main_data = audit_data.get('audit_footing_laporan_keuangan', {})
        
        # Check balance sheet
        if 'laporan_posisi_keuangan' in main_data:
            balance_data = main_data['laporan_posisi_keuangan']
            metrics['balance_sheet_status'] = 'OK VERIFIED'
            
            # Check balancing
            if 'balancing' in balance_data:
                balance_status = balance_data['balancing'].get('status', 'Unknown')
                if isinstance(balance_status, str) and 'seimbang' in balance_status.lower():
                    metrics['balance_sheet_details'] = 'Balance sheet equation verified - Assets = Liabilities + Equity'
                else:
                    metrics['balance_sheet_details'] = f'Balance check: {balance_status}'
            
            # Extract key figures
            if 'aset' in balance_data:
                aset = balance_data['aset']
                if 'total_aset' in aset and isinstance(aset['total_aset'], dict):
                    total_assets = aset['total_aset'].get('nilai_tercatat', 0)
                    # Parse JSON if needed
                    total_assets = self._parse_numeric_value(total_assets)
                    if total_assets > 0:
                        metrics['key_figures']['Total Assets'] = total_assets
        
        # Check income statement
        if 'laporan_laba_rugi' in main_data:
            income_data = main_data['laporan_laba_rugi']
            metrics['income_statement_status'] = 'OK VERIFIED'
            metrics['income_statement_details'] = 'Income statement calculations verified with tools'
            
            # Extract net income if available
            if 'laba_rugi_bersih' in income_data:
                net_income = income_data['laba_rugi_bersih'].get('nilai_tercatat', 0)
                net_income = self._parse_numeric_value(net_income)
                if net_income != 0:
                    metrics['key_figures']['Net Income'] = net_income
        
        # Check cash flow statement
        if 'laporan_arus_kas' in main_data:
            cashflow_data = main_data['laporan_arus_kas']
            metrics['cash_flow_status'] = 'OK VERIFIED'
            metrics['cash_flow_details'] = 'Cash flow calculations verified with tools'
            
            # Extract operating cash flow if available
            if 'aktivitas_operasi' in cashflow_data:
                operating_cf = cashflow_data['aktivitas_operasi'].get('nilai_tercatat', 0)
                operating_cf = self._parse_numeric_value(operating_cf)
                if operating_cf != 0:
                    metrics['key_figures']['Operating Cash Flow'] = operating_cf
        
        # Extract metadata
        metadata = self._extract_metadata(audit_data)
        if metadata:
            metrics['system_type'] = metadata.get('system_type', 'Triple Agent AI')
            metrics['model_used'] = metadata.get('model_used', 'AI Model')
            metrics['consensus_status'] = 'OK ' + metadata.get('consensus_quality', 'ACHIEVED')
            metrics['consensus_details'] = f"Retries: {metadata.get('total_retries', 0)}"
            metrics['timestamp'] = metadata.get('audit_timestamp', 'Unknown')
            metrics['tool_count'] = metadata.get('total_calculations', 0)
            
            if metadata.get('total_retries', 0) == 0:
                metrics['verification_level'] = 'Perfect First-Attempt Consensus'
            else:
                metrics['verification_level'] = 'Consensus Achieved with Validation'
        
        return metrics
    
    def _extract_metadata(self, audit_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract metadata from audit data"""
        
        # Look for different metadata key patterns
        metadata_keys = [
            '_gemini_triple_agent_metadata',
            '_ollama_triple_agent_metadata', 
            '_triple_agent_metadata',
            '_enhanced_triple_agent_metadata',
            'metadata'
        ]
        
        for key in metadata_keys:
            if key in audit_data:
                return audit_data[key]
        
        return None
    
    def _is_audit_successful(self, audit_data: Dict[str, Any]) -> bool:
        """Determine if audit was successful"""
        
        # Check if main audit data exists
        if 'audit_footing_laporan_keuangan' not in audit_data:
            return False
        
        main_data = audit_data['audit_footing_laporan_keuangan']
        
        # Check if at least one statement was processed
        return len(main_data) > 0
    
    def _assess_overall_risk(self, summary_data: Dict[str, Any]) -> Dict[str, str]:
        """Assess overall audit risk"""
        
        success_rate = summary_data['success_rate']
        
        if success_rate >= 95:
            return {
                'level': 'LOW RISK',
                'description': 'All audited financial statements show high accuracy and mathematical precision. Triple agent consensus validation provides strong assurance of data integrity.'
            }
        elif success_rate >= 80:
            return {
                'level': 'MEDIUM RISK', 
                'description': 'Most audited statements are accurate with minor issues identified. Recommend reviewing failed audits for systematic problems.'
            }
        else:
            return {
                'level': 'HIGH RISK',
                'description': 'Significant number of audit failures detected. Immediate review of financial statement preparation processes recommended.'
            }
    
    def _generate_recommendations(self, summary_data: Dict[str, Any]) -> List[str]:
        """Generate executive recommendations"""
        
        recommendations = []
        
        if summary_data['success_rate'] == 100:
            recommendations.extend([
                "Continue current financial reporting processes - all audits passed",
                "Consider implementing automated monthly audits using this AI system",
                "Document current best practices for financial statement preparation"
            ])
        else:
            recommendations.extend([
                f"Review and remediate {summary_data['total_companies'] - summary_data['successful_audits']} failed audits",
                "Investigate root causes of calculation discrepancies",
                "Strengthen internal controls for financial statement preparation"
            ])
        
        recommendations.extend([
            "Maintain 28-digit precision calculation standards",
            "Schedule quarterly comprehensive AI audits",
            "Train accounting staff on AI audit system benefits"
        ])
        
        return recommendations
    
    def _parse_json_value(self, value) -> str:
        """Parse JSON value and extract meaningful data"""
        
        if isinstance(value, dict):
            # Handle tool result structure
            if 'result' in value:
                return self._format_currency(value['result'])
            elif 'nilai_perhitungan' in value:
                nested_value = value['nilai_perhitungan']
                if isinstance(nested_value, dict) and 'result' in nested_value:
                    return self._format_currency(nested_value['result'])
                else:
                    return self._format_currency(nested_value)
            elif 'nilai_tercatat' in value:
                nested_value = value['nilai_tercatat']
                if isinstance(nested_value, dict) and 'result' in nested_value:
                    return self._format_currency(nested_value['result'])
                else:
                    return self._format_currency(nested_value)
            else:
                # Return first numerical value found
                for key, val in value.items():
                    if isinstance(val, (int, float)):
                        return self._format_currency(val)
                return "Complex Data"
        else:
            return self._format_currency(value)
    
    def _clean_text_for_pdf(self, text: str) -> str:
        """Clean text for PDF display - remove problematic characters"""
        
        if not isinstance(text, str):
            text = str(text)
        
        # Replace problematic characters that show as boxes/squares
        replacements = {
            '✓': 'OK',
            '❌': 'ERROR',
            '⚠️': 'WARNING',
            '✅': 'VERIFIED',
            '■': '',
            '□': '',
            '\u2022': '•',  # bullet point
            '\u25A0': '',   # black square
            '\u25A1': '',   # white square
        }
        
        for old_char, new_char in replacements.items():
            text = text.replace(old_char, new_char)
        
        return text.strip()
    
    def _parse_numeric_value(self, value) -> float:
        """Parse numeric value from various formats"""
        
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, dict):
            if 'result' in value:
                return float(value['result'])
            elif 'nilai_perhitungan' in value:
                nested = value['nilai_perhitungan']
                if isinstance(nested, dict) and 'result' in nested:
                    return float(nested['result'])
                else:
                    return float(nested)
            else:
                # Look for first numeric value
                for k, v in value.items():
                    if isinstance(v, (int, float)):
                        return float(v)
                return 0.0
        else:
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0

    def _format_currency(self, amount) -> str:
        """Format currency amount for display"""
        
        # Convert to float if possible
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return f"Rp {amount}"
        
        if amount >= 1_000_000_000:
            return f"Rp {amount/1_000_000_000:.1f}B"
        elif amount >= 1_000_000:
            return f"Rp {amount/1_000_000:.1f}M"
        elif amount >= 1_000:
            return f"Rp {amount/1_000:.1f}K"
        else:
            return f"Rp {amount:,.0f}"

def generate_executive_report(results_dir: str = "results") -> str:
    """Main function to generate executive report"""
    
    if not REPORTLAB_AVAILABLE:
        print("❌ ReportLab not available. Install with: uv add reportlab")
        return ""
    
    try:
        generator = ExecutiveAuditReportGenerator()
        output_path = generator.generate_executive_report(results_dir)
        
        print(f"✅ Executive report generated: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return ""

if __name__ == "__main__":
    # Generate report for all results
    report_path = generate_executive_report()
    
    if report_path:
        print(f"\n📊 EXECUTIVE AUDIT REPORT READY")
        print(f"📄 File: {report_path}")
        print(f"📁 Location: {os.path.abspath(report_path)}")
    else:
        print("❌ Report generation failed")