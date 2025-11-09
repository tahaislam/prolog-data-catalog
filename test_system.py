"""
Test System for Prolog Data Catalog

This script verifies that the Prolog data catalog system is working correctly.
It tests: Prolog connection, knowledge base loading, basic queries, lineage, and governance.
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.7+"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (need 3.7+)")
        return False

def check_dependencies():
    """Check if required Python packages are installed"""
    print("🔍 Checking Python dependencies...")
    
    required = {
        'pyswip': 'PySwip',
        'pandas': 'Pandas',
        'openpyxl': 'OpenPyXL'
    }
    
    missing = []
    for package, name in required.items():
        try:
            __import__(package)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} (install with: pip install {package})")
            missing.append(package)
    
    return len(missing) == 0

def check_prolog():
    """Check if SWI-Prolog is installed and PySwip can connect"""
    print("🔍 Checking SWI-Prolog...")
    
    try:
        from pyswip import Prolog
        prolog = Prolog()
        # Test basic Prolog operation
        list(prolog.query("X = 1"))
        print("   ✅ SWI-Prolog working")
        return True
    except Exception as e:
        print(f"   ❌ SWI-Prolog error: {e}")
        print("   💡 Install from: https://www.swi-prolog.org/download/stable")
        return False

def check_files():
    """Check if required files exist"""
    print("🔍 Checking required files...")
    
    required_files = {
        'metadata_kb.pl': 'Knowledge base rules',
        'dataset_facts.pl': 'Dataset facts',
        'datapoint_facts.pl': 'Datapoint facts'
    }
    
    missing = []
    for filename, description in required_files.items():
        if os.path.exists(filename):
            print(f"   ✅ {filename} ({description})")
        else:
            print(f"   ❌ {filename} ({description})")
            missing.append(filename)
    
    if missing:
        print("\n   💡 Generate facts with:")
        print("      python generate_sample_data.py")
        print("      python excel_to_prolog.py")
        return False
    
    return True

def test_prolog_connection():
    """Test basic Prolog connection"""
    print("\n🧪 Testing Prolog connection...")
    
    try:
        from pyswip import Prolog
        prolog = Prolog()
        results = list(prolog.query("X = test"))
        if results and results[0].get('X') == 'test':
            print("   ✅ Prolog is working")
            return True, prolog
        else:
            print("   ❌ Prolog query returned unexpected results")
            return False, None
    except Exception as e:
        print(f"   ❌ Prolog connection failed: {e}")
        return False, None

def test_knowledge_base():
    """Test loading the knowledge base"""
    print("🧪 Testing knowledge base loading...")
    
    try:
        from pyswip import Prolog
        prolog = Prolog()
        
        # Load the knowledge base
        if not os.path.exists('metadata_kb.pl'):
            print("   ❌ metadata_kb.pl not found")
            return False, None
        
        prolog.consult('metadata_kb.pl')
        
        # Load the fact files
        if os.path.exists('dataset_facts.pl'):
            prolog.consult('dataset_facts.pl')
        else:
            print("   ⚠️  dataset_facts.pl not found")
            
        if os.path.exists('datapoint_facts.pl'):
            prolog.consult('datapoint_facts.pl')
        else:
            print("   ⚠️  datapoint_facts.pl not found")
        
        print("   ✅ Knowledge base loaded")
        return True, prolog
        
    except Exception as e:
        print(f"   ❌ Knowledge base loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def safe_query(prolog, query_str, description):
    """Safely execute a Prolog query and return results"""
    try:
        results = list(prolog.query(query_str))
        return True, results
    except Exception as e:
        print(f"   ❌ {description}: Caused by: '{query_str}'. Returned: '{e}'.")
        return False, []

def test_basic_queries(prolog):
    """Test basic dataset queries"""
    print("🧪 Testing basic queries...")
    
    all_passed = True
    
    # Test 1: Count Gold datasets
    success, results = safe_query(prolog, "datasets_in_layer('Gold', ViewName)", 
                                  "Count Gold datasets")
    if success:
        print(f"   ✅ Count Gold datasets: Found {len(results)} datasets")
    else:
        all_passed = False
    
    # Test 2: Count Silver datasets
    success, results = safe_query(prolog, "datasets_in_layer('Silver', ViewName)", 
                                  "Count Silver datasets")
    if success:
        print(f"   ✅ Count Silver datasets: Found {len(results)} datasets")
    else:
        all_passed = False
    
    # Test 3: Count Bronze datasets
    success, results = safe_query(prolog, "datasets_in_layer('Bronze', ViewName)", 
                                  "Count Bronze datasets")
    if success:
        print(f"   ✅ Count Bronze datasets: Found {len(results)} datasets")
    else:
        all_passed = False
    
    # Test 4: Get all subject areas
    success, results = safe_query(prolog, "all_subject_areas(SubjectAreas)", 
                                  "Get all subject areas")
    if success:
        if results:
            subject_areas = results[0].get('SubjectAreas', [])
            print(f"   ✅ Get all subject areas: Found {len(subject_areas)} areas")
        else:
            print(f"   ✅ Get all subject areas: Query succeeded (no results)")
    else:
        all_passed = False
    
    # Test 5: Get all data sources
    success, results = safe_query(prolog, "all_data_sources(DataSources)", 
                                  "Get all data sources")
    if success:
        if results:
            data_sources = results[0].get('DataSources', [])
            print(f"   ✅ Get all data sources: Found {len(data_sources)} sources")
        else:
            print(f"   ✅ Get all data sources: Query succeeded (no results)")
    else:
        all_passed = False
    
    # Test 6: Find datasets without reviewers
    success, results = safe_query(prolog, "dataset_without_reviewer(ViewName)", 
                                  "Find datasets without reviewers")
    if success:
        print(f"   ✅ Find datasets without reviewers: Found {len(results)} datasets")
    else:
        all_passed = False
    
    # Test 7: Find confidential data
    success, results = safe_query(prolog, "confidential_data(ViewName, ColumnName)", 
                                  "Find confidential data")
    if success:
        print(f"   ✅ Find confidential data: Found {len(results)} datapoints")
    else:
        all_passed = False
    
    return all_passed

def test_lineage_queries(prolog):
    """Test lineage tracing"""
    print("🧪 Testing lineage queries...")
    
    # First, find any datapoint with a source
    success, results = safe_query(prolog, 
                                  "immediate_source(View, Col, Source, SourceCol)",
                                  "Lineage queries")
    
    if not success:
        return False
    
    if not results:
        print("   ⚠️  No lineage found (all datapoints are source/bronze)")
        return True
    
    print(f"   ✅ Found {len(results)} lineage relationships")
    
    # Test full lineage on first result
    if results:
        first = results[0]
        view = first.get('View')
        col = first.get('Col')
        
        success, lineage_results = safe_query(prolog,
                                              f"full_lineage('{view}', '{col}', Lineage)",
                                              f"Full lineage for {view}.{col}")
        if success:
            print(f"   ✅ Full lineage trace working")
            return True
    
    return False

def test_governance_rules(prolog):
    """Test governance violation detection"""
    print("🧪 Testing governance rules...")
    
    success, results = safe_query(prolog, 
                                  "governance_violation(ViewName, ViolationType)",
                                  "Governance rules")
    
    if not success:
        return False
    
    print(f"   ✅ Found {len(results)} governance violations")
    
    # Show examples
    if results:
        for i, result in enumerate(results[:3], 1):
            view = result.get('ViewName')
            violation = result.get('ViolationType')
            print(f"      {i}. {view}: {violation}")
        if len(results) > 3:
            print(f"      ... and {len(results) - 3} more")
    
    return True

def main():
    """Run all tests"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     🧪 PROLOG DATA CATALOG - SYSTEM VERIFICATION TEST            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    tests = []
    
    # Pre-flight checks
    if not check_python_version():
        print("\n❌ Python version check failed")
        return
    
    if not check_dependencies():
        print("\n❌ Dependency check failed")
        return
    
    if not check_prolog():
        print("\n❌ Prolog check failed")
        return
    
    if not check_files():
        print("\n❌ File check failed")
        return
    
    # Prolog connection test
    success, prolog = test_prolog_connection()
    tests.append(("Prolog Connection", success))
    if not success:
        print("\n❌ Cannot proceed without Prolog connection")
        print_summary(tests)
        return
    
    # Knowledge base test
    success, prolog = test_knowledge_base()
    tests.append(("Knowledge Base", success))
    if not success:
        print("\n❌ Cannot proceed without knowledge base")
        print_summary(tests)
        return
    
    # Query tests
    tests.append(("Basic Queries", test_basic_queries(prolog)))
    tests.append(("Lineage Queries", test_lineage_queries(prolog)))
    tests.append(("Governance Rules", test_governance_rules(prolog)))
    
    print_summary(tests)

def print_summary(tests):
    """Print test summary"""
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 SUCCESS! All tests passed!")
        print("\n🚀 Your system is ready to use!")
        print("   Try: python nl_interface.py")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\n💡 Common fixes:")
        print("   1. Regenerate data: python generate_sample_data.py")
        print("   2. Convert to Prolog: python excel_to_prolog.py")
        print("   3. Check file names match")

if __name__ == '__main__':
    main()