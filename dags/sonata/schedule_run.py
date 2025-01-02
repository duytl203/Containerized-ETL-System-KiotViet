from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime
from pathlib import Path
import base_code,json

portal = Path(__file__).parent.name

# Read data from JSON:
with open(f'/opt/airflow/dags/{portal}/table_attributes.json', 'r') as file:
    table_configs = json.load(file)
    
# Where you need to push access_token and retailcode of your business:
access_token, retailer = getattr(__import__(portal), 'secret_file').get_access_token()

db_url = getattr(__import__(portal), 'secret_file').get_db_url()

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'email_on_failure': False,
    'email_on_retry': False,
}

dags = {}

# Iterate through each item in the JSON to create DAGs
for key, config in table_configs.items():
    # Get Information from Json
    table_name = key
    schedule_interval = config['schedule_interval']
    # Create Dags:
    dag = DAG(
        f'sonata_{table_name}',
        default_args=default_args,
        description=f'ETL Job {table_name.title()} to PostgreSQL',
        schedule_interval=schedule_interval,
        catchup=False,
        start_date=datetime(2025, 1, 1),
    )

    # Definition of tasks:
    insert_task_operator = PythonOperator(
        task_id=f'insert_{table_name}_task',
        python_callable=base_code.get_information,
        op_args=[table_name, portal, config,access_token,retailer],
        dag=dag,
    )

    etl_task_operator = PythonOperator(
        task_id=f'etl_{table_name}_task',
        python_callable=base_code.insert_or_update_single,
        op_args=[table_name, portal, config,access_token,retailer,db_url],
        dag=dag,
    )

    # Define relationships between tasks
    insert_task_operator >> etl_task_operator

    # Add DAG to dictionary
    dags[f'sonata_{table_name}'] = dag

# Register DAGs with Airflow
globals().update(dags)

