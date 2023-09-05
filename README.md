# xkcd-pipeline design

These are the instructions for the design of the xkcd pipeline. The pipeline extracts XKCD metadata  on a daily basis it stores this to a db and makes this available via an API. 

This offers improved functionality compared to the current xkcd API (avialable at: https://xkcd.com/json.html). Improved functionality includes a OpenAPI/Swagger docs interface (pictured below) and the option to extract metadata for multiple comics at once. Note the current  xkcd is utilised in the pipeline for accessing data. In this design description first a high-level design is shown, followed by an overview of the project structure.

## Diagram

<div align="center">
  <img src="XKCD_Local-2.jpg" alt="XKCD Local">
</div>

The picture above shows the key components of the pipeline:

1. **xkcd API** - The API used to access xkcd metadata. This is a JSON interface.

2. **Airflow** - Airflow serves as the scheduler executing a Python dag which populates the db with the latest comic which is accessed with the curent comic interface (https://xkcd.com/info.0.json). It executes the dag on a daily basis. It uses a simple check to see if a comic with that id is present in the db and uses SQL INSERT to add to the db if not.

3. **Python** - The intial script to populate the db with comics from the past 180 days. It runs a simple extract to get the datetime of each comic:

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

4. **PostgreSQL** The PostgreSQL table. This is created with 'sql/initalise.sql'

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

5. **FastAPI** The FastAPI application. It makes the entry point available and offers a simple OpenAPI/Swagger docs to make this easy to access. This loosley follows a MCV design, where:
- 'web-api/app.py' calls the routes
- 'web-api/routes/routes/py' contains routes to CRUD
- 'web-api/curd/crud.py' handels read from db

6. **Docker** - A docker-compose.yml file is used to create containers for the different services. This includes multiple containers required for airflow (scheduler, db, tirgger etc.), a container for the PostgreSQL where details of the xkcd comics are stored and a contianer for  FastAPI. Note both FastAPI and Airflow have their own custom images allowing installing of python packages from requirements.txt files.


## Project Structure
```xkcd-pipeline/
├── README.md
├── docker-compose.yml
├── .env
├── airflow/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── config/
│   ├── crud/
│   │   ├── crud.py
│   │   └── crud.sql
│   ├── dags/
│   ├── logs/
│   └── plugins/
├── web-api/
│   ├── app.py    
│   ├── Dockerfile
│   ├── crud/
│   │   └── crud.py
│   └── routes/
│       └── routes.py
└── sql/
    └── initialise.sql
```


## Project Structure Explained

**xkcd-pipeline/**                  - Main project dir
- **README.md**                     - Documentation
- **docker-compose.yml**            - Compose Airflow, PostgreSQL and FastAPI
- **.env**            - Store env variables
- **airflow/**                      - Airflow dir
  - **Dockerfile**                  - Dockerfile for Airflow image
  - **requirements.txt**            - Python requirements for Airflow
  - **config/**                     - Configuration settings for Airflow
  - **crud/**                       - CRUD operations for Airflow 
    - **helpers.py**                   - Python CRUD functions (these call SQL)
    - **crud.sql**                  - SQL  CRUD operations
  - **dags/**                       - Directory for DAGs
  - **logs/**                       - Logs for Airflow tasks
  - **plugins/**                    - Custom plugins for Airflow
- **web-api/**                      - Web API (FastAPI)
  - **app.py**                      - Main FastAPI app setup
  - **Dockerfile**                  - Dockerfile for the web API service
  - **crud/**                       - CRUD operations for web API 
    - **crud.py**                   - Python CRUD operations (no SQL as use SQLAlchemy ORM)
  - **routes/**                     - Route definitions for the web API
    - **routes.py**                 - Python route definitions
- **sql/**                          - SQL start up db
  - **initialise.sql**              - SQL script to initialize comics db

## Design Justification

This design is chosen as a simple concept illustrating seperation of concerns and best practice. Each of the main components of the app are seperaterd:
- Airflow and web-api (FastAPI) have their own dir
- A '.env' file is used to handle env variables and avoid hard coding
- 'requirements.txt' ensures correct packages are used
- Within 'airflow/' the 'airflow/crud' folder is used do that code is not duplicated when used by the Python scripts initalilly populating the db and doing daily updates.
- SQL is seperated and called wherever possible for better organisation and clarity
- The 'web-api' part of the applpication follows a logical strucutre where routes and interaction with the db are spearte from the controller file

# xkcd-pipeline AWS design

This project can also be implemented in AWS. Below is a diagram showing how the project would be adapted and the AWS services used.

## Diagram

<div align="center">
  <img src="AWS_XKCD._dataflow-2.jpg" alt="AWS Dataflow">
</div>

The picture above shows the key components of the pipeline:

1. **xkcd API** - The API used to access xkcd metadata. This is a JSON interface (same as for local pipeline).

2. **MWAA (Managed Workflows for Apache Airflow)** - Manages Apache Airflow. Airflow executes a python dag which populates the db with the latest comic metadta accessed through the current comic interface (https://xkcd.com/info.0.json).

3. **S3** - Holds the actual dags and supporting Python files used by MWAA.

4. **RDS** - Hosts the PostgreSQL db where comic metadata is actually stored.

5. **EC2 (FastAPI)** - The (dockerised) server which hosts the FastAPI API which makes the data available through endpoint(s).

6. **VPC** - Used to create an internal network to host other services.

7. **SecretsManager** - Environment vatiables are securley stored here.

6. **IAM** - Manages both users and the roles assigned to services. 

6. **GitHub** - Used for version control of code.