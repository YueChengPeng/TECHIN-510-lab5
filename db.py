import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


db_user = os.getenv('POSTGRESQLCONNSTR_DB_USER')
db_pw = os.getenv('POSTGRESQLCONNSTR_DB_PASSWORD')
db_host = os.getenv('POSTGRESQLCONNSTR_DB_HOST')
db_port = os.getenv('POSTGRESQLCONNSTR_DB_PORT')
db_name = os.getenv('POSTGRESQLCONNSTR_DB_NAME')

conn_str = f'postgresql://{db_user}:{db_pw}@{db_host}:{db_port}/{db_name}'
print(conn_str)

def get_db_conn():
    conn = psycopg2.connect(conn_str)
    conn.autocommit = True
    return conn

# get_db_conn()