import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Preferred for managed providers (including Supabase)
DATABASE_URL = os.getenv("DATABASE_URL")

# Backward-compatible discrete connection fields
DB_NAME = os.getenv("DB_NAME") or os.getenv("DATABASE")
DB_USER = os.getenv("DB_USER") or os.getenv("USER")
DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("PASSWORD")
DB_HOST = os.getenv("DB_HOST") or os.getenv("HOST")
DB_PORT = os.getenv("DB_PORT") or os.getenv("PORT")
DB_SSLMODE = os.getenv("DB_SSLMODE")

def get_connection():
    """
    Establishes and returns a connection to the PostgreSQL database.
    """
    try:
        if DATABASE_URL:
            if DB_SSLMODE:
                connection = psycopg2.connect(DATABASE_URL, sslmode=DB_SSLMODE)
            else:
                connection = psycopg2.connect(DATABASE_URL)
        else:
            connect_kwargs = {
                "database": DB_NAME,
                "user": DB_USER,
                "password": DB_PASSWORD,
                "host": DB_HOST,
                "port": DB_PORT,
            }
            if DB_SSLMODE:
                connect_kwargs["sslmode"] = DB_SSLMODE
            connection = psycopg2.connect(**connect_kwargs)

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
