# File used to connect to the database
import mysql.connector

# Connect to MySQL Server
db = mysql.connector.connect(
    host="",
    user="",
    passwrd=""
)

# 
c = db.cursor()

db_name = ""

# Creates the database in the server if it does not exist
c.execute("IF DB_ID(%s) IS NULL BEGIN CREATE DATABASE %s END", db_name, db_name)


