# Make required folders for airflow on docker host machine
mkdir -p ./dags ./logs ./plugins ./config

# Build docker image
sudo docker build -t airflow_config:local -f Dockerfile .

# Start cluster
sudo docker-compose up
