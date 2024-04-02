from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()

password = os.getenv("PSQL_PASSWORD")
conn = psycopg2.connect(
    host="rc1b-xilltfvey34cs1tc.mdb.yandexcloud.net",
    database="notificator",
    user="notificator",
    password=password,
    port="6432"
)
