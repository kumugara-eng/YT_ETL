ARG AIRFLOW_VERSION=2.9.2
ARG PYTHON_VERSION=3.11

FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

#  apache//aiflow is a base image that includes Airflow and Python, so we can directly use it as our base image.
ENV AIRFLOW_HOME=/opt/airflow   

# above we were specifying the AIRFLOW_HOME environment variable, which is the directory where Airflow will store its configuration and data. By default, it is set to /opt/airflow in the base image, but we are explicitly setting it here to ensure that it is available in our custom image as well.
COPY requirements.txt /

# above we are copying a requirements.txt file from our local directory to the root directory of the Docker image. This file should contain any additional Python dependencies that we want to install alongside Airflow base image.
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt

# above we are running a pip install command to install the specified version of Apache Airflow along with any additional dependencies listed in the requirements.txt file. The --no-cache-dir option is used to prevent pip from caching the downloaded packages, which can help reduce the size of the Docker image.