# xkcd-pipeline design

These are the instructions for the design of the xkcd pipeline. The pipeline extracts XKCD metadata  on a daily basis it stores this to a db and makes this available via an API. 

This offers improved functionality compared to the current XKCD API (avialable at: https://xkcd.com/json.html). Improved functionality includes a OpenAPI/Swagger docs interface (pictured below) and the option to extract metadata for multiple comics at once. Note the current XKCD is utelissed in the pipeline for accessing data. In this design description first a high-level design is shown, followed by an overview of the project structure.

## Diagram

The picture above shows the key components of the pipeline:

1. **Docker** - A docker-compose.yml file is used to create containers for the different services. This includes multiple containers required for airflow (scheduler, db, tirgger etc.), a container for the PostgreSQL where details of the XKCD comics are stored and a contianer for  FastAPI. Note both FastAPI and Airflow have their own custom images allowing installing of python packages from requirements.txt files.

2. **Airflow** - Airflow serves as the scheduler executing the Python daf indicated in #3 which populates the db with the latest comic. It executes the dag on a daily basis.

3. **Python** - This airlfow dag (Python script) uses the curent comic interface (https://xkcd.com/info.0.json) to access the latest available comic. It uses a simple check to see if a comic with that id is present in the db and uses SQL INSERT to add to the db if not.

4. **Python** - This is the intial script to populate the db with comics from the past 180 days. It runs a simple extract to get the datetime of each comic:

```
def extract_date_from_comic(comic_dict: dict)-> datetime:
    """Extracts the datetime from comic dictionary"""
    year = int(comic_dict['year'])
    month = int(comic_dict['month'])
    day = int(comic_dict['day'])
    
    return datetime(year, month, day)
```
Then uses while to iterate through comics until a comic exceeding 180 days old at which stage it breaks
```
while True:
    extract_date_from_comic(comic)
    iterator += 1
```
An iterator is used to count the number of comics, when this reaches 20, a SQL Insert script is called. This improves pipeline speed as write doesn't have to happen for each indiidual comic.

*Note - For both #3 and #4 all functions are stored in 'airflow/crud/crud.py' to avoid duplicate code. The functions execute SQL saved in 'airflow/crud/sql_crud.sql'

5. **PostgreSQL** This is the Postgres table. This is created with 'sql/initalise.sql'

```
CREATE TABLE xkcd_comics (
    id SERIAL PRIMARY KEY,  -- An auto-incrementing ID for each comic entry
    month INT,
    num INT,
    link VARCHAR(255),
    year INT,
    news TEXT,
    safe_title VARCHAR(255),
    transcript TEXT,
    alt TEXT,
    img VARCHAR(255),
    title VARCHAR(255),
    day INT
);
```

Within docker-compose.yml this dir is mounted and executed when the container is intialised 

```
  volumes:
    - comic-postgres-db-volume:/var/lib/postgresql/data
    - ./sql-scripts:/docker-entrypoint-initdb.d
```

6. This is the FastAPI application. It makes the entry point available and offers a simple OpenAPI/Swagger docs to make this easy to access. This loosley follows a MCV design, where:
- 'web-api/app.py' calls the routes
- 'web-api/routes/routes/py' contains routes to CRUD
- 'web-api/curd/crud.py' handels read from db

## Justification

This design is chosen as a simple concept illustrating seperation of concerns and best practice. Each of the main components of the app are seperaterd:
- Airflow and web-api (FastAPI) have their own dir
- A '.env' file is used to handle env variables and avoid hard coding
- 'requirements.txt' ensures correct packages are used
- Within 'airflow/' the 'airflow/crud' folder is used do that code is not duplicated when used by the Python scripts initalilly populating the db and doing daily updates.
- SQL is seperated and called wherever possible for better organisation and clarity
- The 'web-api' part of the applpication follows a logical strucutre where routes and interaction with the db are spearte from the controller file

