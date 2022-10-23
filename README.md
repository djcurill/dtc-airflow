# dtc-airflow

Repository hosts all source code for running airglow dags to transfer NYC taxi data to a GCP data lake.

## Setup

### 1. Download docker-compose File from Airflow

Docker compose file contains everything to run an airflow server locally.

```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'
```

### 2. Change Memory Allocation in Docker Desktop

Docker desktop by default may not assign enough memory to run airflow server locally. Go to `Docker Desktop > Preferences` to assign at least 5GB of memory.

### 3. Environment Setup

Create three directories:

1. `dags` for storing all pipeline source code
2. `plugins` for custom utilities or plugin source code
3. `logs` log related information between scheduler and workers

Create the following airflow environment variables with the bash command below. The `-e` flag allows for backslash literals to be interpreted (i.e. `\t` will create a tab). We must use this command so that directories are not created by the root user. If the root user were to create these folders, we would need sudo access to have write permissions.

```bash
echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
```

### 4. Docker build
