"""
Starts the db and gets all info for the start page
"""
import os
import mysql.connector

def get_initial_data():
    # The .env variables should already be loaded from previously running the scripts/init_db.py file
    # Get the name of the database to be used
    db_name = os.getenv("db_name")

    # Connect to the Portfolio Tracker database
    db = mysql.connector.connect(
        host=os.getenv("db_host"),
        user=os.getenv("db_user"),
        password=os.getenv("db_password"),
        database=db_name
    )

    # Load all the data to be displayed in the main page of the portfolio tracker from the database
    cursor = db.cursor()
    cursor.execute("USE %s", db_name)
    cursor.execute("SELECT ___ FROM ___") # Loads Holdings
    holdings = cursor.fetchall()