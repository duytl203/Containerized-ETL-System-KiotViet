import pandas as pd
import json, requests
import sonata.secret_file
from sqlalchemy import create_engine, text
from datetime import datetime

def extract_product_details(invoice_details,column_mapping):
    try:
        # Check if invoice_details is not None or empty
        if not invoice_details:
            return []

        # Replace single quotes with double quotes for valid JSON parsing
        invoice_details = invoice_details.replace("'", "\"")

        # Parse the JSON string
        products = json.loads(invoice_details)

        # Extract and map product details
        extracted_data = []
        for product in products:
            mapped_product = {
                column_mapping[key]: product.get(key)
                for key in column_mapping.keys()
                if key in product
            }
            extracted_data.append(mapped_product)

        return extracted_data

    except json.JSONDecodeError:
        # Handle JSON parsing errors
        return []
    except Exception as e:
        # Handle unexpected errors
        return []


def get_information(table_name, portal, config, access_token, retailer):
    attributes = config['kiotviet_column']
    attribute_types = config['postgresql_data_type']
    columns = config['postgresql_column']

    rename_mapping = dict(zip(attributes, columns))
    column_types = dict(zip(attributes, attribute_types))
    
    if not access_token:
        print("Failed to retrieve access token.")
        return
    
    api_endpoint = f'https://publicfnb.kiotapi.com/{table_name}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Retailer': retailer  # Replace with your retailer code
    }

    try:
        response = requests.get(api_endpoint, headers=headers)
        if response.status_code == 200:
            tables = response.json()
            data = tables['data']   
            df = pd.DataFrame(data, columns=attributes)
            
            for column, dtype in column_types.items():
                if dtype == 'timestamp':
                    df[column] = pd.to_datetime(df[column], errors='coerce').fillna(pd.Timestamp.now())
                elif dtype in ('string','jsonb'):
                    df[column] = df[column].astype(str)
                elif dtype == 'numeric':
                    df[column] = df[column].astype(float).fillna(0)   

            if 'invoiceDetails' in columns:
                mapping_config = config.get('invoices_detail', {})
                df['invoiceDetails'] = df['invoiceDetails'].apply(lambda details: extract_product_details(details, mapping_config))
                df['invoiceDetails'] = df['invoiceDetails'].apply(json.dumps)   
            return df.rename(columns=rename_mapping).sort_values('updated_date'), table_name
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

def insert_or_update_single(table_name, portal, config, access_token, retailer, db_url):
    # Get the list of columns from the DataFrame
    df, table_name = get_information(table_name, portal, config, access_token, retailer)
    columns = df.columns.tolist()
    # Create a connection to PostgreSQL
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            # Create the SQL insert or update statement
            insert_update_sql = f"""
                INSERT INTO public.{table_name} ({', '.join(columns)}) 
                VALUES ({', '.join([f':{col}' for col in columns])})
                ON CONFLICT ({columns[0]}) -- Assuming the first column is the PRIMARY KEY
                DO UPDATE SET {', '.join([f'{col} = EXCLUDED.{col}' for col in columns[1:]])}
            """
            # Iterate through each row of the DataFrame
            for _, row in df.iterrows():
                values = {col: row[col] for col in columns}
                conn.execute(text(insert_update_sql), values)
        print(f"Data successfully inserted/updated into table: {table_name}")
    except Exception as e:
        print(f"Error inserting/updating table {table_name}: {e}")
