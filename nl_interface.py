"""
Natural Language Interface for Prolog Data Catalog

This script provides a natural language interface with OPTIONAL AI enhancement via Ollama.
- Default mode: Pattern matching (fast, works offline)  
- AI mode (--ai): Advanced NLP with local Ollama (better understanding)

Usage:
    python nl_interface.py                    # Pattern matching mode
    python nl_interface.py --ai               # AI-enhanced mode
    python nl_interface.py "Show Gold datasets"
    python nl_interface.py --ai "Find compliance issues"
"""

import sys
import re
import os
import argparse
import requests
import json
from pyswip import Prolog

class NaturalLanguageInterface:
    def __init__(self, use_ai=False, kb_file='metadata_kb.pl'):
        """Initialize the Prolog interface with optional AI"""
        self.prolog = Prolog()
        self.use_ai = use_ai
        self.ollama_available = False
        self.ollama_model = 'llama3.2'  # Default, will be updated if other model found
        
        try:
            # Load the knowledge base (rules)
            if not os.path.exists(kb_file):
                print(f"❌ Knowledge base not found: {kb_file}")
                sys.exit(1)
            
            print(f"📚 Loading knowledge base: {kb_file}")
            self.prolog.consult(kb_file)
            
            # Load dataset facts
            if os.path.exists('dataset_facts.pl'):
                print(f"📊 Loading dataset facts")
                self.prolog.consult('dataset_facts.pl')
            
            # Load datapoint facts
            if os.path.exists('datapoint_facts.pl'):
                print(f"📍 Loading datapoint facts")
                self.prolog.consult('datapoint_facts.pl')
            
            print("✅ Knowledge base loaded!")
            
            # Initialize Ollama if AI mode requested
            if use_ai:
                self._init_ollama()
            
            print("💬 Ask me anything about your data.\n")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    def _init_ollama(self):
        """Initialize Ollama connection"""
        print("🤖 Checking Ollama...")
        
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                
                if not models:
                    print("⚠️  Ollama is running but NO MODELS INSTALLED")
                    print("   Install a model:")
                    print("   → ollama pull llama3.2")
                    print("   → ollama pull llama3.1")
                    print("   → ollama pull mistral")
                    self.ollama_available = False
                    return
                
                # Check if our preferred model is available
                model_names = [m.get('name', '') for m in models]
                has_llama32 = any('llama3.2' in name for name in model_names)
                has_llama31 = any('llama3.1' in name or 'llama3.1' in name for name in model_names)
                has_mistral = any('mistral' in name for name in model_names)
                
                if has_llama32:
                    self.ollama_model = 'llama3.2'
                    print(f"✅ AI mode enabled (using llama3.2)")
                elif has_llama31:
                    self.ollama_model = 'llama3.1'
                    print(f"✅ AI mode enabled (using llama3.1)")
                elif has_mistral:
                    self.ollama_model = 'mistral'
                    print(f"✅ AI mode enabled (using mistral)")
                else:
                    print(f"⚠️  Available models: {', '.join(model_names[:3])}")
                    print(f"   Recommended: ollama pull llama3.2")
                    # Try first available model anyway
                    self.ollama_model = model_names[0].split(':')[0]
                    print(f"   Trying {self.ollama_model}...")
                
                self.ollama_available = True
            else:
                print("⚠️  Ollama not responding properly")
                self.ollama_available = False
        except requests.exceptions.ConnectionError:
            print("⚠️  Ollama not running")
            print("   1. Install: https://ollama.ai")
            print("   2. Start: ollama serve")
            print("   3. Pull model: ollama pull llama3.2")
            self.ollama_available = False
        except Exception as e:
            print(f"⚠️  Ollama error: {e}")
            self.ollama_available = False
    
    def translate_with_ai(self, question):
        """Use Ollama for translation"""
        
        predicates_help = """Available Prolog predicates:

DATASET QUERIES:
- datasets_in_layer('Gold'|'Silver'|'Bronze', ViewName)
- datasets_in_subject_area('SubjectArea', ViewName)
- datasets_from_source('DataSource', ViewName)
- datasets_filtered('Layer', 'SubjectArea', ViewName)

GOVERNANCE QUERIES:
- dataset_without_reviewer(ViewName)
- dataset_without_validator(ViewName)
- dataset_with_governance_gap(ViewName)
- gold_without_governance(ViewName)
- datapoint_without_steward(ViewName, ColumnName)
- governance_violation(ViewName, ViolationType)

SECURITY QUERIES:
- confidential_data(ViewName, ColumnName)
- pii_data(ViewName, ColumnName)
- critical_data(ViewName, ColumnName)
- high_risk_data(ViewName, ColumnName, Reason)
- production_pii_without_steward(ViewName, ColumnName)

LINEAGE QUERIES:
- immediate_source(ViewName, ColumnName, SourceView, SourceCol)
- full_lineage(ViewName, ColumnName, Lineage)
- downstream_impact(SourceView, SourceCol, TargetView, TargetCol)

PIPELINE QUERIES:
- complete_pipeline(SubjectArea)
- incomplete_pipeline(SubjectArea)

COMBINED QUERIES (use these for complex questions):
For "Gold datasets without governance" use: gold_without_governance(ViewName)
For "PII without stewards" use: production_pii_without_steward(ViewName, ColumnName)
For "confidential data without stewards" use: confidential_data(ViewName, ColumnName), datapoint_without_steward(ViewName, ColumnName)
For "datasets with problems" use: governance_violation(ViewName, ViolationType)
"""
        
        prompt = f"""You are a Prolog query translator. Analyze the user's question and generate the MOST SPECIFIC query.

{predicates_help}

CRITICAL RULES:
1. Your goal is to combine predicates using commas (AND) and semicolons (OR).
2. NEVER wrap predicates inside other predicates (e.g., a(b(X)) is WRONG).
3. Use commas (,) for AND conditions.
4. Use semicolons (;) for OR conditions, and wrap them in parentheses: (a ; b).
5. Look for the MOST SPECIFIC predicate first (e.g., use 'gold_without_governance' instead of 'datasets_in_layer' + 'dataset_without_governance').
6. Your output MUST follow the pattern of the examples.
7. Return ONLY the query - no explanation, no markdown, no backticks.
8. Silver datasets means datasets_in_layer('Silver', ViewName), Gold datasets means datasets_in_layer('Gold', ViewName), etc.
9. Impact of removing or changing a dataset.column means tracing lineage: full_lineage('dataset', 'column', Lineage).

CORRECT Examples:
"Show Gold datasets" → datasets_in_layer('Gold', ViewName)
"Find governance violations" → governance_violation(ViewName, ViolationType)
"Gold datasets without governance" → gold_without_governance(ViewName)
"Find PII data" → pii_data(ViewName, ColumnName)
"Confidential data without stewards" → confidential_data(ViewName, ColumnName), datapoint_without_steward(ViewName, ColumnName)
"High risk data" → high_risk_data(ViewName, ColumnName, Reason)
"Silver datasets missing reviewers or validators" → datasets_in_layer('Silver', ViewName), (dataset_without_reviewer(ViewName) ; dataset_without_validator(ViewName))
"Trace lineage for A.B" → full_lineage('A', 'B', Lineage)

CORRECT EXAMPLES OF COMBINING RULES, NOT NESTING THEM:
Example 1:
Input: AND(a, b)
Output: a, b.

Example 2:
Input: OR(c, d)
Output: c ; d.

Example 2:
Input: AND(x, OR(y, z))
Output: 
    x, 
    (y ; z).

Now translate (return ONLY the query, no nesting):
User: "{question}"
Prolog:"""
        
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': self.ollama_model,  # Use detected model
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.2,  # Slightly higher for more flexibility
                        'num_predict': 100,
                        'top_p': 0.9
                    }
                },
                timeout=15  # Longer timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                query = result.get('response', '').strip()
                
                # Clean up the response
                query = query.replace('```prolog', '').replace('```', '')
                query = query.replace('```', '').strip()
                
                # Remove any explanatory text (take only first line)
                if '\n' in query:
                    query = query.split('\n')[0].strip()
                
                # Remove trailing period if present
                if query.endswith('.'):
                    query = query[:-1]
                
                # # VALIDATION: Check for incorrect nesting patterns
                # # Pattern: predicate(another_predicate(...))
                # if '(' in query and query.count('(') > query.count(',') + 1:
                #     # Possible nesting detected - try to fix it
                #     # Example: gold_without_governance(gold_without_reviewer(ViewName))
                #     # Should be: gold_without_governance(ViewName)
                    
                #     # Extract the outermost predicate
                #     import re
                #     match = re.match(r'([a-z_]+)\(', query)
                #     if match:
                #         outer_pred = match.group(1)
                #         # Simple fix: just use the outer predicate with ViewName
                #         query = f"{outer_pred}(ViewName)" if 'ViewName' in query else query
                #         print(f"   ⚠️  Fixed nested query to: {query}")
                
                if query:
                    return query, "🧠 AI understood..."
                
            return None, "AI translation failed"
        except:
            return None, "AI error"
    
    def pattern_match(self, question):
        """Pattern matching fallback"""
        q = question.lower().strip()
        
        patterns = [
            # COMPOUND PATTERNS - Check these FIRST for more specific matches!
            (r'gold.*(without|missing|no).*(governance|reviewer|validator)', 
             "gold_without_governance(ViewName)", 
             "Finding Gold datasets with governance gaps..."),
            
            (r'(confidential|pii|sensitive).*(without|missing|no).*steward', 
             "confidential_data(ViewName, ColumnName), datapoint_without_steward(ViewName, ColumnName)", 
             "Finding confidential data without stewards..."),
            
            (r'high.*risk', 
             "high_risk_data(ViewName, ColumnName, Reason)", 
             "Finding high-risk data..."),
            
            (r'(compliance|governance).*(problem|issue|violation|gap)', 
             "governance_violation(ViewName, ViolationType)", 
             "Checking governance violations..."),
            
            # SIMPLE PATTERNS - More general matches
            (r'gold.*datasets?', "datasets_in_layer('Gold', ViewName)", "Finding Gold datasets..."),
            (r'silver.*datasets?', "datasets_in_layer('Silver', ViewName)", "Finding Silver datasets..."),
            (r'bronze.*datasets?', "datasets_in_layer('Bronze', ViewName)", "Finding Bronze datasets..."),
            (r'subject areas?', "all_subject_areas(SubjectAreas)", "Finding subject areas..."),
            (r'data sources?', "all_data_sources(DataSources)", "Finding data sources..."),
            (r'governance.*violations?', "governance_violation(ViewName, ViolationType)", "Checking governance..."),
            (r'without.*reviewer', "dataset_without_reviewer(ViewName)", "Finding missing reviewers..."),
            (r'without.*validator', "dataset_without_validator(ViewName)", "Finding missing validators..."),
            (r'without.*steward', "datapoint_without_steward(ViewName, ColumnName)", "Finding missing stewards..."),
            (r'confidential', "confidential_data(ViewName, ColumnName)", "Finding confidential data..."),
            (r'pii', "pii_data(ViewName, ColumnName)", "Finding PII..."),
            (r'lineage for ([a-z_]+)\.([a-z_]+)', lambda m: f"full_lineage('{m.group(1)}', '{m.group(2)}', Lineage)", "Tracing lineage..."),
        ]
        
        for pattern, query_template, message in patterns:
            match = re.search(pattern, q)
            if match:
                query = query_template(match) if callable(query_template) else query_template
                return query, message
        
        return None, "❓ Try 'help' for examples"
    
    def translate_to_prolog(self, question):
        """Main translation logic"""
        if self.use_ai and self.ollama_available:
            query, msg = self.translate_with_ai(question)
            if query:
                return query, msg
        return self.pattern_match(question)
    
    def query(self, prolog_query):
        """Execute query - handles both simple and compound queries"""
        try:
            # Check if this is a compound query (contains comma)
            if ',' in prolog_query and not prolog_query.startswith('('):
                # This is a compound query like: confidential_data(V,C), datapoint_without_steward(V,C)
                # We need to execute it as a single compound query
                results = list(self.prolog.query(prolog_query))
                return results
            else:
                # Simple query
                results = list(self.prolog.query(prolog_query))
                return results
        except Exception as e:
            print(f"❌ Query error: {e}")
            print(f"   Query was: {prolog_query}")
            return []
    
    def format_results(self, results, query):
        """Format results"""
        if not results:
            return "No results found."
        
        output = [f"\nFound {len(results)} results:\n"]
        
        if 'ViewName' in results[0]:
            for i, r in enumerate(results, 1):
                output.append(f"  {i}. {r.get('ViewName')}")
        elif 'ColumnName' in results[0]:
            for i, r in enumerate(results, 1):
                output.append(f"  {i}. {r.get('ViewName')}.{r.get('ColumnName')}")
        elif 'ViolationType' in results[0]:
            violations = {}
            for r in results:
                vtype = r.get('ViolationType')
                if vtype not in violations:
                    violations[vtype] = []
                violations[vtype].append(r.get('ViewName'))
            for vtype, views in violations.items():
                output.append(f"\n  {vtype}:")
                for v in views[:5]:
                    output.append(f"    - {v}")
        else:
            for i, r in enumerate(results, 1):
                output.append(f"  {i}. {r}")
        
        return '\n'.join(output)
    
    def show_help(self):
        """Show help"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                 NATURAL LANGUAGE INTERFACE                        ║
╚══════════════════════════════════════════════════════════════════╝

EXAMPLES:
  • "Show me all Gold datasets"
  • "Find datasets without reviewers"
  • "Check governance violations"
  • "Find confidential data"
  • "Trace lineage for gold_customer_data.email"
  • "What are all the subject areas?"

COMMANDS:
  • help - Show this message
  • exit - Quit

TIP: Use --ai flag for better understanding!
  python nl_interface.py --ai
        """)
    
    def interactive_mode(self):
        """Interactive loop"""
        mode = "AI" if (self.use_ai and self.ollama_available) else "Pattern Matching"
        print(f"🎯 Mode: {mode}\n")
        
        while True:
            try:
                question = input("💬 You: ").strip()
                
                if not question:
                    continue
                if question.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                if question.lower() == 'help':
                    self.show_help()
                    continue
                
                prolog_query, message = self.translate_to_prolog(question)
                
                if not prolog_query:
                    print(f"\n{message}\n")
                    continue
                
                print(f"\n🔍 {message}")
                print(f"   Query: {prolog_query}\n")
                
                results = self.query(prolog_query)
                formatted = self.format_results(results, prolog_query)
                print(formatted + "\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='NL Interface for Prolog Data Catalog')
    parser.add_argument('question', nargs='*', help='Question to ask')
    parser.add_argument('--ai', action='store_true', help='Enable AI mode (Ollama)')
    args = parser.parse_args()
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║            🧠 PROLOG DATA CATALOG - NATURAL LANGUAGE             ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    interface = NaturalLanguageInterface(use_ai=args.ai)
    
    if args.question:
        question = ' '.join(args.question)
        prolog_query, message = interface.translate_to_prolog(question)
        
        if not prolog_query:
            print(f"\n{message}\n")
            sys.exit(1)
        
        print(f"\n🔍 {message}")
        print(f"   Query: {prolog_query}\n")
        results = interface.query(prolog_query)
        print(interface.format_results(results, prolog_query) + "\n")
    else:
        interface.interactive_mode()

if __name__ == '__main__':
    main()