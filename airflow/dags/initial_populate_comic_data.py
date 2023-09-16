"""
Airflow DAG to initially populate comic data.

This DAG aims handles the initial population of comic data into the database. 
It fetches comics from the last `n` days and inserts them into the database. 
This operation runs only once (no scheduled interval).
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
    'initial-populate-comic-data',
    default_args=default_args,
    description='A DAG to handle initial population of comic data',
    schedule_interval=None,
    start_date=datetime.now(pytz.utc),
    catchup=False,
)

def populate_comic_db(days: int=180):
    """
    Initially populate the comic database with comics from the last `days`.
    
    This function connects to the database, fetches comics from the last `days` 
    days, and then inserts them in batches into the database.
    
    :param days: The number of days to look back for fetching comics.
    :return: None
    """
    conn = helpers.connect_db(
        host="COMIC_POSTGRES_HOST",
        dbname="COMIC_POSTGRES_DB",
        user="COMIC_POSTGRES_USER",
        password="COMIC_POSTGRES_PASSWORD",
        port="COMIC_POSTGRES_PORT"
    )
    
    comics_list = helpers.inital_populate_comic_list(days)
    comics_as_tuples = helpers.convert_comic_list_to_tuples(comics_list)

    # Insert comics in batches of 10
    for i in range(0, len(comics_as_tuples), 10):
        batch = comics_as_tuples[i:i+10]
        helpers.execute_batch_sql(ComicSQLScripts.insert_comic, batch, conn)

# Run airflow task to initially populate comic data
initialise_db_task = PythonOperator(
    task_id='populate_comic_db',
    python_callable=populate_comic_db,
    dag=dag,
)

initialise_db_task
