import os
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'comic_data_dag',
    default_args=default_args,
    description='A DAG to handle comic data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 9, 9),
    catchup=False,
)

def initialise_db():
    import psycopg2
    conn = psycopg2.connect(
        host=os.environ.get("COMIC_POSTGRES_HOST"),
        database=os.environ.get("COMIC_POSTGRES_DB"),
        user=os.environ.get("COMIC_POSTGRES_USER"),
        password=os.environ.get("COMIC_POSTGRES_PASSWORD"))
    cur = conn.cursor()

    # Insert dummy values
    dummy_data = [
        (1, 1, 12, "link1", 2023, "news1", "safe_title1", "transcript1", "alt1", "img1", "title1", 1),
        (2, 2, 12, "link2", 2023, "news2", "safe_title2", "transcript2", "alt2", "img2", "title2", 2),
        (3, 3, 12, "link3", 2023, "news3", "safe_title3", "transcript3", "alt3", "img3", "title3", 3)
    ]

    insert_query = """
        INSERT INTO comics (id, month, num, link, year, news, safe_title, transcript, alt, img, title, day)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    cur.executemany(insert_query, dummy_data)

    conn.commit()
    cur.close()
    conn.close()


# Airflow task that calls the Python function to run the SQL and insert dummy values
initialise_db_task = PythonOperator(
    task_id='initialise_db',
    python_callable=initialise_db,
    dag=dag,
)

initialise_db_task

