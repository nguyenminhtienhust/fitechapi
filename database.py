
import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")

# Connect to MySQL
def connect():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )

def check_leads_name(name):
    conn = connect()
    cursor = conn.cursor()
    sql = ("SELECT * FROM leads where last_name = %s")
    cursor.execute(sql, (name,))
    result = cursor.fetchall()
    conn.close()
    return len(result) > 0

