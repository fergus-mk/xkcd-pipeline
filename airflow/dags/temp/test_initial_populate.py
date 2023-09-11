import os
import psycopg2

def connect_to_db():
    # Fetch environment variables
    host = "localhost"
    dbname = "comicdb"
    user = "myuser"
    password = "mypassword"
    port = "5432"

    # Print the connection details (for debugging purposes)
    print(f"Host: {host}")
    print(f"DB Name: {dbname}")
    print(f"User: {user}")
    print(f"Password: {password}")
    print(f"Port: {port}")

    try:
        # Attempt to connect to the database
        connection = psycopg2.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password,
            port=port
        )
        print("Successfully connected to the database!")
        connection.close()
    except Exception as e:
        print(f"Failed to connect to the database. Error: {e}")

if __name__ == "__main__":
    connect_to_db()
