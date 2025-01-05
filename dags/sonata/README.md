**Step 1:**
Create the corresponding tables in the **table_attributes.json**:

   * **customers,products,categories,branches,invoices**: The tables I will create in pgadmin4 as well as the features I will call from kiotviet's API.
    
   * **kiotviet_column**: The variables I will call from the kiotviet API to correspond to the above tables.
    
   * **postgresql_column,postgresql_data_type**: The variables I will create in pgadmin4 to correspond to the above tables.
    
   * **schedule_interval**: The running time corresponds to the dag in **Airflow**

**Step 2:**
You can do the same with other portals, just change the name in the Sonata folder to the names you want and provide **access_token**, **retail_code**, **db url** information in **schedule_run.py**
