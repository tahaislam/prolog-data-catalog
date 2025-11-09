# Complete User Guide - Metadata AI System

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Data Model](#data-model)
4. [Query Examples](#query-examples)
5. [Customization](#customization)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)

---

## Installation

### Prerequisites

**Python 3.8 or higher**
```bash
python --version  # Should be 3.8+
```

**SWI-Prolog**

*macOS:*
```bash
brew install swi-prolog
```

*Ubuntu/Debian:*
```bash
sudo apt-get update
sudo apt-get install swi-prolog
```

*Windows:*
Download from https://www.swi-prolog.org/download/stable

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/tahaislam/metadata-ai-system.git
cd metadata-ai-system
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Generate sample data**
```bash
python generate_sample_data.py
```

5. **Convert to Prolog**
```bash
python excel_to_prolog.py Sample_Metadata.xlsx
```

6. **Test the system**
```bash
python test_system.py
```

If all tests pass, you're ready to go! 🎉

---

## Quick Start

### Interactive Mode

Start the natural language interface:

```bash
python nl_interface.py
```

Then ask questions:
```
💬 What would you like to know about your data?
> Show me all Gold datasets

🔍 Finding all Gold layer datasets...
✅ Found 18 result(s):

1. gold_customer_crm
2. gold_customer_ecommerce
3. gold_sales_crm
...
```

### Command Line Mode

Ask questions directly:

```bash
python nl_interface.py "Find governance violations"
python nl_interface.py "Where is confidential data?"
python nl_interface.py "Show all subject areas"
```

### Python Script Integration

Use in your own scripts:

```python
from nl_interface import NaturalLanguageInterface

# Initialize
interface = NaturalLanguageInterface()

# Ask questions
results = interface.ask("Show me all Gold datasets")

# Process results
for result in results:
    print(f"Processing: {result['ViewName']}")
```

---

## Data Model

### Dataset Sheet Structure

| Column | Description | Example |
|--------|-------------|---------|
| ViewID | Unique identifier | V0001 |
| ViewName | Table/view name | gold_customer_360 |
| DataLayer | Bronze/Silver/Gold | Gold |
| Name | Human-readable name | Customer 360 View |
| SubjectArea | Domain area | Customer |
| SubjectAreaSubCategory | Sub-domain | Customer Data |
| DataSource | Source system | CRM Platform |
| DataSourceID | Source system ID | CRM001 |
| Reviewer | Business reviewer | Alice Johnson |
| TechnicalDesignReviewer | Technical reviewer | Bob Smith |
| Processor | Processing team | Data Engineering |
| Validator | Data validator | Emily Brown |

### DataPoint Sheet Structure

| Column | Description | Example |
|--------|-------------|---------|
| DatapointID | Unique identifier | DP00001 |
| ViewName | Parent table | gold_customer_360 |
| ColumnName | Column name | email |
| ColumnLabel | Display name | Email Address |
| SourceViewIDName | **Source table (lineage)** | silver_customer_crm |
| SourceViewIDColumnName | **Source column (lineage)** | email |
| SensitivityLabel | Data classification | Confidential |
| DataSteward | Data steward | Sarah Martinez |
| DataOwner | Data owner | VP Sales |
| EnvironmentStatus | Deployment status | Production |
| MobilizationStatus | Implementation status | Complete |
| CriticalDataElementIndicator | Is critical? | Yes/No |

**Key Fields for Lineage:**
- `SourceViewIDName` + `SourceViewIDColumnName` define the parent data point
- System recursively traces these to build full lineage chains

---

## Query Examples

### Data Discovery

**Find all datasets in a layer:**
```
Show me all Gold datasets
Show me all Silver datasets
Show me all Bronze datasets
```

**Find datasets by subject area:**
```
Show me datasets in Customer subject area
Find Sales datasets
```

**Find datasets by data source:**
```
Show datasets from ERP System
Find CRM Platform datasets
```

**Combined queries:**
```
Show me Gold layer Customer datasets
Find Silver datasets from the CRM Platform
```

### Data Governance

**Find governance issues:**
```
Find governance violations
Show datasets without reviewers
Find datasets without validators
Show datapoints without stewards
Find datapoints without owners
```

**Check compliance:**
```
Where is confidential data?
Find sensitive data
Show critical data elements
Find critical data not in production
```

### Data Lineage

**Trace upstream lineage:**
```
Trace lineage for gold_customer_360.email
What is the source of silver_orders.total_amount?
Show lineage for bronze_sales.customer_id
```

The system will show the full chain:
```
📊 Lineage chain:
  ↑ silver_customer_crm-email
    ↑ bronze_customer_raw-email
      ↑ raw_crm_contacts-email_address
```

**Find downstream impact:**
```
What depends on raw_customers.customer_id?
Show downstream impact of bronze_orders.order_id
```

### Subject Area Analysis

**Analyze subject areas:**
```
Show all subject areas
Which subject areas have complete pipelines?
Find subject areas with incomplete pipelines
What subject areas are in Gold layer?
```

**Check data source coverage:**
```
Show all data sources
What subject areas come from ERP System?
Which data sources reach Gold layer?
```

### Production & Mobilization

**Check deployment status:**
```
Show production datapoints
Find mobilized datapoints
Find critical data not in production
```

---

## Customization

### Using Your Own Data

1. **Prepare your Excel file** with two sheets:
   - "Dataset" sheet with dataset metadata
   - "DataPoint" sheet with column metadata

2. **Convert to Prolog:**
```bash
python excel_to_prolog.py your_metadata.xlsx
```

3. **Test:**
```bash
python test_system.py
```

4. **Query:**
```bash
python nl_interface.py
```

### Adding Custom Rules

Edit `metadata_kb.pl` to add domain-specific rules:

```prolog
% Example: Find high-risk datasets
high_risk_dataset(ViewName) :-
    dataset(_, ViewName, 'Gold', _, _, _, _, _, _, _, _, _),
    datapoint(_, _, _, _, _, _, ViewName, _, _, _, _, _, _, _,
              _, _, _, _, _, _, _, _, _, _, _, _, 'Confidential', _, _),
    \+ has_reviewer(ViewName).

% Example: Find datasets needing attention
needs_attention(ViewName, Reason) :-
    (   dataset_without_reviewer(ViewName),
        Reason = 'Missing Reviewer'
    ;   dataset_without_validator(ViewName),
        Reason = 'Missing Validator'
    ;   (   dataset(_, ViewName, 'Gold', _, _, _, _, _, _, _, _, _),
            confidential_data(ViewName, _),
            Reason = 'Gold layer with PII'
        )
    ).
```

### Extending Query Patterns

Edit `nl_interface.py` to add new question patterns:

```python
# Add to patterns list in translate_to_prolog method
(r'.*high.*risk.*datasets?',
 "high_risk_dataset(ViewName)",
 "Finding high-risk datasets..."),

(r'.*needs.*attention',
 "needs_attention(ViewName, Reason)",
 "Finding datasets needing attention..."),
```

---

## Troubleshooting

### Common Issues

**Issue: "No module named 'pyswip'"**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Issue: "Prolog connection failed"**
```bash
# Check SWI-Prolog is installed
swipl --version

# If not installed, install it:
# macOS: brew install swi-prolog
# Ubuntu: sudo apt-get install swi-prolog
```

**Issue: "File not found: metadata_facts.pl"**
```bash
# Generate the facts file:
python excel_to_prolog.py sample_metadata.xlsx
```

**Issue: "Query returns no results"**
- Check your question matches a known pattern
- Try: `python nl_interface.py` to see example questions
- Verify data was loaded: `python test_system.py`

**Issue: "Knowledge base loading failed"**
- Ensure `metadata_kb.pl` and `metadata_facts.pl` are in the same directory
- Check for syntax errors in Prolog files
- Try loading manually: `swipl -s metadata_kb.pl`

### Getting Help

1. Run tests to diagnose:
```bash
python test_system.py
```

2. Check example questions:
```bash
python nl_interface.py
# Then type: help
```

3. Verify your data:
```bash
# Check Excel file has both sheets
python -c "import pandas as pd; print(pd.ExcelFile('sample_metadata.xlsx').sheet_names)"
```

---

## Advanced Usage

### Batch Query Processing

Create a file `questions.txt`:
```
Show me all Gold datasets
Find governance violations
Where is confidential data?
```

Run batch queries:
```bash
while read question; do
    python nl_interface.py "$question"
done < questions.txt
```

### Exporting Results

Modify the interface to save results:

```python
import json

interface = NaturalLanguageInterface()
results = interface.ask("Show me all Gold datasets")

# Save as JSON
with open('results.json', 'w') as f:
    json.dump(results, f, indent=2)

# Save as CSV
import pandas as pd
pd.DataFrame(results).to_csv('results.csv', index=False)
```

### Integration with CI/CD

Use in automated checks:

```python
# check_governance.py
from nl_interface import NaturalLanguageInterface

interface = NaturalLanguageInterface()
violations = interface.ask("Find governance violations")

if len(violations) > 0:
    print(f"❌ {len(violations)} governance violations found!")
    for v in violations:
        print(f"   - {v}")
    exit(1)
else:
    print("✅ All governance checks passed!")
    exit(0)
```

Add to your pipeline:
```bash
python check_governance.py || exit 1
```

### Direct Prolog Queries

For advanced users who know Prolog:

```python
from pyswip import Prolog

prolog = Prolog()
prolog.consult('metadata_kb.pl')

# Custom query
query = "dataset(ID, ViewName, 'Gold', _, 'Customer', _, _, _, _, _, _, _)"
results = list(prolog.query(query))

for result in results:
    print(f"{result['ID']}: {result['ViewName']}")
```

### Performance Optimization

For large datasets (10K+ datapoints):

1. **Pre-compute expensive queries:**
```prolog
% Add to metadata_kb.pl
:- dynamic cached_lineage/3.

% Pre-compute lineages on load
:- forall(
    datapoint(_, _, _, _, _, _, View, Col, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _),
    (full_lineage(View, Col, Lineage), 
     assertz(cached_lineage(View, Col, Lineage)))
).
```

2. **Add indexes:**
```prolog
:- index(dataset(1,1,0,0,0,0,0,0,0,0,0,0)).
:- index(datapoint(1,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)).
```

---

## Best Practices

### Data Management

1. **Keep Excel as source of truth**
   - Version control the Excel file
   - Regenerate Prolog facts from Excel
   - Don't manually edit dataset_facts.pl and datapoint_facts.pl

2. **Document business rules**
   - Add comments to metadata_kb.pl
   - Explain why rules exist
   - Include examples

3. **Regular validation**
   - Run `test_system.py` after changes
   - Check for governance violations
   - Review lineage completeness

### Team Adoption

1. **Start with common questions**
   - "Show me Gold datasets"
   - "Find governance issues"
   - Build from there

2. **Create query library**
   - Document frequently used queries
   - Share with team
   - Add to team wiki

3. **Train incrementally**
   - Start with interface, not Prolog
   - Show value first
   - Teach customization later

---

## Support & Contributing

**Questions?** Open an issue on GitHub

**Bug reports?** Include:
- Error message
- Steps to reproduce
- System info (OS, Python version, Prolog version)

**Feature requests?** Describe:
- Use case
- Expected behavior
- Example queries

**Contributing?** See CONTRIBUTING.md

---

**Happy querying!** 🚀

---

## AI Enhancement with Ollama

### Why Use AI Enhancement?

The default pattern-matching works great for standard queries, but AI enhancement with Ollama provides:

✨ **Better Understanding**
- Handles complex, multi-part questions
- Understands context and nuance
- Works with typos and variations
- More natural conversation

✨ **Flexible Queries**
- "Show me all Gold datasets from the ERP system that don't have reviewers"
- "What's the lineage of that email column in the customer table?"
- "Find datasets with PII but no data stewards"

### Setup

1. **Install Ollama**
   ```bash
   # macOS/Linux
   curl https://ollama.ai/install.sh | sh
   
   # Or download from https://ollama.ai/
   ```

2. **Pull a Model**
   ```bash
   # Recommended: Llama 3.2 (fast, accurate)
   ollama pull llama3.2
   
   # Alternative: Mistral
   ollama pull mistral
   ```

3. **Verify Installation**
   ```bash
   ollama list
   # Should show llama3.2 or your chosen model
   ```

### Usage

**Interactive Mode with AI**:
```bash
python nl_interface.py --ai
```

**Command Line with AI**:
```bash
python nl_interface.py --ai "Find all the datasets with confidential information"
```

**In Python Scripts**:
```python
from nl_interface import NaturalLanguageInterface

# Enable AI
interface = NaturalLanguageInterface(use_ai=True)
results = interface.ask("Show me problematic datasets")
```

### Performance Comparison

| Mode | Query Understanding | Speed | Best For |
|------|-------------------|-------|----------|
| **Pattern Matching** | Good for standard queries | Instant | Quick lookups, standard questions |
| **AI Enhanced** | Excellent for any question | ~1-2 seconds | Complex questions, exploration |

### When AI Makes a Difference

**Pattern matching struggles with:**
```
❌ "What are the tables in the gold layer that come from SAP?"
❌ "Show me datasets with PII and no stewards"  
❌ "Find all the problematic customer data"
```

**AI enhancement handles these easily:**
```
✅ Understands compound queries
✅ Interprets "problematic" as governance violations
✅ Maps "tables" to "datasets", "SAP" to data source
```

### Troubleshooting AI Mode

**Issue: "Ollama not available"**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start Ollama
ollama serve
```

**Issue: "Model not found"**
```bash
# Pull the model
ollama pull llama3.2

# Verify
ollama list
```

**Issue: Slow responses**
- First query is slower (model loading)
- Subsequent queries are faster
- Use CPU mode: `OLLAMA_NUM_GPU=0 ollama serve`
- Or use smaller model: `ollama pull llama3.2:1b`

### Best Practices

1. **Use pattern matching first** for simple queries
2. **Enable AI for** complex questions or exploration
3. **Keep Ollama running** in background for faster responses
4. **Use specific terms** even with AI (helps accuracy)

### Example Session

```bash
$ python nl_interface.py --ai

🤖 Initializing Metadata AI System...
✅ System ready! Ask me anything about your data.
✅ Ollama AI enhancement enabled

💬 What would you like to know about your data?
> Find all datasets in the customer domain that have sensitive data but are missing data stewards

🧠 Using AI to understand your question...
🔍 Analyzing customer datasets with sensitive data...

✅ Found 3 results:
1. silver_customer_crm.email - Confidential
2. gold_customer_360.phone - Restricted  
3. bronze_customer_raw.ssn - Confidential

💬 What would you like to know about your data?
> What's the impact if I change that email column?

🧠 Using AI to understand your question...
🔍 Finding downstream impact of silver_customer_crm.email...

✅ Found 8 downstream dependencies:
1. gold_customer_360.email
2. gold_marketing_campaigns.recipient_email
...
```

---

## Switching Between Modes

You can use both modes depending on your needs:

```bash
# Quick lookup - use pattern matching (default)
python nl_interface.py "Show Gold datasets"

# Complex question - use AI
python nl_interface.py --ai "Find datasets with compliance issues"

# Exploration session - use AI for better conversation
python nl_interface.py --ai
```

The system will fall back to pattern matching if AI is unavailable, so it's always safe to use the `--ai` flag.

