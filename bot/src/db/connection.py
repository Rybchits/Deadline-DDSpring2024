from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()

HOST = "84.201.156.227"
DATABASE = "deadline-db"
USER = "admin"
PASSWORD = os.getenv("PSQL_PASSWORD")
PORT = "5432"

conn = psycopg2.connect(
    host=HOST,
    database=DATABASE,
    user=USER,
    password=PASSWORD,
    port=PORT
)

POOL = [None] # sets in application init
