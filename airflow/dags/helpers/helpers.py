import os
import psycopg2
import requests
from datetime import datetime, timedelta
from decouple import config
from helpers.sql_scripts import ComicSQLScripts

# db conncect functions
def connect_db(host: str, dbname: str, user: str, password: str, port: int):
    """
    Establish a connection to the PostgreSQL database using environment variables.

    :param host: Environment variable key for database host.
    :param dbname: Environment variable key for database name.
    :param user: Environment variable key for database user.
    :param password: Environment variable key for database password.
    :param port: Environment variable key for database port.
    :return: psycopg2 database connection object.
    """
    return psycopg2.connect(
        host=os.environ.get(host),
        database=os.environ.get(dbname),
        user=os.environ.get(user),
        password=os.environ.get(password),
        port=os.environ.get(port)
    )

# Populate comic functions
def get_comic_info(comic_number=None) -> dict:
    """
    Fetch metadata for a specific xkcd comic. If comic_number isn't provided, fetch the most recent comic.

    :param comic_number: Comic issue number to fetch, or None for the latest comic.
    :return: Dictionary containing comic metadata.
    """
    url = f'https://xkcd.com/{comic_number if comic_number else ""}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()  # Raises an exception if the GET request was not successful
    return response.json()  # Parse the JSON response

def extract_date_from_comic(comic_dict: dict) -> datetime:
    """
    Extract the publication date of a comic from its metadata dictionary.

    :param comic_dict: Dictionary containing comic metadata.
    :return: Datetime object representing the comic's publication date.
    """
    year = int(comic_dict['year'])
    month = int(comic_dict['month'])
    day = int(comic_dict['day'])
    return datetime(year, month, day)

def get_comic_issue_no(comic_dict: dict) -> int:
    """
    Extract the issue number of a comic from its metadata dictionary.

    :param comic_dict: Dictionary containing comic metadata.
    :return: Integer representing the comic's issue number.
    """
    return comic_dict['num']

def date_compare(date1: datetime, date2: datetime) -> bool:
    """
    Compare two dates to determine if the first date is after the second date.

    :param date1: The first datetime object.
    :param date2: The second datetime object.
    :return: True if date1 is after date2, otherwise False.
    """
    return date1 > date2

def date_x_days_ago(x: int) -> datetime:
    """
    Calculate the date x days ago from the current date.

    :param x: Number of days to subtract from the current date.
    :return: Datetime object representing the date x days ago.
    """
    return datetime.now() - timedelta(days=x)

def inital_populate_comic_list(no_of_days: int) -> list:
    """
    Retrieve a list of comics from xkcd that were published within the last no_of_days.

    :param no_of_days: Number of days to look back.
    :return: List of dictionaries, each containing metadata for a comic.
    """
    comics_list = []
    most_recent_comic = get_comic_info()
    comic_issue_no = get_comic_issue_no(most_recent_comic)

    while True:
        comic = get_comic_info(comic_issue_no)
        comic_date = extract_date_from_comic(comic)
        max_back_date = date_x_days_ago(no_of_days)

        if not date_compare(comic_date, max_back_date):
            break

        comics_list.append(comic)
        comic_issue_no -= 1

    return comics_list

def convert_comic_list_to_tuples(comics_list: list) -> list:
    """
    Convert a list of comic metadata dictionaries into a list of tuples suitable for database insertion.

    :param comics_list: List of dictionaries, each containing metadata for a comic.
    :return: List of tuples, each representing a comic's metadata.
    """
    return [
        (comic["month"], comic["num"], comic["link"], comic["year"],
        comic["news"], comic["safe_title"], comic["transcript"], comic["alt"],
        comic["img"], comic["title"], comic["day"])
        for comic in comics_list
    ]

def comic_dict_to_tuple(comic_dict: dict) -> tuple:
    """
    Convert a single comic metadata dictionary into a tuple suitable for database insertion.

    :param comic_dict: Dictionary containing comic metadata.
    :return: Tuple representing the comic's metadata.
    """
    return (
        comic_dict['month'], comic_dict['num'], comic_dict['link'],
        comic_dict['year'], comic_dict['news'], comic_dict['safe_title'],
        comic_dict['transcript'], comic_dict['alt'], comic_dict['img'],
        comic_dict['title'], comic_dict['day']
    )

def check_if_comic_in_db(conn, comic_num: int) -> bool:
    """
    Check if a comic with a specific issue number is already present in the database.

    :param conn: Active database connection.
    :param comic_num: Comic issue number to check.
    :return: True if the comic is in the database, otherwise False.
    """
    comic_details = execute_sql(
        query=ComicSQLScripts.select_comic_by_num,
        params=(comic_num,),
        connection=conn
    )
    return bool(comic_details)

def add_most_recent_comic(conn):
    """
    Fetch the most recent comic from xkcd and add it to the database if it's not already present.

    :param conn: Active database connection.
    :return: None
    """
    current_comic = get_comic_info()
    current_comic_num = current_comic['num']
    current_comic_tuple = comic_dict_to_tuple(current_comic)

    if check_if_comic_in_db(conn, current_comic_num):
        print(f"comic with num {current_comic_num} already in db") # Visible in ariflow logs
    else:
        execute_sql(ComicSQLScripts.insert_comic, current_comic_tuple, conn)

# Execute SQL scripts functions
def execute_batch_sql(query, params_list, connection):
    """
    Execute a batch SQL insert.

    :param query: The SQL query string.
    :param params_list: A list of tuples, each containing parameters for the SQL query.
    :param connection: Active database connection.
    :return: None
    """
    try:
        with connection.cursor() as cursor:
            cursor.executemany(query, params_list)
            connection.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def execute_sql(query, params, connection):
    """
    Execute a single SQL statement.

    :param query: The SQL query string.
    :param params: A tuple containing parameters for the SQL query.
    :param connection: Active database connection.
    :return: Results if it's a SELECT query, otherwise None
    """
    results = None

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)

            # If the query is a SELECT statement, fetch the results
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()

            # Otherwise, commit the changes
            else:
                connection.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
        raise

    return results
