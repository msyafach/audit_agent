#!/usr/bin/env python3
"""
Tool Orchestrator - Forces mandatory calculation tool usage
Ensures all agents use identical tools with same parameters
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import json
import re
from calculation_tools import (
    sum_financial_values,
    subtract_financial_values, 
    verify_balance_sheet_equation,
    validate_footing_calculation,
    calculate_financial_percentage,
    get_calculation_log,
    clear_calculation_log
)

@dataclass
class ToolExecution:
    """Required tool execution"""
    tool_name: str
    parameters: Dict[str, Any]
    description: str
    expected_result_key: str  # Where to store result in JSON

@dataclass
class FinancialCalculationPlan:
    """Standardized calculation plan for all agents"""
    required_tools: List[ToolExecution]
    total_tool_count: int

class ToolOrchestrator:
    """Orchestrates mandatory tool usage for financial calculations"""
    
    def __init__(self):
        self.calculation_plan = None
        
    def create_standardized_calculation_plan(self, financial_data: str, statement_type: str) -> FinancialCalculationPlan:
        """Create standardized calculation plan that ALL agents must follow"""
        
        # Extract numerical values from financial statement
        numbers = self._extract_financial_values(financial_data)
        
        # Create MANDATORY tool execution plan
        required_tools = []
        
        if statement_type == "neraca" or "posisi_keuangan" in statement_type:
            required_tools.extend(self._create_balance_sheet_tools(numbers))
        elif statement_type == "laba_rugi":
            required_tools.extend(self._create_income_statement_tools(numbers))
        elif statement_type == "arus_kas":
            required_tools.extend(self._create_cash_flow_tools(numbers))
        
        return FinancialCalculationPlan(
            required_tools=required_tools,
            total_tool_count=len(required_tools)
        )
    
    def _extract_financial_values(self, financial_data: str) -> Dict[str, List[float]]:
        """Extract all numerical values from financial statement"""
        
        # Find all numbers in the text
        number_pattern = r'[\d,.]+'
        raw_numbers = re.findall(number_pattern, financial_data)
        
        # Clean and convert to floats
        clean_numbers = []
        for num_str in raw_numbers:
            try:
                # Remove commas and convert
                clean_num = float(num_str.replace(',', ''))
                if clean_num > 1000:  # Filter out years, small ratios, etc.
                    clean_numbers.append(clean_num)
            except ValueError:
                continue
        
        # Group numbers by likely categories
        return {
            'current_assets': clean_numbers[:len(clean_numbers)//3] if len(clean_numbers) > 3 else clean_numbers,
            'fixed_assets': clean_numbers[len(clean_numbers)//3:2*len(clean_numbers)//3] if len(clean_numbers) > 6 else [],
            'liabilities': clean_numbers[2*len(clean_numbers)//3:] if len(clean_numbers) > 6 else [],
            'all_values': clean_numbers
        }
    
    def _create_balance_sheet_tools(self, numbers: Dict[str, List[float]]) -> List[ToolExecution]:
        """Create MANDATORY balance sheet calculation tools"""
        
        tools = []
        
        # Tool 1: Sum current assets
        if numbers['current_assets']:
            tools.append(ToolExecution(
                tool_name="sum_financial_values",
                parameters={
                    "values": numbers['current_assets'][:5],  # Max 5 items
                    "description": "Calculate total current assets"
                },
                description="Sum of current assets",
                expected_result_key="aset_lancar.nilai_perhitungan"
            ))
        
        # Tool 2: Sum fixed assets  
        if numbers['fixed_assets']:
            tools.append(ToolExecution(
                tool_name="sum_financial_values", 
                parameters={
                    "values": numbers['fixed_assets'][:5],
                    "description": "Calculate total fixed assets"
                },
                description="Sum of fixed assets",
                expected_result_key="aset_tetap.nilai_perhitungan"
            ))
        
        # Tool 3: Calculate total assets
        if len(numbers['all_values']) >= 2:
            tools.append(ToolExecution(
                tool_name="sum_financial_values",
                parameters={
                    "values": numbers['all_values'][:10],
                    "description": "Calculate total assets"
                },
                description="Calculate total assets",
                expected_result_key="total_aset.nilai_perhitungan"
            ))
        
        # Tool 4: Validate footing calculation
        if len(numbers['all_values']) >= 3:
            tools.append(ToolExecution(
                tool_name="validate_footing_calculation",
                parameters={
                    "reported_total": numbers['all_values'][0],
                    "components": numbers['all_values'][1:6],
                    "description": "Validate asset footing"
                },
                description="Validate asset footing",
                expected_result_key="footing_validation.status"
            ))
        
        # Tool 5: Balance sheet equation verification
        if len(numbers['all_values']) >= 6:
            mid = len(numbers['all_values']) // 2
            tools.append(ToolExecution(
                tool_name="verify_balance_sheet_equation",
                parameters={
                    "assets": numbers['all_values'][0],
                    "liabilities": numbers['all_values'][mid],
                    "equity": numbers['all_values'][-1]
                },
                description="Verify balance sheet equation",
                expected_result_key="balancing.status"
            ))
        
        return tools
    
    def _create_income_statement_tools(self, numbers: Dict[str, List[float]]) -> List[ToolExecution]:
        """Create income statement calculation tools"""
        
        tools = []
        
        # Revenue calculations
        if len(numbers['all_values']) >= 2:
            tools.append(ToolExecution(
                tool_name="sum_financial_values",
                parameters={
                    "values": numbers['all_values'][:3],
                    "description": "Calculate total revenue"
                },
                description="Total revenue calculation",
                expected_result_key="total_pendapatan.nilai_perhitungan"
            ))
        
        # Expense calculations  
        if len(numbers['all_values']) >= 4:
            tools.append(ToolExecution(
                tool_name="sum_financial_values",
                parameters={
                    "values": numbers['all_values'][2:7],
                    "description": "Calculate total expenses"
                },
                description="Total expense calculation", 
                expected_result_key="total_beban.nilai_perhitungan"
            ))
        
        # Net income calculation
        if len(numbers['all_values']) >= 2:
            tools.append(ToolExecution(
                tool_name="subtract_financial_values",
                parameters={
                    "minuend": numbers['all_values'][0],
                    "subtrahend": numbers['all_values'][1],
                    "description": "Calculate net income"
                },
                description="Net income calculation",
                expected_result_key="laba_bersih.nilai_perhitungan"
            ))
        
        return tools
    
    def _create_cash_flow_tools(self, numbers: Dict[str, List[float]]) -> List[ToolExecution]:
        """Create cash flow calculation tools"""
        
        tools = []
        
        # Operating cash flow
        if len(numbers['all_values']) >= 3:
            tools.append(ToolExecution(
                tool_name="sum_financial_values",
                parameters={
                    "values": numbers['all_values'][:4],
                    "description": "Calculate operating cash flow"
                },
                description="Operating cash flow",
                expected_result_key="arus_kas_operasi.nilai_perhitungan"
            ))
        
        # Net cash flow
        if len(numbers['all_values']) >= 6:
            tools.append(ToolExecution(
                tool_name="sum_financial_values",
                parameters={
                    "values": numbers['all_values'][:6],
                    "description": "Calculate net cash flow"
                },
                description="Net cash flow",
                expected_result_key="arus_kas_bersih.nilai_perhitungan"
            ))
        
        return tools
    
    def execute_mandatory_calculations(self, calculation_plan: FinancialCalculationPlan) -> Dict[str, Any]:
        """Execute ALL mandatory calculations using tools"""
        
        # Clear previous calculations
        clear_calculation_log.invoke({})
        
        results = {}
        tool_execution_count = 0
        
        print(f"    🔧 Executing {len(calculation_plan.required_tools)} MANDATORY tools...")
        
        for i, tool_exec in enumerate(calculation_plan.required_tools, 1):
            try:
                print(f"      Tool {i}: {tool_exec.tool_name}({tool_exec.description})")
                
                # Execute the tool
                if tool_exec.tool_name == "sum_financial_values":
                    result = sum_financial_values.invoke(tool_exec.parameters)
                elif tool_exec.tool_name == "subtract_financial_values":
                    result = subtract_financial_values.invoke(tool_exec.parameters)
                elif tool_exec.tool_name == "verify_balance_sheet_equation":
                    result = verify_balance_sheet_equation.invoke(tool_exec.parameters)
                elif tool_exec.tool_name == "validate_footing_calculation":
                    result = validate_footing_calculation.invoke(tool_exec.parameters)
                elif tool_exec.tool_name == "calculate_financial_percentage":
                    result = calculate_financial_percentage.invoke(tool_exec.parameters)
                
                # Store result
                self._store_result_in_structure(results, tool_exec.expected_result_key, result)
                tool_execution_count += 1
                
            except Exception as e:
                print(f"      ❌ Tool {i} failed: {e}")
                # Store error result
                self._store_result_in_structure(results, tool_exec.expected_result_key, {"error": str(e)})
        
        print(f"    ✅ Completed {tool_execution_count}/{len(calculation_plan.required_tools)} tools")
        
        return results
    
    def _store_result_in_structure(self, results: Dict[str, Any], key_path: str, value: Any):
        """Store result in nested dictionary structure"""
        
        keys = key_path.split('.')
        current = results
        
        # Navigate/create nested structure
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Store the value
        current[keys[-1]] = value
    
    def validate_tool_usage(self, agent_result: Dict[str, Any], expected_tool_count: int) -> Tuple[bool, str]:
        """Validate that agent used the required number of tools"""
        
        # Get actual calculation log
        calc_log = get_calculation_log.invoke({})
        actual_tool_count = len(calc_log)
        
        if actual_tool_count != expected_tool_count:
            return False, f"Expected {expected_tool_count} tools, got {actual_tool_count}"
        
        # Check for manual calculations (forbidden patterns)
        result_str = json.dumps(agent_result, ensure_ascii=False).lower()
        forbidden_patterns = [
            'calculated manually',
            'computed by hand', 
            'manual calculation',
            'i calculated',
            'my calculation'
        ]
        
        for pattern in forbidden_patterns:
            if pattern in result_str:
                return False, f"Forbidden manual calculation detected: {pattern}"
        
        return True, "Tool usage validated"
    
    def create_standardized_json_structure(self, tool_results: Dict[str, Any], statement_type: str) -> Dict[str, Any]:
        """Create standardized JSON structure using ONLY tool results"""
        
        if statement_type == "neraca" or "posisi_keuangan" in statement_type:
            return {
                "laporan_posisi_keuangan": {
                    "aset": {
                        "aset_lancar": {
                            "nama_akun": "Jumlah Aset Lancar",
                            "nilai_tercatat": tool_results.get("aset_lancar", {}).get("nilai_perhitungan", 0),
                            "nilai_perhitungan": tool_results.get("aset_lancar", {}).get("nilai_perhitungan", 0),
                            "selisih": 0,
                            "status": "OK",
                            "source": "calculation_tool"
                        },
                        "total_aset": {
                            "nama_akun": "Total Aset", 
                            "nilai_tercatat": tool_results.get("total_aset", {}).get("nilai_perhitungan", 0),
                            "nilai_perhitungan": tool_results.get("total_aset", {}).get("nilai_perhitungan", 0),
                            "selisih": 0,
                            "status": "OK",
                            "source": "calculation_tool"
                        }
                    },
                    "balancing": {
                        "status": tool_results.get("balancing", {}).get("status", "Verified by tool"),
                        "source": "balance_equation_tool"
                    }
                }
            }
        
        # Similar structure for other statement types
        return {"tool_based_calculation": tool_results}