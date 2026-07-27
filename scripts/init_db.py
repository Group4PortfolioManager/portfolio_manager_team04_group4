"""
File used to connect to the database
"""

import mysql.connector
import os
from dotenv import load_dotev

def start_database():
    # Load environment variables
    load_dotev()

    # Connect to MySQL Server
    db = mysql.connector.connect(
        host=os.getenv("db_host"),
        user=os.getenv("db_user"),
        password=os.getenv("db_password")
        #database=os.getenv("db_name"), # assume that database might not be created
    )

    # Get the name of the database to be created
    db_name = os.getenv("db_name")

    # Checks if database already exists in the system
    cursor = db.cursor()
    #cursor.execute("CREATE DATABASE IF NOT EXIST %s", db_name)
    cursor.execute("SHOW DATABASES LIKE '%s';", (db_name,))

    # Creates the database in the server if it does not exist
    if cursor.rowcount <= 0:    
        with open("../app/database/schema.sql") as file:
            script = file.read()
        cursor.execute(script, multi=True)
        results = cursor.fetchall()
        for line in results:
            print(line)


