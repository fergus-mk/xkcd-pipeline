# Use the official Airflow image as the base
FROM apache/airflow:2.7.0

# The WORKDIR instruction sets the working directory inside the container.
# All following commands will be run from this directory.
WORKDIR /opt/airflow/

# Copy your requirements file into the container
COPY requirements.txt ./

# Install your custom python packages
RUN pip install --no-cache-dir -r requirements.txt
