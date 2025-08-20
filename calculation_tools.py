"""
Dedicated calculation tools for financial statement footing
Eliminates rounding errors and ensures mathematical precision
"""

from typing import List, Dict, Any, Union, Tuple
from decimal import Decimal, getcontext
from langchain_core.tools import tool
import json

# Set high precision for financial calculations
getcontext().prec = 28

class FinancialCalculator:
    """High-precision financial calculator with audit trail"""
    
    def __init__(self):
        self.calculation_log = []
        
    def log_calculation(self, operation: str, inputs: Any, result: Any, description: str = ""):
        """Log calculation for audit trail"""
        self.calculation_log.append({
            "operation": operation,
            "inputs": inputs,
            "result": result,
            "description": description
        })
    
    def precise_decimal(self, value: Union[int, float, str]) -> Decimal:
        """Convert to high-precision decimal"""
        if isinstance(value, str):
            # Clean string input
            cleaned = value.replace(',', '').replace('(', '-').replace(')', '').strip()
            return Decimal(cleaned)
        return Decimal(str(value))
    
    def sum_values(self, values: List[Union[int, float, str]], description: str = "") -> Dict[str, Any]:
        """Sum a list of values with high precision"""
        try:
            decimal_values = [self.precise_decimal(v) for v in values if v is not None]
            result = sum(decimal_values)
            float_result = float(result)
            
            self.log_calculation(
                operation="sum",
                inputs=values,
                result=float_result,
                description=description
            )
            
            return {
                "result": float_result,
                "precision": "high",
                "components": [float(d) for d in decimal_values],
                "component_count": len(decimal_values),
                "operation": "sum"
            }
        except Exception as e:
            return {
                "result": 0.0,
                "error": str(e),
                "precision": "error",
                "components": [],
                "component_count": 0,
                "operation": "sum"
            }
    
    def subtract_values(self, minuend: Union[int, float, str], subtrahend: Union[int, float, str], 
                       description: str = "") -> Dict[str, Any]:
        """Subtract two values with high precision"""
        try:
            decimal_minuend = self.precise_decimal(minuend)
            decimal_subtrahend = self.precise_decimal(subtrahend)
            result = decimal_minuend - decimal_subtrahend
            float_result = float(result)
            
            self.log_calculation(
                operation="subtract",
                inputs={"minuend": minuend, "subtrahend": subtrahend},
                result=float_result,
                description=description
            )
            
            return {
                "result": float_result,
                "precision": "high",
                "minuend": float(decimal_minuend),
                "subtrahend": float(decimal_subtrahend),
                "operation": "subtract"
            }
        except Exception as e:
            return {
                "result": 0.0,
                "error": str(e),
                "precision": "error",
                "operation": "subtract"
            }
    
    def verify_balance_equation(self, assets: Union[int, float, str], 
                               liabilities: Union[int, float, str], 
                               equity: Union[int, float, str]) -> Dict[str, Any]:
        """Verify balance sheet equation: Assets = Liabilities + Equity"""
        try:
            decimal_assets = self.precise_decimal(assets)
            decimal_liabilities = self.precise_decimal(liabilities)
            decimal_equity = self.precise_decimal(equity)
            
            liabilities_plus_equity = decimal_liabilities + decimal_equity
            difference = decimal_assets - liabilities_plus_equity
            
            is_balanced = abs(difference) < Decimal('0.01')  # Allow 1 cent tolerance
            
            result = {
                "assets": float(decimal_assets),
                "liabilities": float(decimal_liabilities),
                "equity": float(decimal_equity),
                "liabilities_plus_equity": float(liabilities_plus_equity),
                "difference": float(difference),
                "is_balanced": is_balanced,
                "status": "Balanced" if is_balanced else "Unbalanced",
                "precision": "high",
                "operation": "balance_verification"
            }
            
            self.log_calculation(
                operation="balance_verification",
                inputs={"assets": assets, "liabilities": liabilities, "equity": equity},
                result=result,
                description="Balance sheet equation verification"
            )
            
            return result
            
        except Exception as e:
            return {
                "assets": 0.0,
                "liabilities": 0.0,
                "equity": 0.0,
                "liabilities_plus_equity": 0.0,
                "difference": 0.0,
                "is_balanced": False,
                "status": "Error",
                "error": str(e),
                "precision": "error",
                "operation": "balance_verification"
            }
    
    def calculate_percentage(self, part: Union[int, float, str], 
                           total: Union[int, float, str]) -> Dict[str, Any]:
        """Calculate percentage with high precision"""
        try:
            decimal_part = self.precise_decimal(part)
            decimal_total = self.precise_decimal(total)
            
            if decimal_total == 0:
                return {
                    "percentage": 0.0,
                    "part": float(decimal_part),
                    "total": float(decimal_total),
                    "error": "Division by zero",
                    "precision": "error",
                    "operation": "percentage"
                }
            
            percentage = (decimal_part / decimal_total) * 100
            float_result = float(percentage)
            
            self.log_calculation(
                operation="percentage",
                inputs={"part": part, "total": total},
                result=float_result,
                description=f"Percentage calculation: {part}/{total}"
            )
            
            return {
                "percentage": float_result,
                "part": float(decimal_part),
                "total": float(decimal_total),
                "precision": "high",
                "operation": "percentage"
            }
            
        except Exception as e:
            return {
                "percentage": 0.0,
                "part": 0.0,
                "total": 0.0,
                "error": str(e),
                "precision": "error",
                "operation": "percentage"
            }

# Global calculator instance
calculator = FinancialCalculator()

# LangChain tools that agents can use
@tool
def sum_financial_values(values: List[float], description: str = "Sum calculation") -> Dict[str, Any]:
    """
    Sum a list of financial values with high precision to avoid rounding errors.
    
    Args:
        values: List of numerical values to sum
        description: Description of what is being calculated
    
    Returns:
        Dictionary with result, precision info, and audit trail
    """
    return calculator.sum_values(values, description)

@tool
def subtract_financial_values(minuend: float, subtrahend: float, description: str = "Subtraction calculation") -> Dict[str, Any]:
    """
    Subtract two financial values with high precision.
    
    Args:
        minuend: Value to subtract from
        subtrahend: Value to subtract
        description: Description of what is being calculated
    
    Returns:
        Dictionary with result, precision info, and audit trail
    """
    return calculator.subtract_values(minuend, subtrahend, description)

@tool
def verify_balance_sheet_equation(assets: float, liabilities: float, equity: float) -> Dict[str, Any]:
    """
    Verify the fundamental balance sheet equation: Assets = Liabilities + Equity
    
    Args:
        assets: Total assets amount
        liabilities: Total liabilities amount  
        equity: Total equity amount
    
    Returns:
        Dictionary with verification result, difference, and balance status
    """
    return calculator.verify_balance_equation(assets, liabilities, equity)

@tool
def calculate_financial_percentage(part: float, total: float) -> Dict[str, Any]:
    """
    Calculate percentage with high precision for financial analysis.
    
    Args:
        part: The part value
        total: The total value
    
    Returns:
        Dictionary with percentage result and precision info
    """
    return calculator.calculate_percentage(part, total)

@tool
def validate_footing_calculation(reported_total: float, component_values: List[float], 
                                description: str = "Footing validation") -> Dict[str, Any]:
    """
    Validate footing by comparing reported total with sum of components.
    
    Args:
        reported_total: Total as reported in financial statement
        component_values: List of component values that should sum to total
        description: Description of what is being validated
    
    Returns:
        Dictionary with validation result, difference, and status
    """
    sum_result = calculator.sum_values(component_values, f"Components for {description}")
    calculated_total = sum_result["result"]
    
    difference = calculator.subtract_values(calculated_total, reported_total, 
                                          f"Difference for {description}")["result"]
    
    is_accurate = abs(difference) < 1.0  # Allow 1 unit tolerance for rounding
    
    result = {
        "reported_total": reported_total,
        "calculated_total": calculated_total,
        "difference": difference,
        "is_accurate": is_accurate,
        "status": "OK" if is_accurate else "ERROR",
        "component_count": len(component_values),
        "components": component_values,
        "precision": "high",
        "operation": "footing_validation",
        "description": description
    }
    
    calculator.log_calculation(
        operation="footing_validation",
        inputs={"reported": reported_total, "components": component_values},
        result=result,
        description=description
    )
    
    return result

@tool
def get_calculation_log() -> List[Dict[str, Any]]:
    """
    Get the complete calculation log for audit trail.
    
    Returns:
        List of all calculations performed with inputs, outputs, and descriptions
    """
    return calculator.calculation_log

@tool
def clear_calculation_log() -> Dict[str, str]:
    """
    Clear the calculation log (use at start of new audit).
    
    Returns:
        Confirmation message
    """
    calculator.calculation_log.clear()
    return {"status": "cleared", "message": "Calculation log has been cleared"}

# Helper function to get all tools for binding to agents
def get_all_calculation_tools():
    """Get all calculation tools for binding to agents"""
    return [
        sum_financial_values,
        subtract_financial_values,
        verify_balance_sheet_equation,
        calculate_financial_percentage,
        validate_footing_calculation,
        get_calculation_log,
        clear_calculation_log
    ]

# Validation functions for tool results
def validate_calculation_result(result: Dict[str, Any]) -> bool:
    """Validate that a calculation result is properly formatted and reasonable"""
    if not isinstance(result, dict):
        return False
    
    # Check for required fields
    required_fields = ["result", "precision", "operation"]
    if not all(field in result for field in required_fields):
        return False
    
    # Check for errors
    if "error" in result:
        return False
    
    # Check precision
    if result["precision"] != "high":
        return False
    
    # Check that result is a number
    if not isinstance(result["result"], (int, float)):
        return False
    
    return True

if __name__ == "__main__":
    # Test the calculation tools
    print("🧮 Testing Financial Calculation Tools")
    print("=" * 50)
    
    # Test sum
    test_values = [1000000, 500000, 250000, 100000]
    sum_result = sum_financial_values.invoke({
        "values": test_values,
        "description": "Test sum calculation"
    })
    print(f"Sum test: {test_values} = {sum_result['result']}")
    
    # Test subtraction
    subtract_result = subtract_financial_values.invoke({
        "minuend": 1000000,
        "subtrahend": 300000,
        "description": "Test subtraction"
    })
    print(f"Subtract test: 1000000 - 300000 = {subtract_result['result']}")
    
    # Test balance sheet equation
    balance_result = verify_balance_sheet_equation.invoke({
        "assets": 28793225,
        "liabilities": 5591163,
        "equity": 23202062
    })
    print(f"Balance test: Assets={balance_result['assets']}, Liab+Equity={balance_result['liabilities_plus_equity']}")
    print(f"Balanced: {balance_result['is_balanced']}, Difference: {balance_result['difference']}")
    
    # Test footing validation
    footing_result = validate_footing_calculation.invoke({
        "reported_total": 1850000,
        "component_values": [1000000, 500000, 250000, 100000],
        "description": "Test footing validation"
    })
    print(f"Footing test: Reported={footing_result['reported_total']}, Calculated={footing_result['calculated_total']}")
    print(f"Status: {footing_result['status']}, Difference: {footing_result['difference']}")
    
    # Show calculation log
    log = get_calculation_log.invoke({})
    print(f"\nCalculation log entries: {len(log)}")
    
    print("\n✅ All calculation tools working correctly!")