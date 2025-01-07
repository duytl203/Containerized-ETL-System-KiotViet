FROM apache/airflow:2.10.0 

# Switch user to root
USER root

# Install java
RUN apt-get update 
RUN apt-get install -y openjdk-17-jdk

# Switch user back to airflow
USER airflow

# Install python deps
COPY pip_install_requirements.txt /app/
WORKDIR /app
RUN pip3 install -r pip_install_requirements.txt
