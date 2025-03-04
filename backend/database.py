import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve database connection details from environment variables
DATABASE = os.getenv("DATABASE")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")

def get_connection():
    """
    Establishes and returns a connection to the PostgreSQL database.
    """
    try:
        connection = psycopg2.connect(
            database=DATABASE,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        )
        print("Connection to PostgreSQL database was successful!")
        return connection
    except Exception as e:
        print("Error connecting to the PostgreSQL database:", e)
        raise e

if __name__ == "__main__":
    # Test the database connection
    conn = get_connection()
    try:
        # Create a cursor with dictionary output
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print("PostgreSQL version:", db_version)
    finally:
        cursor.close()
        conn.close()
