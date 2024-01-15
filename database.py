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

def get_item_by_name(name):
    conn = connect()
    cursor = conn.cursor()
    sql = ("SELECT * FROM leads where last_name = %s")
    cursor.execute(sql, (name,))
    result = cursor.fetchone()
    conn.close()
    if result is None:
        return ""
    else:
        #print(result)
        return result[0]

def get_all_active_user():
    conn = connect()
    cursor = conn.cursor()
    sql = ("SELECT * FROM users where status = %s")

def find_minimum_leads_by_sale():
    conn = connect()
    cursor = conn.cursor()
    sql = ("select * from suitecrm.users where employee_status = 'Active' and department = 'Sales Dept.' and id != '6d14a07c-f8d3-d21a-f31c-6592da7f6c30';")
    cursor.execute(sql,())
    results = cursor.fetchall()
    first_result = results[0]
    
    selected_user_id = results[0][0]
    check_sql = ("select count(*) from leads where assigned_user_id = %s")
    cursor.execute(check_sql,(selected_user_id,))
    _min_count = cursor.fetchone()
    min_count = _min_count[0]

    for result in results:
        user_id = result[0]
        #print(user_id)
        check_sql = ("select count(*) from leads where assigned_user_id = %s")
        cursor.execute(check_sql,(user_id,))
        final_count = cursor.fetchone()
        #print(final_count[0])
        if (final_count[0] <= min_count):
            selected_user_id = user_id
            min_count = final_count[0]
        else:
            continue
    #print("Selected user id:" + selected_user_id)
    return selected_user_id
