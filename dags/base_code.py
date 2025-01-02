import pandas as pd
import json, requests
import sonata.secret_file
from sqlalchemy import create_engine, text
from datetime import datetime

def extract_product_details(invoice_details):
    try:
        # Replace single quotes with double quotes and check the JSON string
        if invoice_details:
            invoice_details = invoice_details.replace("'", "\"")
            products = json.loads(invoice_details)
            
            extracted_data = []
            for product in products:
                extracted_data.append({
                    'product_id': product.get('productCode'),
                    'name': product.get('productName'),
                    'line_item_quantity': product.get('quantity'),
                    'line_item_sale_price': product.get('price'),
                    'line_item_rounded_amount': product.get('subTotal'),
                })
            return extracted_data
        else:
            return []
    except json.JSONDecodeError as e:
        return []  # Return an empty list if a JSON error occurs
    except Exception as e:
        return []


def get_information(table_name, portal, config, access_token, retailer):
    
    attributes = config['attribute']
    attribute_types = config['attribute_type']
    columns = config['column']

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
                elif dtype == 'string':
                    df[column] = df[column].astype(str)
                elif dtype == 'numeric':
                    df[column] = df[column].astype(float).fillna(0)    
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
    if 'invoiceDetails' in columns:
        df['invoiceDetails'] = df['invoiceDetails'].apply(extract_product_details)
        df['invoiceDetails'] = df['invoiceDetails'].apply(json.dumps)
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
