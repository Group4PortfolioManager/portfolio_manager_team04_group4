"""
Starts the db and gets all info for the start page
These functions will be executed in main.py
"""
import os
from dotenv import load_dotenv
import mysql.connector

# Load environment variables
load_dotenv()
# The .env variables should already be loaded from previously running the scripts/init_db.py file
# Get the name of the database to be used
db_name = os.getenv("db_name")
    
def get_db_connection(): 
    # Connect to the Portfolio Tracker database
    db = mysql.connector.connect(
        host=os.getenv("db_host"),
        user=os.getenv("db_user"),
        password=os.getenv("db_password"),
        database=db_name
    )

    return db

def get_portfolios(db):
    # Load all the portfolios in the database
    p_cursor = db.cursor(dictionary=True)
    p_cursor.execute("SELECT * FROM Portfolio;")
    portfolios = p_cursor.fetchall()
    p_cursor.close()
    return portfolios # TODO: IF MORE THAN 1 PORTFOLIO ASK USER TO SELECT PORTFOLIO
    
def get_initial_data(db, portfolio): # Load all the data to be displayed in the main page of the portfolio tracker from the database
    a_cursor = db.cursor()
    h_cursor = db.cursor()
    
    # Creates a portfolio if none exist
    if not portfolio:
        p_cursor = db.cursor(dictionary=True)
        p_cursor.execute("INSERT INTO portfolio (portfolio_id, portfolio_name, cash_balance, created_at) VALUES (1, 'New Portfolio', 0, NOW());")
        db.commit()
        p_cursor.execute("SELECT * FROM Portfolio;")
        portfolio = p_cursor.fetchall()[0]
        print(f"Portfolio Created: {portfolio}")
    
    # Load all assets
    a_cursor.execute("SELECT * FROM Asset;") # Loads Assets
    assets = a_cursor.fetchall()
    
    # Load holdings related to a specific portfolio
    portfolio_id = portfolio['portfolio_id']
    h_cursor.execute("SELECT * FROM Holdings WHERE portfolio_id = %s;", (portfolio_id,)) # Loads Holdings Related to Specific Portfolio
    holdings = h_cursor.fetchall()

    a_cursor.close()
    h_cursor.close()
    
    return assets, holdings