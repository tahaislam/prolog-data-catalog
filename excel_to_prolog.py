"""
Excel to Prolog Facts Converter
Converts metadata Excel file to Prolog facts
"""

import pandas as pd
from pathlib import Path
import sys

def safe_prolog_value(value):
    """
    Convert a value to safe Prolog format
    - None/NaN → 'null'
    - Strings → quoted atoms with escaped quotes
    - Numbers → direct representation
    """
    if pd.isna(value) or value is None or value == '':
        return 'null'
    
    if isinstance(value, (int, float)):
        return str(value)
    
    # Convert to string and escape single quotes
    str_value = str(value).replace("'", "\\'")
    return f"'{str_value}'"

def convert_dataset_to_prolog(df, output_file):
    """Convert Dataset sheet to Prolog facts"""
    
    facts = []
    facts.append("% Dataset Facts")
    facts.append("% dataset(ViewID, ViewName, DataLayer, Name, SubjectArea, SubjectAreaSubCategory,")
    facts.append("%         DataSource, DataSourceID, Reviewer, TechnicalDesignReviewer, Processor, Validator).\n")
    
    for _, row in df.iterrows():
        fact = (
            f"dataset("
            f"{safe_prolog_value(row.get('ViewID'))}, "
            f"{safe_prolog_value(row.get('ViewName'))}, "
            f"{safe_prolog_value(row.get('DataLayer'))}, "
            f"{safe_prolog_value(row.get('Name'))}, "
            f"{safe_prolog_value(row.get('SubjectArea'))}, "
            f"{safe_prolog_value(row.get('SubjectAreaSubCategory'))}, "
            f"{safe_prolog_value(row.get('DataSource'))}, "
            f"{safe_prolog_value(row.get('DataSourceID'))}, "
            f"{safe_prolog_value(row.get('Reviewer'))}, "
            f"{safe_prolog_value(row.get('TechnicalDesignReviewer'))}, "
            f"{safe_prolog_value(row.get('Processor'))}, "
            f"{safe_prolog_value(row.get('Validator'))}"
            f")."
        )
        facts.append(fact)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(facts))
    
    return len(df)

def convert_datapoint_to_prolog(df, output_file):
    """Convert DataPoint sheet to Prolog facts (simplified structure)"""
    
    facts = []
    facts.append("% DataPoint Facts (Simplified Structure)")
    facts.append("% datapoint(DatapointID, SubjectArea, ViewID, ViewName, ColumnName, ColumnLabel,")
    facts.append("%           EnvironmentStatus, DbState, DataPointClass, Description,")
    facts.append("%           SourceDatapointID, SourceViewIDName, SourceViewIDColumnName,")
    facts.append("%           DataSteward, DataOwner, SensitivityLabel, SensitivityLabelRationale,")
    facts.append("%           CriticalDataElementIndicator).\n")
    
    for _, row in df.iterrows():
        fact = (
            f"datapoint("
            f"{safe_prolog_value(row.get('DatapointID'))}, "
            f"{safe_prolog_value(row.get('SubjectArea'))}, "
            f"{safe_prolog_value(row.get('ViewID'))}, "
            f"{safe_prolog_value(row.get('ViewName'))}, "
            f"{safe_prolog_value(row.get('ColumnName'))}, "
            f"{safe_prolog_value(row.get('ColumnLabel'))}, "
            f"{safe_prolog_value(row.get('EnvironmentStatus'))}, "
            f"{safe_prolog_value(row.get('DbState'))}, "
            f"{safe_prolog_value(row.get('DataPointClass'))}, "
            f"{safe_prolog_value(row.get('Description'))}, "
            f"{safe_prolog_value(row.get('SourceDatapointID'))}, "
            f"{safe_prolog_value(row.get('SourceViewIDName'))}, "
            f"{safe_prolog_value(row.get('SourceViewIDColumnName'))}, "
            f"{safe_prolog_value(row.get('DataSteward'))}, "
            f"{safe_prolog_value(row.get('DataOwner'))}, "
            f"{safe_prolog_value(row.get('SensitivityLabel'))}, "
            f"{safe_prolog_value(row.get('SensitivityLabelRationale'))}, "
            f"{safe_prolog_value(row.get('CriticalDataElementIndicator'))}"
            f")."
        )
        facts.append(fact)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(facts))
    
    return len(df)

def main(excel_file='Sample_Metadata.xlsx'):
    """Main conversion function"""
    
    excel_path = Path(excel_file)
    
    if not excel_path.exists():
        print(f"❌ Error: Excel file not found: {excel_file}")
        print(f"   Expected location: {excel_path.absolute()}")
        print(f"\n💡 Tip: Run generate_sample_data_simplified.py first!")
        sys.exit(1)
    
    print(f"📖 Reading Excel file: {excel_file}")
    
    try:
        # Read both sheets
        datasets_df = pd.read_excel(excel_file, sheet_name='Dataset')
        datapoints_df = pd.read_excel(excel_file, sheet_name='DataPoint')
        
        print(f"   ✅ Found {len(datasets_df)} datasets")
        print(f"   ✅ Found {len(datapoints_df)} datapoints")
        
        # Convert to Prolog
        print(f"\n🔄 Converting to Prolog facts...")
        
        dataset_count = convert_dataset_to_prolog(datasets_df, 'dataset_facts.pl')
        datapoint_count = convert_datapoint_to_prolog(datapoints_df, 'datapoint_facts.pl')
        
        print(f"   ✅ Generated dataset_facts.pl ({dataset_count} facts)")
        print(f"   ✅ Generated datapoint_facts.pl ({datapoint_count} facts)")
        
        # Show some stats
        print(f"\n📊 Summary:")
        print(f"   Layers: {sorted(datasets_df['DataLayer'].unique())}")
        print(f"   Subject Areas: {sorted(datasets_df['SubjectArea'].unique())}")
        print(f"   Data Sources: {sorted(datasets_df['DataSource'].unique())}")
        
        # Check for governance issues
        missing_reviewers = datasets_df['Reviewer'].isna().sum()
        missing_validators = datasets_df['Validator'].isna().sum()
        missing_stewards = datapoints_df['DataSteward'].isna().sum()
        
        print(f"\n⚠️  Governance gaps (intentional for demo):")
        print(f"   Datasets without reviewers: {missing_reviewers}")
        print(f"   Datasets without validators: {missing_validators}")
        print(f"   Datapoints without stewards: {missing_stewards}")
        
        print(f"\n🎯 Next steps:")
        print(f"   1. Check the generated files: dataset_facts.pl, datapoint_facts.pl")
        print(f"   2. Run: python nl_interface.py")
        print(f"   3. Or run: python test_system.py")
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()