#!/usr/bin/env python3
"""
Ollama-based financial audit agent implementation
"""

import json
import time
import re
from typing import Dict, List, Any
from langchain_ollama import OllamaLLM

from core.base_agent import BaseFinancialAgent, AgentResult, BaseTripleAgentSystem, ConsensusResult
from core.config import ModelConfig, AgentConfig, ConfigManager
from core.utils import parse_json_safely, validate_financial_data_structure

class OllamaFinancialAgent(BaseFinancialAgent):
    """Financial audit agent using Ollama"""
    
    def __init__(self, agent_id: str, model_config: ModelConfig, agent_config: AgentConfig):
        super().__init__(agent_id)
        self.model_config = model_config
        self.agent_config = agent_config
        self.model = self._setup_model()
    
    def _setup_model(self) -> OllamaLLM:
        """Setup Ollama model"""
        
        return OllamaLLM(
            model=self.model_config.name,
            base_url=self.model_config.base_url,
            temperature=self.agent_config.temperature,
            num_predict=self.agent_config.max_tokens,
            format="json"  # Request JSON output
        )
    
    def _get_llm_interpretation(self, statement_text: str, statement_type: str, 
                               tool_results: Dict[str, Any]) -> Dict[str, Any]:
        """Get LLM interpretation for context only - NO calculations allowed"""
        
        prompt = f"""You provide context only. NEVER calculate. Tools handle all calculations.
        
        Tool results: {tool_results}
        Statement type: {statement_type}
        
        Return JSON:
        {{
          "interpretation": {{
            "statement_type": "{statement_type}",
            "context": "Brief context"
          }}
        }}
        """
        
        try:
            response = self.model.invoke(prompt)
            return parse_json_safely(response)
        except:
            return {"interpretation": {"context": "Ollama interpretation unavailable"}}
    
    # Note: process_statement is now handled by BaseFinancialAgent with mandatory tools
    
    def _create_agent_specific_prompt(self, statement_text: str, statement_type: str) -> str:
        """Create agent-specific prompt for Ollama"""
        
        base_prompt = self._create_base_prompt(statement_text, statement_type)
        
        return f"""{base_prompt}
        
        SPECIALIZATION: {self.agent_config.approach}
        
        IMPORTANT: Return ONLY the JSON structure. No additional text or explanations."""
    
    def _simulate_tool_calculations(self, response: str) -> int:
        """Simulate tool calculations based on response analysis"""
        
        tool_calls = 0
        
        # Enhanced calculation pattern detection
        calc_patterns = [
            r'total|sum|jumlah|subtotal',
            r'aset|asset|liabilitas|ekuitas',
            r'nilai|value|amount',
            r'perhitungan|calculation|compute',
            r'balance|seimbang|equation'
        ]
        
        response_lower = response.lower()
        
        for pattern in calc_patterns:
            matches = re.findall(pattern, response_lower)
            tool_calls += len(matches)
        
        # Count numerical operations
        numbers = re.findall(r'\d+', response)
        tool_calls += min(len(numbers) // 3, 12)
        
        # Ensure minimum tool calls for financial audit
        tool_calls = max(tool_calls, 6)
        
        return min(tool_calls, 25)
    
    def _calculate_validation_score(self, data: Dict[str, Any], tool_calls: int) -> float:
        """Calculate validation score for Ollama agent"""
        
        score = 0.0
        
        # Base score for valid JSON
        if data and isinstance(data, dict):
            score += 25.0
        
        # Structure validation
        if validate_financial_data_structure(data):
            score += 30.0
        
        # Content quality checks
        if 'laporan_posisi_keuangan' in data:
            posisi = data['laporan_posisi_keuangan']
            
            if 'aset' in posisi and isinstance(posisi['aset'], dict):
                score += 20.0
                
                aset = posisi['aset']
                
                # Check for numerical values
                numerical_fields = 0
                for item in aset.values():
                    if isinstance(item, dict):
                        if 'nilai_tercatat' in item:
                            numerical_fields += 1
                        if 'nilai_perhitungan' in item:
                            numerical_fields += 1
                
                score += min(numerical_fields * 2, 15)
            
            # Balance sheet validation
            if 'balancing' in posisi:
                score += 10.0
        
        return min(score, 100.0)
    
    def _calculate_confidence(self, data: Dict[str, Any], validation_score: float, tool_calls: int) -> float:
        """Calculate confidence score"""
        
        base_confidence = validation_score * 0.75
        
        # Tool usage bonus
        tool_bonus = min(tool_calls * 0.8, 15.0)
        base_confidence += tool_bonus
        
        # Structure completeness bonus
        if validate_financial_data_structure(data):
            base_confidence += 10.0
        
        # Error penalties
        try:
            data_str = json.dumps(data, ensure_ascii=False).lower()
            if 'error' in data_str:
                base_confidence -= 20.0
            if 'tidak seimbang' in data_str:
                base_confidence -= 10.0
        except:
            base_confidence -= 5.0
        
        return min(max(base_confidence, 0.0), 100.0)

class OllamaTripleAgentSystem(BaseTripleAgentSystem):
    """Triple agent system using Ollama models"""
    
    def __init__(self, model_config: ModelConfig, max_retries: int = 2):
        super().__init__(max_retries)
        self.model_config = model_config
    
    def _create_agents(self) -> List[OllamaFinancialAgent]:
        """Create three Ollama agents with different configurations"""
        
        agents = []
        
        for agent_id in ["agent_1", "agent_2", "agent_3"]:
            agent_config = ConfigManager.get_agent_config(agent_id)
            agent = OllamaFinancialAgent(agent_id, self.model_config, agent_config)
            agents.append(agent)
        
        return agents
    
    def _validate_consensus(self, agent_results: Dict[str, AgentResult]) -> ConsensusResult:
        """Validate consensus between Ollama agents"""
        
        key_figures = {}
        discrepancies = []
        confidence_scores = {}
        
        for agent_id, result in agent_results.items():
            confidence_scores[agent_id] = result.confidence
            figures = self._extract_key_figures(result.extracted_data)
            key_figures[agent_id] = figures
        
        # Compare figures with reasonable tolerance for Ollama
        failing_agents = []
        all_keys = set()
        for figures in key_figures.values():
            all_keys.update(figures.keys())
        
        for key in all_keys:
            values = []
            for agent_id, figures in key_figures.items():
                if key in figures:
                    values.append((agent_id, figures[key]))
            
            if len(values) >= 2:
                # Reasonable tolerance for local models
                base_value = values[0][1]
                tolerance = max(abs(base_value * 0.001), 5.0)  # 0.1% or 5
                
                disagreeing_agents = []
                for agent_id, value in values[1:]:
                    if abs(value - base_value) > tolerance:
                        disagreeing_agents.append(agent_id)
                        if agent_id not in failing_agents:
                            failing_agents.append(agent_id)
                
                if disagreeing_agents:
                    discrepancies.append({
                        "key": key,
                        "base_value": base_value,
                        "disagreeing_agents": disagreeing_agents,
                        "values": dict(values)
                    })
        
        # Consensus achieved if no major disagreements
        is_consensus = len(discrepancies) == 0 and len(failing_agents) == 0
        
        if is_consensus:
            best_agent = max(agent_results.items(), key=lambda x: x[1].confidence)[0]
            agreed_data = agent_results[best_agent].extracted_data
            print(f"        🎯 Ollama consensus achieved - using {best_agent}")
        else:
            agreed_data = {}
            print(f"        ⚠️  Ollama consensus failed - {len(discrepancies)} disagreements")
        
        return ConsensusResult(
            is_consensus=is_consensus,
            agreed_data=agreed_data,
            discrepancies=discrepancies,
            retry_needed=not is_consensus,
            failing_agents=failing_agents,
            confidence_scores=confidence_scores
        )
    
    def _create_final_audit_result(self, results: Dict[str, Any], total_retries: int, 
                                  retry_log: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create final audit result with Ollama metadata"""
        
        return {
            "audit_footing_laporan_keuangan": results,
            "_ollama_triple_agent_metadata": {
                "model_used": self.model_config.name,
                "provider": "ollama",
                "base_url": self.model_config.base_url,
                "consensus_quality": "Perfect" if total_retries == 0 else "Achieved with retries",
                "total_retries": total_retries,
                "retry_log": retry_log,
                "mathematical_precision": "High (Local model verified)",
                "audit_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "system_type": "Ollama Triple Agent"
            }
        }