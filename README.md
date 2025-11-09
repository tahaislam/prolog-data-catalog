# 🧠 Metadata AI System - Intelligent Data Governance with Prolog

A powerful natural language interface for data catalog management, built with Prolog logic programming and Python. Query your data infrastructure using plain English!

## 🎯 What Problem Does This Solve?

Modern data platforms have hundreds or thousands of tables across multiple layers (Bronze, Silver, Gold). Managing metadata becomes challenging:

- 📊 **Data Lineage**: "Where does this column come from?"
- 🔍 **Impact Analysis**: "What breaks if I change this table?"
- ✅ **Governance**: "Which datasets lack proper documentation?"
- 🎭 **Compliance**: "Where is sensitive data stored?"

This system provides an **AI-powered natural language interface** to answer these questions instantly.

## ✨ Key Features

### 🗣️ Natural Language Queries
Ask questions in plain English:
```
💬 "Show me all Gold layer datasets"
💬 "Trace lineage for customer_orders.email"
💬 "What governance violations do we have?"
💬 "Where is confidential data?"
```

### 🧠 AI-Enhanced Understanding (Optional)
Enable Ollama integration for superior natural language understanding:
- Better handling of complex, multi-part questions
- Understands context and ambiguity
- Handles typos and variations
- More natural conversation flow

Works with both pattern matching (default) and AI enhancement (with Ollama)!

### 🧠 Prolog Logic Engine
- Complex rule-based validation
- Recursive lineage tracing
- Cycle detection
- Graph traversal
- Pattern matching

### 📊 Rich Metadata Model
Tracks comprehensive metadata across:
- **Datasets**: Tables across medallion architecture (Bronze/Silver/Gold)
- **Data Points**: Individual columns with lineage
- **Governance**: Owners, stewards, reviewers, validators
- **Sensitivity**: Data classification and compliance labels
- **Lineage**: Source-target relationships with transformations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Natural Language Interface                 │
│                          (Python)                           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Prolog Logic Engine                       │
│          • Query Processing                                 │
│          • Rule Validation                                  │
│          • Lineage Resolution                               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Metadata Knowledge Base                  │
│          dataset_facts.pl (Auto-generated from Excel)       │
│         datapoint_facts.pl (Auto-generated from Excel)      │
│          metadata_kb.pl (Business rules & queries)          │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.8+
python --version

# SWI-Prolog
brew install swi-prolog  # macOS
# or
apt-get install swi-prolog  # Linux
```

### Installation
```bash
# Clone the repository
git clone https://github.com/tahaislam/prolog-data-catalog.git
cd prolog-data-catalog

# Install dependencies
pip install -r requirements.txt

# Generate sample data
python generate_sample_data.py

# Convert Excel to Prolog facts
python excel_to_prolog.py Sample_Metadata.xlsx

# Test the system
python test_system.py
```

### Interactive Mode
```bash
python nl_interface.py

# Or with AI enhancement (requires Ollama)
python nl_interface.py --ai

💬 What would you like to know about your data?
> Show me all Gold datasets

🔍 Finding all Gold layer datasets...
✅ Found 15 datasets:
1. gold_customer_360
2. gold_sales_analytics
3. gold_financial_summary
...
```

### Command Line Mode
```bash
python nl_interface.py "Trace lineage for customer_orders.email"
python nl_interface.py "Find datasets without reviewers"

# With AI enhancement
python nl_interface.py --ai "Show governance violations"
```

### Enable AI Enhancement (Optional)

For better natural language understanding, install Ollama:

1. **Install Ollama**: https://ollama.ai/
2. **Pull a model**:
   ```bash
   ollama pull llama3.2
   ```
3. **Run with AI flag**:
   ```bash
   python nl_interface.py --ai
   ```

AI mode provides superior understanding of complex questions!

## 📖 Example Queries

### Data Discovery
```
• "Show me all Gold layer datasets"
• "Find datasets in the Customer subject area"
• "What datasets come from the ERP system?"
• "Show Silver layer Sales datasets"
```

### Governance & Compliance
```
• "Find datasets without reviewers"
• "Where is confidential data?"
• "Show governance violations"
• "Find critical data not in production"
• "Which datasets lack data stewards?"
```

### Data Lineage
```
• "Trace lineage for customer_orders.email"
• "What is the source of gold_revenue.amount?"
• "Show me the full lineage chain"
```

### Impact Analysis
```
• "What depends on raw_customers.customer_id?"
• "Show downstream impact of bronze_orders"
• "What breaks if I change this column?"
```

### Analysis & Insights
```
• "Which subject areas have complete pipelines?"
• "Show subject areas missing Gold layer"
• "Count datasets by data source"
• "Which data source has the most datasets?"
```

## 📁 Project Structure

```
metadata-ai-system/
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── Sample_Metadata.xlsx          # Sample Excel metadata (to be generated)
├── generate_sample_data.py       # Generate artificial data
├── excel_to_prolog.py            # Excel → Prolog converter
├── metadata_kb.pl                # Prolog rules & queries
├── dataset_facts.pl              # Auto-generated facts (to be generated)
├── datapoint_facts.pl            # Auto-generated facts (to be generated)
├── nl_interface.py               # Natural language interface
├── test_system.py                # System tests
├── user_guide.md                 # Comprehensive guide
├── sample_questions.txt          # Sample questions on the auto-generated facts
```

## 🎓 Use Cases

### 1. Data Governance Teams
- Automated compliance checking
- Data quality monitoring
- Ownership tracking

### 2. Data Engineers
- Impact analysis before changes
- Lineage documentation
- Dependency mapping

### 3. Data Analysts
- Data discovery
- Source identification
- Quality assessment

### 4. Compliance Officers
- Sensitive data tracking
- Audit trails
- Policy enforcement

## 🔧 Customization

### Adding Custom Rules
Edit `metadata_kb.pl` to add domain-specific rules:

```prolog
% Custom rule: Find high-risk datasets
high_risk_dataset(ViewName) :-
    dataset(_, ViewName, 'Gold', _, _, _, _, _, _, _, _, _),
    datapoint(_, _, _, _, _, _, ViewName, _, _, _, _, _, _, _,
              _, _, _, _, _, _, _, _, _, _, _, _, 'Confidential', _, _),
    \+ has_reviewer(ViewName).
```

### Extending Metadata Model
Add new columns to Excel template and regenerate:
```bash
python excel_to_prolog.py your_metadata.xlsx
```

## 📊 Performance

- ⚡ **Fast**: Queries execute in milliseconds
- 📈 **Scalable**: Tested with 18,000+ data points, 800+ datasets
- 🔄 **Efficient**: Optimized for recursive lineage tracing
- 💾 **Lightweight**: Minimal memory footprint

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- Built with [SWI-Prolog](https://www.swi-prolog.org/)
- Python interface via [PySwip](https://github.com/yuce/pyswip)
- Inspired by modern data catalog solutions

## 📧 Contact

Questions? Open an issue or reach out!

---

**⭐ If you find this useful, please star the repository!**
