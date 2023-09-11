import os
from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from helpers import helpers


# Define the check_db_connection function
def check_db_connection():
    print(os.environ.get("COMIC_POSTGRES_HOST"))
    print(os.environ.get("COMIC_POSTGRES_DB"))
    print(os.environ.get("COMIC_POSTGRES_USER"))
    print(os.environ.get("COMIC_POSTGRES_PASSWORD"))
    print(os.environ.get("COMIC_POSTGRES_PORT"))
    conn = helpers.connect_db(
        host = "comic-postgres",
        dbname = "comicdb",
        user = "myuser",
        password = "mypassword",
        port = "5432"
    )
    print("db connection works")

# Define the default_args dictionary
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'start_date': datetime(2023, 9, 7)
}

# Instantiate the DAG
dag = DAG(
    'check_db_connection_dag',
    default_args=default_args,
    description='A DAG to check DB connection',
    schedule_interval=None,
    catchup=False
)

# Set up the PythonOperator
check_connection_task = PythonOperator(
    task_id='check_db_connection_task',
    python_callable=check_db_connection,
    dag=dag
)

# If there are other tasks, set the order using set_upstream or set_downstream methods, or the bitshift operators.
# Example:
# task1 >> check_connection_task >> task2
