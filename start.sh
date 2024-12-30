# Make required folders for airflow on docker host machine
mkdir -p ./dags ./logs ./plugins ./config

# Optional env variables
echo -e "AIRFLOW_UID=50000" > /home/duytl/airflow_config/.env

# Build docker image
sudo docker build -t airflow_config:local -f Dockerfile .

# Start cluster
sudo docker-compose up