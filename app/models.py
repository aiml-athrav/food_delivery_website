import mysql.connector
from app import app

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            database=app.config['DB_NAME'],
            port=app.config['DB_PORT']
        )
        return connection
    except mysql.connector.Error as err:
        print(f"MySQL connection error: {err}")
        return None


def initialize_database():
    connection = get_db_connection()

    if connection is None:
        print("Database connection failed")
        return

    cursor = connection.cursor()

    # read schema.sql
    with open('database/schema.sql', 'r') as f:
        sql_commands = f.read()

    # execute each statement
    for command in sql_commands.split(';'):
        if command.strip():
            cursor.execute(command)

    connection.commit()
    cursor.close()
    connection.close()

    print("Database tables checked/created successfully")