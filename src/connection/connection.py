import psycopg2
import configparser

def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database using config settings.
    
    Returns:
        conn: A PostgreSQL database connection.
    """
    try:
        # Read database credentials from config.ini
        config = configparser.ConfigParser()
        config.read("/usr/local/chatbot/src/config.ini")

        conn = psycopg2.connect(
            dbname=config["postgres"]["dbname"],
            user=config["postgres"]["user"],
            password=config["postgres"]["password"],
            host=config["postgres"]["host"],
            port=config["postgres"]["port"]
        )
        return conn

    except Exception as e:
        print(f"❌ Error connecting to the database: {e}")
        return None
