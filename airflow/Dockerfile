# Official Airflow image as the base
FROM apache/airflow:2.7.0

WORKDIR /opt/airflow/

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
