import mysql.connector
from mysql.connector import Error

def create_connection():
    """Create a connection to the database"""
    try:
        # Define your database connection parameters
        connection = mysql.connector.connect(
            host='vidurindia.cbkgp37sk7e2.ap-south-1.rds.amazonaws.com',  # Change this to your database server
            user='banku',  # Your database username
            password='BankuInverted1994',  # Your database password
            database='kunalTesting'  # The database name you want to connect to
        )
        if connection.is_connected():
            print("Connected to the database")
            return connection
        else:
            print("Failed to connect to the database")
            return None
    except Error as e:
        print(f"Error: {e}")
        return None

def close_connection(connection):
    """Close the database connection"""
    try:
        if connection.is_connected():
            connection.close()
            print("Connection closed")
    except Error as e:
        print(f"Error: {e}")
    