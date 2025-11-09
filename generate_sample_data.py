"""
Generate Anonymized Sample Metadata for Demo
Creates realistic but fictional data for the metadata system
"""

import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

def generate_sample_data(output_file='Sample_Metadata.xlsx'):
    """Generate sample metadata with realistic data catalog scenarios"""
    
    # Set seed for reproducibility
    random.seed(42)
    
    # Define subject areas and data sources
    subject_areas = [
        ('Customer', 'Customer Data', 'CRM Platform', 'CRM001'),
        ('Order', 'Order Management', 'Order System', 'ORDER001'),
        ('Product', 'Product Information', 'Product Catalog', 'PROD001'),
        ('Finance', 'Financial Data', 'ERP System', 'ERP001'),
        ('Sales', 'Sales Analytics', 'Sales Platform', 'SALES001'),
    ]
    
    # Column templates for each subject area
    column_templates = {
        'Customer': [
            ('customer_id', 'Customer ID', 'string', False),
            ('email', 'Email Address', 'string', True),
            ('phone', 'Phone Number', 'string', True),
            ('first_name', 'First Name', 'string', True),
            ('last_name', 'Last Name', 'string', True),
            ('address', 'Street Address', 'string', True),
            ('city', 'City', 'string', False),
            ('state', 'State', 'string', False),
            ('zip_code', 'Postal Code', 'string', True),
            ('registration_date', 'Registration Date', 'date', False),
            ('loyalty_tier', 'Loyalty Tier', 'string', False),
            ('total_lifetime_value', 'Total Lifetime Value', 'number', False),
        ],
        'Order': [
            ('order_id', 'Order ID', 'string', False),
            ('customer_id', 'Customer ID', 'string', False),
            ('order_date', 'Order Date', 'date', False),
            ('total_amount', 'Total Amount', 'number', False),
            ('order_status', 'Order Status', 'string', False),
            ('payment_method', 'Payment Method', 'string', True),
            ('shipping_address', 'Shipping Address', 'string', True),
            ('discount_applied', 'Discount Applied', 'number', False),
        ],
        'Product': [
            ('product_id', 'Product ID', 'string', False),
            ('product_name', 'Product Name', 'string', False),
            ('category', 'Category', 'string', False),
            ('price', 'Price', 'number', False),
            ('stock_quantity', 'Stock Quantity', 'number', False),
            ('supplier_id', 'Supplier ID', 'string', False),
            ('description', 'Description', 'string', False),
        ],
        'Finance': [
            ('transaction_id', 'Transaction ID', 'string', False),
            ('account_number', 'Account Number', 'string', True),
            ('amount', 'Amount', 'number', False),
            ('transaction_date', 'Transaction Date', 'date', False),
            ('transaction_type', 'Transaction Type', 'string', False),
            ('balance', 'Account Balance', 'number', True),
        ],
        'Sales': [
            ('sale_id', 'Sale ID', 'string', False),
            ('product_id', 'Product ID', 'string', False),
            ('quantity', 'Quantity Sold', 'number', False),
            ('revenue', 'Revenue', 'number', False),
            ('sale_date', 'Sale Date', 'date', False),
            ('region', 'Sales Region', 'string', False),
        ],
    }
    
    # Generate Dataset sheet
    datasets = []
    view_id_counter = 1
    
    # Define data stewards and owners
    stewards = ['Alice Johnson', 'Bob Smith', 'Carol Williams', 'David Brown', 'Eve Martinez']
    owners = ['Finance Team', 'Sales Team', 'Customer Service', 'Data Engineering', 'Product Team']
    processors = ['Data Engineering', 'Analytics Team', 'IT Department']
    
    for subject_area, subcategory, data_source, data_source_id in subject_areas:
        # Generate Bronze -> Silver -> Gold for each subject area
        for layer in ['Bronze', 'Silver', 'Gold']:
            view_name = f"{layer.lower()}_{subject_area.lower()}_data"
            
            # Some governance variations
            reviewer = random.choice(stewards) if random.random() > 0.1 else None
            tech_reviewer = random.choice(stewards) if random.random() > 0.15 else None
            validator = random.choice(stewards) if random.random() > 0.2 else None
            
            datasets.append({
                'ViewID': f'V{view_id_counter:04d}',
                'ViewName': view_name,
                'DataLayer': layer,
                'Name': f'{layer} {subject_area} View',
                'SubjectArea': subject_area,
                'SubjectAreaSubCategory': subcategory,
                'DataSource': data_source,
                'DataSourceID': data_source_id,
                'Reviewer': reviewer,
                'TechnicalDesignReviewer': tech_reviewer,
                'Processor': random.choice(processors),
                'Validator': validator,
            })
            
            view_id_counter += 1
    
    # Generate DataPoint sheet
    datapoints = []
    datapoint_id = 1
    
    for dataset in datasets:
        subject_area = dataset['SubjectArea']
        view_name = dataset['ViewName']
        layer = dataset['DataLayer']
        
        if subject_area in column_templates:
            columns = column_templates[subject_area]
            
            for col_name, col_label, data_type, is_sensitive in columns:
                # Determine source based on layer (lineage!)
                source_datapoint_id = None
                source_view_name = None
                source_column = None
                
                if layer == 'Silver':
                    # Silver comes from Bronze
                    bronze_view = view_name.replace('silver_', 'bronze_')
                    source_view_name = bronze_view
                    source_column = col_name
                    # Find the source datapoint ID (would be the bronze version)
                    source_datapoint_id = f'DP{datapoint_id-100:05d}' if datapoint_id > 100 else None
                    
                elif layer == 'Gold':
                    # Gold comes from Silver
                    silver_view = view_name.replace('gold_', 'silver_')
                    source_view_name = silver_view
                    source_column = col_name
                    source_datapoint_id = f'DP{datapoint_id-100:05d}' if datapoint_id > 100 else None
                
                # Determine sensitivity
                if is_sensitive:
                    sensitivity = random.choice(['Confidential', 'Restricted'])
                    sensitivity_rationale = 'Contains personally identifiable information (PII)'
                    critical = random.choice(['Yes', 'No'])
                else:
                    sensitivity = random.choice(['Internal', 'Public'])
                    sensitivity_rationale = 'Non-sensitive business data'
                    critical = 'No'
                
                # Assign data steward and owner
                steward = random.choice(stewards) if random.random() > 0.15 else None
                owner = random.choice(owners)
                
                # Environment status based on layer
                if layer == 'Bronze':
                    env_status = random.choice(['Production', 'Production', 'Development'])
                elif layer == 'Silver':
                    env_status = random.choice(['Production', 'UAT', 'Development'])
                else:  # Gold
                    env_status = random.choice(['Production', 'UAT'])
                
                # Database state
                db_state = random.choice(['Active', 'Active', 'Active', 'Deprecated'])
                
                datapoints.append({
                    'DatapointID': f'DP{datapoint_id:05d}',
                    'SubjectArea': subject_area,
                    'ViewID': dataset['ViewID'],
                    'ViewName': view_name,
                    'ColumnName': col_name,
                    'ColumnLabel': col_label,
                    'EnvironmentStatus': env_status,
                    'DbState': db_state,
                    'DataPointClass': data_type,
                    'Description': f"{col_label} for {subject_area} domain",
                    'SourceDatapointID': source_datapoint_id,
                    'SourceViewIDName': source_view_name,
                    'SourceViewIDColumnName': source_column,
                    'DataSteward': steward,
                    'DataOwner': owner,
                    'SensitivityLabel': sensitivity,
                    'SensitivityLabelRationale': sensitivity_rationale,
                    'CriticalDataElementIndicator': critical,
                })
                
                datapoint_id += 1
    
    # Create DataFrames
    datasets_df = pd.DataFrame(datasets)
    datapoints_df = pd.DataFrame(datapoints)
    
    # Write to Excel
    output_path = Path(output_file)
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        datasets_df.to_excel(writer, sheet_name='Dataset', index=False)
        datapoints_df.to_excel(writer, sheet_name='DataPoint', index=False)
    
    print(f"✅ Generated sample metadata: {output_file}")
    print(f"   📊 Datasets: {len(datasets)}")
    print(f"   📍 Datapoints: {len(datapoints)}")
    print(f"\n📁 File location: {output_path.absolute()}")
    
    return output_path

if __name__ == '__main__':
    output_file = generate_sample_data()
    print(f"\n🎯 Next steps:")
    print(f"   1. Run: python excel_to_prolog.py {output_file}")
    print(f"   2. Run: python nl_interface.py")
    print(f"   3. Ask questions!")