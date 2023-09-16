"""
Airflow DAG to insert comic data.

This DAG is designed to handle comic data by adding the most recent comic into 
a database. It runs twice a day to check and insert any new comics.
"""

import pytz
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from helpers import helpers
from helpers.sql_scripts import ComicSQLScripts

# DAG default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Instantiate DAG 
dag = DAG(
    'add-comic',
    default_args=default_args,
    description='A DAG to handle comic data',
    schedule_interval='0 22,10 * * *',  # Running twice a day (12am & 12pm CEST)
    start_date=datetime.now(pytz.utc),
    catchup=False,
)

def add_current_comic(conn):
    """
    Add the most recent comic to the database.
    
    This function connects to the database and checks if the most recent comic 
    is already present. If not, it adds the comic to the database.
    
    :param conn: The database connection object.
    :return: None
    """
    conn = helpers.connect_db(
        host="COMIC_POSTGRES_HOST",
        dbname="COMIC_POSTGRES_DB",
        user="COMIC_POSTGRES_USER",
        password="COMIC_POSTGRES_PASSWORD",
        port="COMIC_POSTGRES_PORT"
    )
    helpers.add_most_recent_comic(conn)

# Run airflow task and insert comic
initialise_db_task = PythonOperator(
    task_id='add_current_comic',
    python_callable=add_current_comic,
    dag=dag,
)
