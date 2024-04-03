from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()

password = os.getenv("PSQL_PASSWORD")
conn = psycopg2.connect(
    host="178.154.202.11",
    database="deadline-db",
    user="admin",
    password=password,
    port="5432"
)
