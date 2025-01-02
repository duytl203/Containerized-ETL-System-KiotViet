**Step 1:**
Create the corresponding tables in the **table_attributes.json**:

   * **customers,products,categories,branches,invoices**: The tables I will create in pgadmin4 as well as the features I will call from kiotviet's API.
    
   * **attribute**: The variables I will call from the kiotviet API to correspond to the above tables.
    
   * **column,attribute_type**: The variables I will create in pgadmin4 to correspond to the above tables.
    
   * **schedule_interval**: The running time corresponds to the dag in **Airflow**

**Step 2:**
Create all tables in pgadmin4 with create_table.sql
