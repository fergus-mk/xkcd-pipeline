import os
import requests # Install
from datetime import datetime, timedelta
import psycopg2
from decouple import config

# Connection
def connect_db(host: str, dbname: str, user: str, password: str, port: int):
    """Connects to db using config variables from .env file"""
    return psycopg2.connect(
        host=os.environ.get(host),
        database=os.environ.get(dbname),
        user=os.environ.get(user),
        password=os.environ.get(password),
        port=os.environ.get(port)
    )

# Accesing xkcd metadata
def get_comic_info(comic_number=None) -> dict:
    """If comic_number is None, fetch the current comic, otherwise fetch the comic with comic_number"""
    url = f'https://xkcd.com/{comic_number if comic_number else ""}/info.0.json'

    response = requests.get(url)

    response.raise_for_status()  # Raises an exception if the GET request was not successful

    json_response = response.json()  # Parse the JSON response

    return json_response

def extract_date_from_comic(comic_dict: dict)-> datetime:
    """Extracts the datetime from comic dictionary"""
    year = int(comic_dict['year'])
    month = int(comic_dict['month'])
    day = int(comic_dict['day'])
    
    return datetime(year, month, day)

def get_comic_issue_no(comic_dict: dict)-> int:
    """Gets the issue number of input comic"""
    return comic_dict['num']

def date_compare(date1: datetime, date2: datetime)-> bool:
    """Returns True if date1 is after date2, otherwise returns False"""
    if date1 > date2:
        return True
    else:
        return False

def date_x_days_ago(x: int):
    """This function calculates date x days ago from current date, returns datetime object"""
    current_date = datetime.now()
    return current_date - timedelta(days=x)

def inital_populate_comic_list(no_of_days: int):
    """Create a list of comic JSONs from the last X days"""
    comics_list = []
    
    most_recent_comic = get_comic_info()
    comic_issue_no = get_comic_issue_no(most_recent_comic)

    while True:
        comic = get_comic_info(comic_issue_no)
        comic_date = extract_date_from_comic(comic)
        max_back_date = date_x_days_ago(no_of_days)  # The furthest date back to get comics

        if not date_compare(comic_date, max_back_date):  # Check if comic within timeframe
            break 

        comics_list.append(comic)
        comic_issue_no -= 1

    return comics_list

def convert_comic_list_to_tuples(comics_list: list) ->list:
    """Takes a lits of comic dictionaries and converts into a list of tuples"""
    return [
        (comic["month"], comic["num"], comic["link"], comic["year"],
        comic["news"], comic["safe_title"], comic["transcript"], comic["alt"],
        comic["img"], comic["title"], comic["day"])
        for comic in comics_list
    ]

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