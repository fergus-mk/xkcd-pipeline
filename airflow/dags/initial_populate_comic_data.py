import pytz
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

from helpers import helpers
from helpers.sql_scripts import ComicSQLScripts

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'initial-populate-comic-data',
    default_args=default_args,
    description='A DAG to handle comic data',
    schedule_interval=None,
    start_date=datetime.now(pytz.utc),
    catchup=False,
)

def populate_db(days: int=180):
    """Inital populate comic db with comics within x days"""
    conn = helpers.connect_db(
        host = "COMIC_POSTGRES_HOST",
        dbname = "COMIC_POSTGRES_DB",
        user = "COMIC_POSTGRES_USER",
        password = "COMIC_POSTGRES_PASSWORD",
        port = "COMIC_POSTGRES_PORT"  
    )

    comics_list = helpers.inital_populate_comic_list(days)
    comics_as_tuples = helpers.convert_comic_list_to_tuples(comics_list)

    # Insert comics in batches of 10
    for i in range(0, len(comics_as_tuples), 10):
        batch = comics_as_tuples[i:i+10]
        helpers.execute_batch_sql(ComicSQLScripts.insert_comic, batch, conn)

    print(f"{comics_list}")
    print(f"Thre are {len(comics_list)} total comics")

# Run airflow task and insert xkcd data 
initialise_db_task = PythonOperator(
    task_id='populate_db',
    python_callable=populate_db,
    dag=dag,
)

initialise_db_task
