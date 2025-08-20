#!/usr/bin/env python3
"""
Unified Financial Statement Audit System
Supports both Gemini and Ollama models with triple agent consensus validation
"""

import os
import sys
from typing import Dict, List, Any, Optional

# Add core modules to path
sys.path.insert(0, os.path.dirname(__file__))

from core.config import ConfigManager, ModelConfig, SystemConfig
from core.utils import detect_all_companies, load_financial_statements, save_audit_results, print_audit_summary
from agents.gemini_agent import GeminiTripleAgentSystem
from agents.ollama_agent import OllamaTripleAgentSystem

class UnifiedAuditSystem:
    """Unified audit system supporting multiple model providers"""
    
    def __init__(self, provider: str = "gemini", model_name: str = None, **config_kwargs):
        """
        Initialize audit system
        
        Args:
            provider: "gemini" or "ollama"
            model_name: Specific model name
            **config_kwargs: Additional configuration options
        """
        self.provider = provider
        
        # Separate system config from provider-specific config
        system_config_keys = {'max_retries', 'consensus_tolerance', 'input_dir', 'output_dir', 'enable_debug'}
        system_kwargs = {k: v for k, v in config_kwargs.items() if k in system_config_keys}
        
        self.system_config = ConfigManager.create_system_config(**system_kwargs)
        
        # Create model configuration
        if provider == "gemini":
            api_key = config_kwargs.get("api_key")
            self.model_config = ConfigManager.create_gemini_config(
                model_name or "gemini-2.0-flash", api_key
            )
            self.agent_system = GeminiTripleAgentSystem(
                self.model_config, self.system_config.max_retries
            )
            
        elif provider == "ollama":
            base_url = config_kwargs.get("base_url", "http://localhost:11434")
            self.model_config = ConfigManager.create_ollama_config(
                model_name or "qwen3:4b", base_url
            )
            self.agent_system = OllamaTripleAgentSystem(
                self.model_config, self.system_config.max_retries
            )
            
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Validate configuration
        if not ConfigManager.validate_config(self.model_config):
            raise ValueError("Invalid model configuration")
    
    def audit_single_company(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Audit a single company"""
        
        print(f"🏢 Processing company: {company_name}")
        
        try:
            # Load financial statements
            statements, company = load_financial_statements(
                self.system_config.input_dir, company_name
            )
            
            if not statements:
                print(f"❌ Could not load statements for {company_name}")
                return None
            
            # Process with triple agent system
            results = self.agent_system.process_financial_statements(statements, company)
            
            # Save results
            output_path = save_audit_results(
                results, company, self.system_config.output_dir,
                f"{self.provider}_triple_agent"
            )
            
            print(f"✅ Audit completed for {company}")
            print(f"💾 Results saved to: {output_path}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error processing {company_name}: {e}")
            return None
    
    def audit_all_companies(self) -> Dict[str, Any]:
        """Audit all companies found in input directory"""
        
        print(f"🚀 UNIFIED FINANCIAL AUDIT SYSTEM")
        print("=" * 60)
        print(f"🤖 Provider: {self.provider.title()}")
        print(f"📊 Model: {self.model_config.name}")
        print(f"🎯 Triple agent consensus validation enabled\n")
        
        # Detect companies
        companies = detect_all_companies(self.system_config.input_dir)
        
        if not companies:
            raise ValueError("No companies found in input folder")
        
        print(f"🏢 Found {len(companies)} companies: {', '.join(companies)}")
        
        # Process each company
        successful_audits = []
        failed_audits = []
        all_results = {}
        
        for i, company in enumerate(companies, 1):
            print(f"\n{'='*60}")
            print(f"PROCESSING COMPANY {i}/{len(companies)}: {company}")
            print(f"{'='*60}")
            
            result = self.audit_single_company(company)
            
            if result:
                successful_audits.append(company)
                all_results[company] = result
                
                # Print summary
                if not self.system_config.enable_debug:
                    print_audit_summary(result, company)
            else:
                failed_audits.append(company)
        
        # Final summary
        print(f"\n{'='*80}")
        print(f"{self.provider.upper()} TRIPLE AGENT BATCH AUDIT SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Successful audits: {len(successful_audits)} companies")
        for company in successful_audits:
            print(f"   - {company}")
        
        if failed_audits:
            print(f"\n❌ Failed audits: {len(failed_audits)} companies")
            for company in failed_audits:
                print(f"   - {company}")
        
        print(f"\n💾 All results saved to {self.system_config.output_dir}/ folder")
        
        return all_results
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system configuration info"""
        
        return {
            "provider": self.provider,
            "model": self.model_config.name,
            "system_config": {
                "max_retries": self.system_config.max_retries,
                "consensus_tolerance": self.system_config.consensus_tolerance,
                "input_dir": self.system_config.input_dir,
                "output_dir": self.system_config.output_dir
            },
            "available_models": ConfigManager.list_available_models()
        }

def create_gemini_system(model_name: str = "gemini-2.0-flash", 
                        api_key: str = None, **kwargs) -> UnifiedAuditSystem:
    """Create Gemini-based audit system"""
    return UnifiedAuditSystem("gemini", model_name, api_key=api_key, **kwargs)

def create_ollama_system(model_name: str = "qwen3:4b", 
                        base_url: str = "http://localhost:11434", **kwargs) -> UnifiedAuditSystem:
    """Create Ollama-based audit system"""
    return UnifiedAuditSystem("ollama", model_name, base_url=base_url, **kwargs)

def main():
    """Main CLI interface"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Financial Statement Audit System")
    parser.add_argument("--provider", choices=["gemini", "ollama"], default="gemini",
                       help="Model provider to use")
    parser.add_argument("--model", help="Specific model name")
    parser.add_argument("--company", help="Specific company to audit")
    parser.add_argument("--api-key", help="Gemini API key")
    parser.add_argument("--base-url", default="http://localhost:11434", 
                       help="Ollama base URL")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--retries", type=int, default=2, help="Max retries for consensus")
    
    args = parser.parse_args()
    
    try:
        # Create system
        config_kwargs = {
            "enable_debug": args.debug,
            "max_retries": args.retries
        }
        
        if args.provider == "gemini":
            config_kwargs["api_key"] = args.api_key
            system = UnifiedAuditSystem("gemini", args.model, **config_kwargs)
        else:
            config_kwargs["base_url"] = args.base_url
            system = UnifiedAuditSystem("ollama", args.model, **config_kwargs)
        
        # Print system info
        print("📋 System Configuration:")
        info = system.get_system_info()
        print(f"   Provider: {info['provider']}")
        print(f"   Model: {info['model']}")
        print(f"   Max Retries: {info['system_config']['max_retries']}")
        print()
        
        # Run audit
        if args.company:
            system.audit_single_company(args.company)
        else:
            system.audit_all_companies()
        
    except Exception as e:
        print(f"❌ System error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()