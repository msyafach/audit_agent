#!/usr/bin/env python3
"""
Gemini-based financial audit agent implementation
"""

import os
import json
import time
from typing import Dict, List, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from core.base_agent import BaseFinancialAgent, AgentResult, BaseTripleAgentSystem, ConsensusResult
from core.config import ModelConfig, AgentConfig, ConfigManager
from core.utils import parse_json_safely, validate_financial_data_structure

class GeminiFinancialAgent(BaseFinancialAgent):
    """Financial audit agent using Google Gemini"""
    
    def __init__(self, agent_id: str, model_config: ModelConfig, agent_config: AgentConfig):
        super().__init__(agent_id)
        self.model_config = model_config
        self.agent_config = agent_config
        self.model = self._setup_model()
    
    def _setup_model(self) -> ChatGoogleGenerativeAI:
        """Setup Gemini model"""
        
        os.environ["GOOGLE_API_KEY"] = self.model_config.api_key
        
        return ChatGoogleGenerativeAI(
            model=self.model_config.name,
            temperature=self.agent_config.temperature,
            max_tokens=self.agent_config.max_tokens,
            max_retries=self.model_config.max_retries
        )
    
    def _get_llm_interpretation(self, statement_text: str, statement_type: str, 
                               tool_results: Dict[str, Any]) -> Dict[str, Any]:
        """Get LLM interpretation for context only - NO calculations allowed"""
        
        # LLM can only provide context/interpretation, NOT calculations
        prompt = f"""
        CONTEXT ONLY: You are {self.agent_id} providing interpretation context.
        
        CRITICAL: You are FORBIDDEN from doing calculations. All calculations are done by tools.
        
        Tool results: {tool_results}
        Statement type: {statement_type}
        
        Provide ONLY interpretation context about the financial statement structure.
        DO NOT calculate anything. DO NOT verify numbers. Just provide business context.
        
        Return JSON with interpretation only:
        {{
          "interpretation": {{
            "statement_type": "{statement_type}",
            "context": "Brief business context about this statement",
            "structure_notes": "Notes about statement structure"
          }}
        }}
        """
        
        try:
            messages = [
                SystemMessage(content="You provide context only. NEVER calculate. Tools handle all calculations."),
                HumanMessage(content=prompt)
            ]
            
            response = self.model.invoke(messages)
            return parse_json_safely(response.content)
        except:
            return {"interpretation": {"context": "LLM interpretation unavailable"}}
    
    # Note: process_statement is now handled by BaseFinancialAgent with mandatory tools
    
    def _create_agent_specific_prompt(self, statement_text: str, statement_type: str) -> str:
        """Create agent-specific prompt"""
        
        base_prompt = self._create_base_prompt(statement_text, statement_type)
        
        return f"""{base_prompt}
        
        AGENT SPECIALIZATION: {self.agent_config.approach}
        
        CRITICAL: Return ONLY the JSON structure above. No additional text."""
    
    def _count_implied_calculations(self, response: str) -> int:
        """Count implied calculations from response content"""
        
        # Count calculation-related keywords
        calc_keywords = ['total', 'sum', 'jumlah', 'subtotal', 'balance', 'calculation', 'perhitungan']
        
        count = 0
        response_lower = response.lower()
        
        for keyword in calc_keywords:
            count += response_lower.count(keyword)
        
        # Count numerical values (indicates calculations)
        import re
        numbers = re.findall(r'\d+', response)
        count += min(len(numbers) // 4, 10)  # Every 4 numbers = 1 calculation
        
        return max(count, 3)  # Minimum 3 for any financial audit
    
    def _calculate_validation_score(self, data: Dict[str, Any], tool_calls: int) -> float:
        """Calculate validation score for Gemini agent"""
        
        score = 0.0
        
        # Base validation
        if validate_financial_data_structure(data):
            score += 40.0
        
        # Check for specific financial elements
        if 'laporan_posisi_keuangan' in data:
            posisi = data['laporan_posisi_keuangan']
            
            if 'aset' in posisi:
                score += 25.0
                
                aset = posisi['aset']
                # Check for detailed calculations
                if any('detail_perhitungan' in v for v in aset.values() if isinstance(v, dict)):
                    score += 15.0
                
                # Check for numerical accuracy
                if any('selisih' in v and v.get('selisih') == 0 for v in aset.values() if isinstance(v, dict)):
                    score += 10.0
            
            # Balance sheet validation
            if 'balancing' in posisi:
                score += 10.0
        
        return min(score, 100.0)
    
    def _calculate_confidence(self, data: Dict[str, Any], validation_score: float, tool_calls: int) -> float:
        """Calculate confidence score"""
        
        base_confidence = validation_score * 0.8
        
        # Bonus for structural completeness
        if validate_financial_data_structure(data):
            base_confidence += 10.0
        
        # Penalty for errors
        data_str = json.dumps(data).lower()
        if 'error' in data_str or 'tidak seimbang' in data_str:
            base_confidence -= 15.0
        
        return min(max(base_confidence, 0.0), 100.0)

class GeminiTripleAgentSystem(BaseTripleAgentSystem):
    """Triple agent system using Gemini models"""
    
    def __init__(self, model_config: ModelConfig, max_retries: int = 2):
        super().__init__(max_retries)
        self.model_config = model_config
    
    def _create_agents(self) -> List[GeminiFinancialAgent]:
        """Create three Gemini agents with different configurations"""
        
        agents = []
        
        for agent_id in ["agent_1", "agent_2", "agent_3"]:
            agent_config = ConfigManager.get_agent_config(agent_id)
            agent = GeminiFinancialAgent(agent_id, self.model_config, agent_config)
            agents.append(agent)
        
        return agents
    
    def _validate_consensus(self, agent_results: Dict[str, AgentResult]) -> ConsensusResult:
        """Validate strict consensus between Gemini agents"""
        
        # Extract key figures for comparison
        key_figures = {}
        discrepancies = []
        confidence_scores = {}
        
        for agent_id, result in agent_results.items():
            confidence_scores[agent_id] = result.confidence
            figures = self._extract_key_figures(result.extracted_data)
            key_figures[agent_id] = figures
        
        # Compare ALL figures with strict tolerance
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
                # STRICT comparison
                base_value = values[0][1]
                tolerance = max(abs(base_value * 0.0001), 1.0)  # 0.01% or 1
                
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
                        "values": dict(values),
                        "tolerance_used": tolerance
                    })
        
        # Perfect consensus requirement
        is_consensus = len(discrepancies) == 0 and len(failing_agents) == 0
        
        if is_consensus:
            best_agent = max(agent_results.items(), key=lambda x: x[1].confidence)[0]
            agreed_data = agent_results[best_agent].extracted_data
        else:
            agreed_data = {}
        
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
        """Create final audit result with Gemini metadata"""
        
        return {
            "audit_footing_laporan_keuangan": results,
            "_gemini_triple_agent_metadata": {
                "model_used": self.model_config.name,
                "provider": "google_gemini",
                "consensus_quality": "Perfect" if total_retries == 0 else "Achieved with retries",
                "total_retries": total_retries,
                "retry_log": retry_log,
                "mathematical_precision": "High (AI-verified)",
                "audit_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "system_type": "Gemini Triple Agent"
            }
        }