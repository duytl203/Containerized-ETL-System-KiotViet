# Containerized-ETL-System
This is a side project I am working on for my uncle, aiming to manage data more efficiently and sustainably in the long term.

**Note that this only applies to the KiotViet data source.**

# Description Content
• Implement Apache Airflow on Docker
Container hosted on VirtualBox Machine
running Ubuntu 20.04.

• Implement PostgreSQL Database and
design schemas, boost performance by
applying optimal indexing and partitioning
strategy as well as defining various
triggers and constraints.

• Define Airflow DAGs to multiple ETL
modes (Daily, Backfill).

• Execute data quality checks.

• Toolkit: Python, DBEaver, VirtualBox,
Linux, Postman.

# Instructions for use:  
• Install your **airflow** with the following:

sudo chmod +x start.sh

• Read README.md in dags/sonata to build your pipeline to integrate data from **KiotViet** to **PostgreSQL**.


./start.sh

