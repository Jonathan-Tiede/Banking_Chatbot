import psycopg2
from config import load_config

"""
Connect to server using connection string as seen below:
conn = psycopg2.connect("dbname=suppliers user=YourUsername password=YourPassword")

Or by using keyword arguments:
conn = psycopg2.connect(
    host="localhost",
    database="suppliers",
    user="YourUsername",
    password="YourPassword"
)

"""
def connection(config):
    """ Connect to the PostgreSQL database server """
    try:
        # with psycopg2.connect(**config) as conn:
        #     print('Connected to the PostgreSQL server.')
        #     return conn
        conn = psycopg2.connect(**config)
        return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

if __name__ == '__main__':
    config = load_config()
    connection(config)

def connection(config):
    try:
        conn = psycopg2.connect(**config)
        return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)