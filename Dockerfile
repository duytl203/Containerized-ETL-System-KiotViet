FROM apache/airflow:2.10.0 

# Optional env variables
ENV AIRFLOW_UID=50000

# Switch user to root
USER root

# Install java
RUN apt-get update 
RUN apt-get install -y openjdk-17-jdk

# Switch user back to airflow
USER airflow

# Install python deps
RUN pip3 install -r adfuel_ftp_requirements.txt
