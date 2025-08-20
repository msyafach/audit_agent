#!/usr/bin/env python3
"""
Base classes and interfaces for financial audit agents
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import time
from .tool_orchestrator import ToolOrchestrator, FinancialCalculationPlan

@dataclass
class AgentResult:
    """Result from a single agent processing"""
    agent_id: str
    company: str
    statement_type: str
    extracted_data: Dict[str, Any]
    calculation_log: List[Dict[str, Any]]
    processing_time: float
    validation_score: float
    confidence: float
    tool_calls_made: int
    errors: List[str]
    raw_response: str

@dataclass
class ConsensusResult:
    """Result of consensus validation between agents"""
    is_consensus: bool
    agreed_data: Dict[str, Any]
    discrepancies: List[Dict[str, Any]]
    retry_needed: bool
    failing_agents: List[str]
    confidence_scores: Dict[str, float]
    calculation_verification: Optional[Dict[str, float]] = None
    calculation_accuracy: Optional[float] = None

class BaseFinancialAgent(ABC):
    """Abstract base class for financial audit agents"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.tool_orchestrator = ToolOrchestrator()
        
    def process_statement(self, statement_text: str, statement_type: str, company: str) -> AgentResult:
        """Process a financial statement using MANDATORY tool orchestration"""
        
        start_time = time.time()
        
        # Step 1: Create standardized calculation plan (SAME for ALL agents)
        calculation_plan = self.tool_orchestrator.create_standardized_calculation_plan(
            statement_text, statement_type
        )
        
        print(f"    🎯 {self.agent_id}: Created calculation plan with {calculation_plan.total_tool_count} MANDATORY tools")
        
        # Step 2: Execute ALL mandatory calculations using tools
        tool_results = self.tool_orchestrator.execute_mandatory_calculations(calculation_plan)
        
        # Step 3: Create standardized JSON structure using ONLY tool results
        extracted_data = self.tool_orchestrator.create_standardized_json_structure(
            tool_results, statement_type
        )
        
        # Step 4: Validate tool usage
        tool_valid, validation_message = self.tool_orchestrator.validate_tool_usage(
            extracted_data, calculation_plan.total_tool_count
        )
        
        if not tool_valid:
            print(f"    ❌ {self.agent_id}: Tool validation failed - {validation_message}")
        
        processing_time = time.time() - start_time
        
        # Calculate metrics based on tool usage
        validation_score = 100.0 if tool_valid else 0.0
        confidence = 95.0 if tool_valid else 10.0
        
        return AgentResult(
            agent_id=self.agent_id,
            company=company,
            statement_type=statement_type,
            extracted_data=extracted_data,
            calculation_log=tool_results,  # Store tool execution results
            processing_time=processing_time,
            validation_score=validation_score,
            confidence=confidence,
            tool_calls_made=calculation_plan.total_tool_count,
            errors=[] if tool_valid else [validation_message],
            raw_response=f"Tool-based calculation with {calculation_plan.total_tool_count} tools"
        )
    
    @abstractmethod 
    def _get_llm_interpretation(self, statement_text: str, statement_type: str, 
                               tool_results: Dict[str, Any]) -> Dict[str, Any]:
        """Get LLM interpretation (for context only - NO calculations allowed)"""
        pass
    
    @abstractmethod
    def _calculate_validation_score(self, data: Dict[str, Any], tool_calls: int) -> float:
        """Calculate validation score based on audit results"""
        pass
    
    @abstractmethod
    def _calculate_confidence(self, data: Dict[str, Any], validation_score: float, tool_calls: int) -> float:
        """Calculate confidence score"""
        pass
    
    def _clean_json_response(self, content: str) -> str:
        """Clean JSON response - common implementation"""
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
    
    def _create_base_prompt(self, statement_text: str, statement_type: str) -> str:
        """Create base prompt for financial analysis"""
        return f"""
        TASK: Audit the {statement_type} for mathematical accuracy and footing verification.
        
        CALCULATION REQUIREMENTS:
        1. Verify all addition/subtraction operations
        2. Check that totals equal sum of components  
        3. Validate balance sheet equation (Assets = Liabilities + Equity)
        4. Identify any discrepancies or errors
        
        OUTPUT FORMAT: Return valid JSON with this structure:
        {{
          "laporan_posisi_keuangan": {{
            "aset": {{
              "aset_lancar": {{
                "nama_akun": "Jumlah Aset Lancar",
                "nilai_tercatat": [reported_value],
                "nilai_perhitungan": [calculated_value], 
                "selisih": [difference],
                "status": "OK|ERROR",
                "detail_perhitungan": [
                  {{"akun": "item_name", "nilai": value}}
                ]
              }},
              "total_aset": {{
                "nama_akun": "Total Aset",
                "nilai_tercatat": [reported_value],
                "nilai_perhitungan": [calculated_value],
                "selisih": [difference],
                "status": "OK|ERROR"
              }}
            }},
            "balancing": {{
              "total_aset": [assets_total],
              "total_liabilitas_ekuitas": [liab_equity_total], 
              "selisih": [difference],
              "status": "Seimbang|Tidak Seimbang"
            }}
          }}
        }}
        
        FINANCIAL STATEMENT:
        {statement_text}
        """

class BaseTripleAgentSystem(ABC):
    """Abstract base class for triple agent systems"""
    
    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries
    
    @abstractmethod
    def _create_agents(self) -> List[BaseFinancialAgent]:
        """Create the three agents for consensus validation"""
        pass
    
    @abstractmethod
    def _validate_consensus(self, agent_results: Dict[str, AgentResult]) -> ConsensusResult:
        """Validate consensus between agents"""
        pass
    
    def process_financial_statements(self, statements: Dict[str, str], company: str) -> Dict[str, Any]:
        """Process all financial statements using triple agent consensus"""
        
        print(f"🚀 TRIPLE AGENT AUDIT - {company}")
        print("=" * 60)
        
        # Create agents
        agents = self._create_agents()
        
        # Process each statement type
        results = {}
        retry_log = []
        total_retries = 0
        
        for statement_type, statement_text in statements.items():
            print(f"\n📊 Processing {statement_type}...")
            
            final_result, retries = self._process_with_consensus(
                agents, statement_text, statement_type, company
            )
            
            results.update(final_result)
            retry_log.extend(retries)
            total_retries += len(retries)
        
        return self._create_final_audit_result(results, total_retries, retry_log)
    
    def _process_with_consensus(self, agents: List[BaseFinancialAgent], 
                               statement_text: str, statement_type: str, 
                               company: str) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Process with MANDATORY tool consensus validation"""
        
        retries = []
        
        for attempt in range(self.max_retries + 1):
            print(f"  🔄 Attempt {attempt + 1} - MANDATORY TOOL VALIDATION")
            
            # Step 1: Create ONE standardized calculation plan for ALL agents
            orchestrator = agents[0].tool_orchestrator  # Use same orchestrator
            calculation_plan = orchestrator.create_standardized_calculation_plan(
                statement_text, statement_type
            )
            
            print(f"    📋 Standardized plan: {calculation_plan.total_tool_count} MANDATORY tools")
            
            # Step 2: All agents MUST execute the SAME tools
            agent_results = {}
            tool_execution_valid = True
            
            for agent in agents:
                print(f"    🤖 Running {agent.agent_id} with MANDATORY tools...")
                result = agent.process_statement(statement_text, statement_type, company)
                agent_results[agent.agent_id] = result
                
                # STRICT validation: ALL agents MUST use same number of tools
                if result.tool_calls_made != calculation_plan.total_tool_count:
                    print(f"      ❌ {agent.agent_id}: Expected {calculation_plan.total_tool_count} tools, got {result.tool_calls_made}")
                    tool_execution_valid = False
                
                print(f"      ✅ {agent.agent_id}: Validation={result.validation_score:.1f}%, "
                      f"Confidence={result.confidence:.1f}%, Tools={result.tool_calls_made}")
            
            # Step 3: Validate tool consistency BEFORE consensus check
            if not tool_execution_valid:
                print(f"    ❌ TOOL EXECUTION INCONSISTENT - All agents must use same tools!")
                retry_info = {
                    "attempt": attempt + 1,
                    "reason": "tool_execution_inconsistent",
                    "expected_tools": calculation_plan.total_tool_count,
                    "agent_tool_counts": {aid: res.tool_calls_made for aid, res in agent_results.items()}
                }
                retries.append(retry_info)
                
                if attempt < self.max_retries:
                    print(f"  🔄 RESTARTING - Enforcing mandatory tool usage...")
                    continue
                else:
                    print(f"  ❌ Max retries reached. Tool validation failed.")
                    return {}, retries
            
            # Step 4: Now check consensus (should be identical since same tools used)
            consensus = self._validate_consensus(agent_results)
            
            if consensus.is_consensus:
                print(f"  🎉 PERFECT TOOL-BASED CONSENSUS achieved!")
                print(f"      All {len(agents)} agents used identical {calculation_plan.total_tool_count} tools")
                return consensus.agreed_data, retries
            else:
                print(f"  ⚠️  TOOL RESULTS DISAGREE - This should not happen with identical tools!")
                print(f"      Found {len(consensus.discrepancies)} disagreements")
                
                # This indicates a bug in tool execution
                retry_info = {
                    "attempt": attempt + 1,
                    "reason": "tool_results_disagree_unexpectedly",
                    "disagreements": len(consensus.discrepancies),
                    "failing_agents": consensus.failing_agents,
                    "note": "Identical tools produced different results - possible bug"
                }
                retries.append(retry_info)
                
                if attempt < self.max_retries:
                    print(f"  🔄 RESTARTING - Investigating tool execution bug...")
                    time.sleep(1)
                else:
                    print(f"  ❌ Max retries reached. Tool execution has systematic issue.")
                    # Use first agent result since all should be identical
                    return list(agent_results.values())[0].extracted_data, retries
        
        return {}, retries
    
    @abstractmethod
    def _create_final_audit_result(self, results: Dict[str, Any], total_retries: int, 
                                  retry_log: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create the final audit result with metadata"""
        pass
    
    def _extract_key_figures(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract key financial figures for consensus comparison"""
        
        key_figures = {}
        
        try:
            if 'laporan_posisi_keuangan' in data:
                posisi = data['laporan_posisi_keuangan']
                
                # Extract asset figures
                if 'aset' in posisi:
                    aset = posisi['aset']
                    
                    if 'aset_lancar' in aset and isinstance(aset['aset_lancar'], dict):
                        if 'nilai_tercatat' in aset['aset_lancar']:
                            key_figures['aset_lancar'] = float(aset['aset_lancar']['nilai_tercatat'])
                    
                    if 'total_aset' in aset and isinstance(aset['total_aset'], dict):
                        if 'nilai_tercatat' in aset['total_aset']:
                            key_figures['total_aset'] = float(aset['total_aset']['nilai_tercatat'])
                
                # Extract balancing figures
                if 'balancing' in posisi:
                    balancing = posisi['balancing']
                    
                    if 'total_aset' in balancing:
                        key_figures['balance_total_aset'] = float(balancing['total_aset'])
                    
                    if 'total_liabilitas_ekuitas' in balancing:
                        key_figures['balance_total_liab_eq'] = float(balancing['total_liabilitas_ekuitas'])
        
        except (ValueError, KeyError, TypeError):
            pass
        
        return key_figures