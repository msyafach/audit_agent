# 🚀 Financial Statement Audit System

**Advanced triple agent system for automated financial statement footing verification with strict consensus validation**

## ✨ Features

- **🤖 Multi-Provider Support**: Gemini AI and Ollama local models
- **🎯 Triple Agent Consensus**: 3 independent agents with strict agreement validation
- **🔄 Automatic Retry Logic**: System restarts if agents disagree
- **📊 Batch Processing**: Process multiple companies automatically
- **🧮 High Precision**: Enhanced calculation tools with 28-digit accuracy
- **📁 Clean Architecture**: Modular, extensible codebase

## 🏗️ Architecture

```
audit_system.py          # Main unified interface
├── core/               # Base classes and utilities
│   ├── base_agent.py   # Abstract agent interfaces
│   ├── config.py       # Configuration management
│   └── utils.py        # Utility functions
├── agents/             # Provider-specific implementations
│   ├── gemini_agent.py # Google Gemini agents
│   └── ollama_agent.py # Ollama local model agents
├── input/              # Financial statement data
└── results/            # Audit results output
```

## 🚀 Quick Start

### **Option 1: Gemini AI (Cloud)**
```bash
# Set API key
export GOOGLE_API_KEY="your_api_key_here"

# Run audit
uv run python audit_system.py --provider gemini --model gemini-2.0-flash
```

### **Option 2: Ollama (Local)**
```bash
# Start Ollama service
ollama serve

# Install model
ollama pull qwen3:4b

# Run audit
uv run python audit_system.py --provider ollama --model qwen3:4b
```

## 📋 Usage Examples

### **Audit All Companies**
```bash
uv run python audit_system.py --provider gemini
```

### **Audit Specific Company**
```bash
uv run python audit_system.py --provider ollama --model qwen3:4b --company AALI
```

### **With Custom Settings**
```bash
uv run python audit_system.py \
  --provider gemini \
  --model gemini-2.0-flash \
  --retries 3 \
  --debug
```

## 🔧 Configuration

### **Supported Models**

**Gemini:**
- `gemini-1.5-flash`
- `gemini-2.0-flash` (recommended)

**Ollama:**
- `qwen3:4b` (recommended)
- `gemma3n:e2b`
- `qwen2.5:4b`
- `llama3.2:3b`

### **CLI Options**
```bash
--provider        Model provider (gemini/ollama)
--model          Specific model name
--company        Process specific company only
--api-key        Gemini API key
--base-url       Ollama server URL (default: http://localhost:11434)
--retries        Max consensus retries (default: 2)
--debug          Enable debug output
```

## 📁 Input Format

Financial statements should be placed in `input/` folder with naming convention:
```
input/
├── COMPANY_posisi_keuangan.txt    # Balance Sheet
├── COMPANY_laba_rugi.txt          # Income Statement
└── COMPANY_arus_kas.txt           # Cash Flow Statement
```

Example: `AALI_posisi_keuangan.txt`

## 📊 Output

Results are saved to `results/` folder as JSON files:
```json
{
  "audit_footing_laporan_keuangan": {
    "laporan_posisi_keuangan": {
      "aset": {
        "total_aset": {
          "nilai_tercatat": 1000000,
          "nilai_perhitungan": 1000000,
          "selisih": 0,
          "status": "OK"
        }
      },
      "balancing": {
        "status": "Seimbang"
      }
    }
  },
  "_metadata": {
    "system_type": "Triple Agent",
    "consensus_quality": "Perfect",
    "total_retries": 0
  }
}
```

## 🎯 How It Works

### **Triple Agent Consensus**
1. **Three independent agents** analyze the same financial statement
2. **Each agent** extracts numerical data and performs calculations
3. **Consensus validation** compares all agent results with strict tolerance
4. **If agents disagree** → automatic retry (up to 2 additional attempts)
5. **Perfect consensus required** → all agents must agree completely

### **Strict Validation**
- **Tolerance**: 0.01% difference maximum
- **Restart Logic**: ANY disagreement triggers retry
- **Quality Assurance**: Only perfect consensus results accepted

## 🛠️ Installation

### **Prerequisites**
- Python 3.11+
- UV package manager

### **Install Dependencies**
```bash
# For Gemini
uv add langchain-google-genai

# For Ollama  
uv add langchain-ollama

# Install Ollama (if using local models)
curl -fsSL https://ollama.ai/install.sh | sh
```

### **Setup**
```bash
git clone <repository>
cd api_footing
uv sync
```

## 🧮 Enhanced Features

### **High-Precision Calculations**
- 28-digit decimal precision
- Automatic rounding error elimination
- Complete calculation audit trails

### **Intelligent Error Handling**
- JSON parsing fallbacks
- Graceful failure recovery
- Detailed error reporting

### **Flexible Configuration**
- Per-agent temperature settings
- Configurable retry limits
- Debug mode support

## 📈 Performance

### **Gemini AI**
- ⚡ **Speed**: ~10-30 seconds per company
- 🎯 **Accuracy**: High with cloud processing
- 💰 **Cost**: API usage charges apply

### **Ollama Local**
- ⚡ **Speed**: ~30-60 seconds per company  
- 🎯 **Accuracy**: Good with local inference
- 💰 **Cost**: Free (local processing)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes following the architecture patterns
4. Add tests for new features
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
1. Check existing issues
2. Create new issue with detailed description
3. Include system info and error logs

---

**🎉 Ready to audit financial statements with AI precision!**