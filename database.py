import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone
import calendar
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

# def connect():
# 	return mysql.connector.connect(
# 		host='localhost',
# 		user='root',
# 		password='tranha1111',
# 		database='suitecrm'
# 	)

def export_all_leads_in_Malaysia():
	conn = connect()
	cursor = conn.cursor()
	sql = ("select * from suitecrm.leads where primary_address_country LIKE 'Malaysia' or primary_address_country LIKE 'Kuala Lumpur' or primary_address_country LIKE 'Penang' or primary_address_street LIKE 'Malaysia' or primary_address_street LIKE 'Kuala Lumpur' or primary_address_street LIKE 'Penang'")
	cursor.execute(sql, ())
	result = cursor.fetchall()
	conn.close()
	if result is None:
		return ""
	else:
		#print(result )
		return result

def get_leads_today():
	today = datetime.today().date()
	today_string = today.strftime('%Y-%m-%d')

	yesterday = today - timedelta(days=1)
	yesterday_string = yesterday.strftime('%Y-%m-%d')

	tomorow = today + timedelta(days=1)
	tomorow_string = tomorow.strftime('%Y-%m-%d')

	conn = connect()
	cursor = conn.cursor(dictionary=True)
	today_sql = ("select * from suitecrm.leads where date_entered> %s and date_entered < %s")                                                                                                                                                             
	cursor.execute(today_sql,(yesterday_string,tomorow_string))                                                                                                                                                               
	results_today = cursor.fetchall()                                                                                                                                                
	conn.close()
	return {"data": results_today}

def get_leads_yesterday():
	today = datetime.today().date()
	today_string = today.strftime('%Y-%m-%d')

	yesterday = today - timedelta(days=2)
	yesterday_string = yesterday.strftime('%Y-%m-%d')

	conn = connect()
	cursor = conn.cursor(dictionary=True)
	today_sql = ("select * from suitecrm.leads where date_entered> %s and date_entered < %s")                                                                                                                                                             
	cursor.execute(today_sql,(yesterday_string,today_string))                                                                                                                                                               
	results_today = cursor.fetchall()                                                                                                                                                
	conn.close()
	return {"data": results_today}

def get_item_by_name(title, account, contact):
	conn = connect()
	cursor = conn.cursor()
	sql = ("SELECT * FROM suitecrm.leads where title = %s and last_name = %s and first_name = %s and Deleted = 0")
	if(contact == ""):
		sql = ("SELECT * FROM suitecrm.leads where title = %s and last_name = %s and (first_name = %s or first_name is Null) and Deleted = 0")
	cursor.execute(sql, (title,account, contact))
	result = cursor.fetchone()
	conn.close()
	if result is None:
		return ""
	else:
		#print(result)
		return result

def get_active_sales():
	conn = connect()
	cursor = conn.cursor(dictionary=True)
	sql = ("select * from suitecrm.users where status = 'Active' and id != '6d14a07c-f8d3-d21a-f31c-6592da7f6c30' and is_admin = 'False';")
	cursor.execute(sql,())
	results = cursor.fetchall()
	cursor.close()
	return {"data":results}

def assign_sale_with_lead(user_id,lead_id):
	conn = connect()
	cursor = conn.cursor()
	sql = ("update suitecrm.leads set assigned_user_id = %s where id = %s")
	cursor.execute(sql,(user_id,lead_id))
	cursor.close()
	conn.commit()
	return True


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

def get_all_dashboard():
	conn = connect()
	cursor = conn.cursor()
	sql = ("select * from suitecrm.users where status = 'Active' and id != '6d14a07c-f8d3-d21a-f31c-6592da7f6c30' and is_admin = 'False';")
	cursor.execute(sql,())
	sales = cursor.fetchall()
	sales_list = []
	for sale in sales:
		full_name = sale[8] + " " + sale[7]
		detail_dict = {"full_name":full_name}

		total_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and deleted = 0 ")
		cursor.execute(total_sql,(sale[0],))                                                                                                                                                               
		results_total = cursor.fetchone()                                                                                                                                                   
		detail_dict["total_leads"] = results_total[0]

		new_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'New' and deleted = 0")
		cursor.execute(new_sql,(sale[0],))
		results_new = cursor.fetchone()
		detail_dict["total_new"] = results_new[0]

		assigned_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Assigned' and deleted = 0")
		cursor.execute(assigned_sql,(sale[0],))
		results_assigned = cursor.fetchone()
		detail_dict["total_assigned"] = results_assigned[0]
		
		inprocess_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'In Process' and deleted = 0")
		cursor.execute(inprocess_sql,(sale[0],))
		results_inprocess = cursor.fetchone()
		detail_dict["total_inprocess"] = results_inprocess[0]
		
		converted_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Converted' and deleted = 0")
		cursor.execute(converted_sql,(sale[0],))
		results_converted = cursor.fetchone()
		detail_dict["total_converted"] = results_converted[0]
		
		recycled_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Recycled' and deleted = 0")
		cursor.execute(recycled_sql,(sale[0],))
		results_recycled = cursor.fetchone()
		detail_dict["total_recycled"] = results_recycled[0]
		
		dead_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Dead' and deleted = 0")
		cursor.execute(dead_sql,(sale[0],))
		results_dead = cursor.fetchone()
		detail_dict["total_dead"] = results_dead[0]
		
		sales_list.append(detail_dict)
	final_dict = {"sales": sales_list}

	sumary_sql = ("select count(*) from suitecrm.leads where deleted = 0")
	cursor.execute(sumary_sql,())
	total_leads_result = cursor.fetchone()
	final_dict["total_leads"] = total_leads_result[0]

	supersale_sql = ("select count(*) from suitecrm.leads where created_by = '6d14a07c-f8d3-d21a-f31c-6592da7f6c30' and deleted = 0")
	cursor.execute(supersale_sql,())
	total_leads_by_supersale = cursor.fetchone()
	final_dict["total_leads_by_supersale"] = total_leads_by_supersale[0]
 
	# dttoday_str = datetime.today().strftime('%Y-%m-%d')
	# dttoday = datetime.fromisoformat(dttoday_str)
	# dtTo = dttoday + timedelta(1)
	# # ...and to UTC:
	# dtTodayUtc = dttoday.astimezone(timezone.utc)
	# dtToUtc = dtTo.astimezone(timezone.utc) - timedelta(seconds=1)
	# dtTodayUtc_str = dtTodayUtc.strftime("%Y-%m-%d %H:%M:%S")
	# dtToUtc_str = dtToUtc.strftime("%Y-%m-%d %H:%M:%S")
	# leadbyday_sql = ("select count(*) from suitecrm.leads where created_by = '6d14a07c-f8d3-d21a-f31c-6592da7f6c30' and deleted = 0 and date_entered >= %s and date_entered <= %s")
	# cursor.execute(leadbyday_sql, (dtTodayUtc_str, dtToUtc_str,))
	# total_by_day_supersale = cursor.fetchone()
	# final_dict["total_by_day_supersale"] = total_by_day_supersale[0]

	admin_sql = ("select count(*) from suitecrm.leads where created_by = '1' and deleted = 0")
	cursor.execute(admin_sql,())
	total_leads_by_admin = cursor.fetchone()
	final_dict["total_leads_by_admin"] = total_leads_by_admin[0]

	new_sql = ("select count(*) from suitecrm.leads where status = 'New' and deleted = 0")
	cursor.execute(new_sql,())
	results_new = cursor.fetchone()
	final_dict["total_new_leads"] = results_new[0]

	assigned_sql = ("select count(*) from suitecrm.leads where status = 'Assigned' and deleted = 0")
	cursor.execute(assigned_sql,())
	results_assigned = cursor.fetchone()
	final_dict["total_assigned"] = results_assigned[0]
		
	inprocess_sql = ("select count(*) from suitecrm.leads where status = 'In Process' and deleted = 0")
	cursor.execute(inprocess_sql,())
	results_inprocess = cursor.fetchone()
	final_dict["total_inprocess"] = results_inprocess[0]
		
	converted_sql = ("select count(*) from suitecrm.leads where status = 'Converted' and deleted = 0")
	cursor.execute(converted_sql,())
	results_converted = cursor.fetchone()
	final_dict["total_converted"] = results_converted[0]
		
	recycled_sql = ("select count(*) from suitecrm.leads where status = 'Recycled' and deleted = 0")
	cursor.execute(recycled_sql,())
	results_recycled = cursor.fetchone()
	final_dict["total_recycled"] = results_recycled[0]
	
	dead_sql = ("select count(*) from suitecrm.leads where status = 'Dead' and deleted = 0")
	cursor.execute(dead_sql,())
	results_dead = cursor.fetchone()
	final_dict["total_dead"] = results_dead[0]

	return {"data":final_dict}

def get_this_month_dashboard():
	input_dt = datetime.today().date()
	day_num = input_dt.strftime("%d")
	first_date = input_dt - timedelta(days=int(day_num) - 1)
	first_date_string = first_date.strftime('%Y-%m-%d')
	
	current_year = first_date.year
	current_month = first_date.month
	number_day_per_month = calendar.monthrange(current_year, current_month)
	last_date = first_date.replace(day=number_day_per_month[1])
	last_date_string = last_date.strftime('%Y-%m-%d')
	
	conn = connect()
	cursor = conn.cursor()
	sql = ("select * from suitecrm.users where status = 'Active' and id != '6d14a07c-f8d3-d21a-f31c-6592da7f6c30' and is_admin = 'False';")
	cursor.execute(sql,())
	sales = cursor.fetchall()
	sales_list = []
	for sale in sales:
		full_name = sale[8] + " " + sale[7]
		detail_dict = {"full_name":full_name}

		total_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and date_modified >= %s and date_modified <= %s")
		cursor.execute(total_sql,(sale[0],first_date_string,last_date_string))                                                                                                                                                               
		results_total = cursor.fetchone()                                                                                                                                                   
		detail_dict["total_leads"] = results_total[0]

		new_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'New' and date_modified >= %s and date_modified <= %s")
		cursor.execute(new_sql,(sale[0],first_date_string,last_date_string))
		results_new = cursor.fetchone()
		detail_dict["total_new"] = results_new[0]

		assigned_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Assigned' and date_modified >= %s and date_modified <= %s")
		cursor.execute(assigned_sql,(sale[0],first_date_string,last_date_string))
		results_assigned = cursor.fetchone()
		detail_dict["total_assigned"] = results_assigned[0]
		
		inprocess_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'In Process' and date_modified >= %s and date_modified <= %s")
		cursor.execute(inprocess_sql,(sale[0],first_date_string,last_date_string))
		results_inprocess = cursor.fetchone()
		detail_dict["total_inprocess"] = results_inprocess[0]
		
		converted_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Converted' and date_modified >= %s and date_modified <= %s")
		cursor.execute(converted_sql,(sale[0],first_date_string,last_date_string))
		results_converted = cursor.fetchone()
		detail_dict["total_converted"] = results_converted[0]
		
		recycled_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Recycled' and date_modified >= %s and date_modified <= %s")
		cursor.execute(recycled_sql,(sale[0],first_date_string,last_date_string))
		results_recycled = cursor.fetchone()
		detail_dict["total_recycled"] = results_recycled[0]
		
		dead_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Dead' and date_modified >= %s and date_modified <= %s")
		cursor.execute(dead_sql,(sale[0],first_date_string,last_date_string))
		results_dead = cursor.fetchone()
		detail_dict["total_dead"] = results_dead[0]
		
		sales_list.append(detail_dict)
	final_dict = {"sales": sales_list}
	print(final_dict)
	sumary_sql = ("select count(*) from suitecrm.leads where date_modified >= %s and date_modified <= %s")
	cursor.execute(sumary_sql,(first_date_string,last_date_string))
	total_leads_result = cursor.fetchone()
	final_dict["total_leads"] = total_leads_result[0]

	supersale_sql = ("select count(*) from suitecrm.leads where created_by = '6d14a07c-f8d3-d21a-f31c-6592da7f6c30' and date_modified >= %s and date_modified <= %s")
	cursor.execute(supersale_sql,(first_date_string,last_date_string,))
	total_leads_by_supersale = cursor.fetchone()
	final_dict["total_leads_by_supersale"] = total_leads_by_supersale[0]

	admin_sql = ("select count(*) from suitecrm.leads where created_by = '1' and date_modified >= %s and date_modified <= %s")
	cursor.execute(admin_sql,(first_date_string,last_date_string))
	total_leads_by_admin = cursor.fetchone()
	final_dict["total_leads_by_admin"] = total_leads_by_admin[0]

	new_sql = ("select count(*) from suitecrm.leads where status = 'New' and date_modified >= %s and date_modified <= %s")
	cursor.execute(new_sql,(first_date_string,last_date_string))
	results_new = cursor.fetchone()
	final_dict["total_new_leads"] = results_new[0]

	assigned_sql = ("select count(*) from suitecrm.leads where status = 'Assigned' and date_modified >= %s and date_modified <= %s")
	cursor.execute(assigned_sql,(first_date_string,last_date_string))
	results_assigned = cursor.fetchone()
	final_dict["total_assigned"] = results_assigned[0]
		
	inprocess_sql = ("select count(*) from suitecrm.leads where status = 'In Process' and date_modified >= %s and date_modified <= %s")
	cursor.execute(inprocess_sql,(first_date_string,last_date_string))
	results_inprocess = cursor.fetchone()
	final_dict["total_inprocess"] = results_inprocess[0]
		
	converted_sql = ("select count(*) from suitecrm.leads where status = 'Converted' and date_modified >= %s and date_modified <= %s")
	cursor.execute(converted_sql,(first_date_string,last_date_string))
	results_converted = cursor.fetchone()
	final_dict["total_converted"] = results_converted[0]
		
	recycled_sql = ("select count(*) from suitecrm.leads where status = 'Recycled' and date_modified >= %s and date_modified <= %s")
	cursor.execute(recycled_sql,(first_date_string,last_date_string))
	results_recycled = cursor.fetchone()
	final_dict["total_recycled"] = results_recycled[0]
	
	dead_sql = ("select count(*) from suitecrm.leads where status = 'Dead' and date_modified >= %s and date_modified <= %s")
	cursor.execute(dead_sql,(first_date_string,last_date_string))
	results_dead = cursor.fetchone()
	final_dict["total_dead"] = results_dead[0]

	return {"data":final_dict}

def get_today_dashboard():
	conn = connect()
	cursor = conn.cursor()
	sql = ("select * from suitecrm.users where status = 'Active' and id != '6d14a07c-f8d3-d21a-f31c-6592da7f6c30' and is_admin = 'False';")
	cursor.execute(sql,())
	sales = cursor.fetchall()
	sales_list = []
	for sale in sales:
		full_name = sale[8] + " " + sale[7]
		detail_dict = {"full_name":full_name}

		total_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s")
		cursor.execute(total_sql,(sale[0],))                                                                                                                                                               
		results_total = cursor.fetchone()                                                                                                                                                   
		detail_dict["total_leads"] = results_total[0]

		new_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'New'")
		cursor.execute(new_sql,(sale[0],))
		results_new = cursor.fetchone()
		detail_dict["total_new"] = results_new[0]

		assigned_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Assigned'")
		cursor.execute(assigned_sql,(sale[0],))
		results_assigned = cursor.fetchone()
		detail_dict["total_assigned"] = results_assigned[0]
		
		inprocess_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'In Process'")
		cursor.execute(inprocess_sql,(sale[0],))
		results_inprocess = cursor.fetchone()
		detail_dict["total_inprocess"] = results_inprocess[0]
		
		converted_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Converted'")
		cursor.execute(converted_sql,(sale[0],))
		results_converted = cursor.fetchone()
		detail_dict["total_converted"] = results_converted[0]
		
		recycled_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Recycled'")
		cursor.execute(recycled_sql,(sale[0],))
		results_recycled = cursor.fetchone()
		detail_dict["total_recycled"] = results_recycled[0]
		
		dead_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Dead'")
		cursor.execute(dead_sql,(sale[0],))
		results_dead = cursor.fetchone()
		detail_dict["total_dead"] = results_dead[0]
		
		sales_list.append(detail_dict)
	final_dict = {"sales": sales_list}

	sumary_sql = ("select count(*) from suitecrm.leads")
	cursor.execute(sumary_sql,())
	total_leads_result = cursor.fetchone()
	final_dict["total_leads"] = total_leads_result[0]

	supersale_sql = ("select count(*) from suitecrm.leads where created_by = '6d14a07c-f8d3-d21a-f31c-6592da7f6c30'")
	cursor.execute(supersale_sql,())
	total_leads_by_supersale = cursor.fetchone()
	final_dict["total_leads_by_supersale"] = total_leads_by_supersale[0]

	admin_sql = ("select count(*) from suitecrm.leads where created_by = '1'")
	cursor.execute(admin_sql,())
	total_leads_by_admin = cursor.fetchone()
	final_dict["total_leads_by_admin"] = total_leads_by_admin[0]

	new_sql = ("select count(*) from suitecrm.leads where status = 'New'")
	cursor.execute(new_sql,())
	results_new = cursor.fetchone()
	final_dict["total_new_leads"] = results_new[0]

	assigned_sql = ("select count(*) from suitecrm.leads where status = 'Assigned'")
	cursor.execute(assigned_sql,())
	results_assigned = cursor.fetchone()
	final_dict["total_assigned"] = results_assigned[0]
		
	inprocess_sql = ("select count(*) from suitecrm.leads where status = 'In Process'")
	cursor.execute(inprocess_sql,())
	results_inprocess = cursor.fetchone()
	final_dict["total_inprocess"] = results_inprocess[0]
		
	converted_sql = ("select count(*) from suitecrm.leads where status = 'Converted'")
	cursor.execute(converted_sql,())
	results_converted = cursor.fetchone()
	final_dict["total_converted"] = results_converted[0]
		
	recycled_sql = ("select count(*) from suitecrm.leads where status = 'Recycled'")
	cursor.execute(recycled_sql,())
	results_recycled = cursor.fetchone()
	final_dict["total_recycled"] = results_recycled[0]
	
	dead_sql = ("select count(*) from suitecrm.leads where status = 'Dead'")
	cursor.execute(dead_sql,())
	results_dead = cursor.fetchone()
	final_dict["total_dead"] = results_dead[0]

	return {"data":final_dict}
	
def get_account_by_name(name):
	conn = connect()
	cursor = conn.cursor()
	sql = ("SELECT * FROM suitecrm.accounts where name = %s")
	cursor.execute(sql, (name,))
	result = cursor.fetchone()
	conn.close()
	if result is None:
		return ""
	else:
		return result
		
def check_exist_email(name):
	conn = connect()
	cursor = conn.cursor()
	sql = ("SELECT * FROM suitecrm.email_addresses where email_address_caps = %s")
	cursor.execute(sql, (name,))
	result = cursor.fetchone()
	conn.close()
	if result is None:
		return ""
	else:
		return result[0]
		
def check_email_lead(lead_id):
	conn = connect()
	cursor = conn.cursor()
	email_list = []
	sql = ("SELECT email_address FROM suitecrm.email_addresses where id in (select email_address_id from suitecrm.email_addr_bean_rel where bean_id = %s)")
	cursor.execute(sql,(lead_id,))
	emails = cursor.fetchall()
	conn.close()
	for email in emails:
		email_list.append(email[0])
	return {"email_list" : email_list}

def add_email_addressed(id, email, email_cap):
	conn = connect()
	cursor = conn.cursor()
	sql = ("insert into suitecrm.email_addresses (id, email_address, email_address_caps) values (%s, %s, %s)")
	cursor.execute(sql, (id, email, email_cap,))
	conn.commit()
	result = cursor.rowcount
	conn.close()
	return result

def get_contact_by_name(name):
	conn = connect()
	cursor = conn.cursor()
	sql = ("SELECT * FROM suitecrm.contacts where last_name = %s and created_by = '1'")
	cursor.execute(sql, (name,))
	result = cursor.fetchone()	
	conn.close()
	if result is None:
		return ""
	else:
		return result
	#if result is None:
		#return ""
	#else:
		#return result[0]

def get_contact_assigned_user(name):
	conn = connect()
	cursor = conn.cursor()
	sql = ("SELECT assigned_user_id FROM suitecrm.contacts where id = %s")
	cursor.execute(sql, (name,))
	result = cursor.fetchone()
	conn.close()
	#return name
	if result is None:
		return ""
	else:
		return result[0]

def get_account_assigned_user(name):
	conn = connect()
	cursor = conn.cursor()
	sql = ("SELECT assigned_user_id FROM suitecrm.accounts where id = %s")
	cursor.execute(sql, (name,))
	result = cursor.fetchone()
	conn.close()
	#return name
	if result is None:
		return ""
	else:
		return result[0]

def get_lead_assigned_user_by_contact(name):
	conn = connect()
	cursor = conn.cursor()
	sql = ("SELECT assigned_user_id FROM suitecrm.leads where first_name = %s and assigned_user_id is not null and assigned_user_id <> '' and assigned_user_id <> 'd6ea87ac-8c7e-a4ed-ba81-65f500a98e58' ")
	cursor.execute(sql, (name,))
	result = cursor.fetchone()
	conn.close()
	if result is None:
		return ""
	else:
		return result

def get_lead_assigned_user_by_account(name):
	conn = connect()
	cursor = conn.cursor()
	sql = ("SELECT assigned_user_id FROM suitecrm.leads where last_name = %s and assigned_user_id is not null and assigned_user_id <> '' and assigned_user_id <> 'd6ea87ac-8c7e-a4ed-ba81-65f500a98e58'")
	cursor.execute(sql, (name,))
	result = cursor.fetchone()
	conn.close()
	if result is None:
		return ""
	else:
		return result

def get_lead_count(date_from, date_to,sale_id):
	#datetime_object = datetime.strptime(date_from, '%m/%d/%y %H:%M:%S')
	conn = connect()
	cursor = conn.cursor()
	sql = ("SELECT count(*) FROM suitecrm.leads where created_by = %s and date_entered >= %s and date_entered <= %s")
	cursor.execute(sql, (sale_id,date_from, date_to,))
	result = cursor.fetchone()
	conn.close()
	if result is None:
		return ""
	else:
		return result[0]


def get_all_dashboard_by_date(date_from, date_to):
	conn = connect()
	cursor = conn.cursor()
	sql = ("select * from suitecrm.users where status = 'Active' and id != '6d14a07c-f8d3-d21a-f31c-6592da7f6c30' and is_admin = 'False';")
	cursor.execute(sql,())
	sales = cursor.fetchall()
	sales_list = []
	for sale in sales:
		full_name = sale[8] + " " + sale[7]
		detail_dict = {"full_name":full_name}

		total_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and deleted = 0 and date_entered >= %s and date_entered <= %s")
		cursor.execute(total_sql,(sale[0],date_from,date_to,))                                                                                                                                                               
		results_total = cursor.fetchone()                                                                                                                                                   
		detail_dict["total_leads"] = results_total[0]

		new_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'New' and deleted = 0 and date_entered >= %s and date_entered <= %s" )
		cursor.execute(new_sql,(sale[0],date_from, date_to,))
		results_new = cursor.fetchone()
		detail_dict["total_new"] = results_new[0]

		assigned_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Assigned' and deleted = 0 and date_entered >= %s and date_entered <= %s")
		cursor.execute(assigned_sql,(sale[0],date_from, date_to,))
		results_assigned = cursor.fetchone()
		detail_dict["total_assigned"] = results_assigned[0]
		
		inprocess_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'In Process' and deleted = 0 and date_entered >= %s and date_entered <= %s")
		cursor.execute(inprocess_sql,(sale[0],date_from, date_to,))
		results_inprocess = cursor.fetchone()
		detail_dict["total_inprocess"] = results_inprocess[0]
		
		converted_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Converted' and deleted = 0 and date_entered >= %s and date_entered <= %s")
		cursor.execute(converted_sql,(sale[0],date_from, date_to,))
		results_converted = cursor.fetchone()
		detail_dict["total_converted"] = results_converted[0]
		
		recycled_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Recycled' and deleted = 0 and date_entered >= %s and date_entered <= %s")
		cursor.execute(recycled_sql,(sale[0],date_from, date_to,))
		results_recycled = cursor.fetchone()
		detail_dict["total_recycled"] = results_recycled[0]
		
		dead_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Dead' and deleted = 0 and date_entered >= %s and date_entered <= %s")
		cursor.execute(dead_sql,(sale[0],date_from, date_to))
		results_dead = cursor.fetchone()
		detail_dict["total_dead"] = results_dead[0]
		
		sales_list.append(detail_dict)
	final_dict = {"sales": sales_list}

	sumary_sql = ("select count(*) from suitecrm.leads where deleted = 0 and date_entered >= %s and date_entered <= %s")
	cursor.execute(sumary_sql,(date_from, date_to,))
	total_leads_result = cursor.fetchone()
	final_dict["total_leads"] = total_leads_result[0]

	supersale_sql = ("select count(*) from suitecrm.leads where created_by = '6d14a07c-f8d3-d21a-f31c-6592da7f6c30' and deleted = 0 and date_entered >= %s and date_entered <= %s")
	cursor.execute(supersale_sql,(date_from, date_to))
	total_leads_by_supersale = cursor.fetchone()
	final_dict["total_leads_by_supersale"] = total_leads_by_supersale[0]
 
	# dttoday_str = datetime.today().strftime('%Y-%m-%d')
	# dttoday = datetime.fromisoformat(dttoday_str)
	# dtTo = dttoday + timedelta(1)
	# # ...and to UTC:
	# dtTodayUtc = dttoday.astimezone(timezone.utc)
	# dtToUtc = dtTo.astimezone(timezone.utc) - timedelta(seconds=1)
	# dtTodayUtc_str = dtTodayUtc.strftime("%Y-%m-%d %H:%M:%S")
	# dtToUtc_str = dtToUtc.strftime("%Y-%m-%d %H:%M:%S")
	# leadbyday_sql = ("select count(*) from suitecrm.leads where created_by = '6d14a07c-f8d3-d21a-f31c-6592da7f6c30' and deleted = 0 and date_entered >= %s and date_entered <= %s")
	# cursor.execute(leadbyday_sql, (dtTodayUtc_str, dtToUtc_str,))
	# total_by_day_supersale = cursor.fetchone()
	# final_dict["total_by_day_supersale"] = total_by_day_supersale[0]

	admin_sql = ("select count(*) from suitecrm.leads where created_by = '1' and deleted = 0 and date_entered >= %s and date_entered <= %s")
	cursor.execute(admin_sql,(date_from, date_to))
	total_leads_by_admin = cursor.fetchone()
	final_dict["total_leads_by_admin"] = total_leads_by_admin[0]

	new_sql = ("select count(*) from suitecrm.leads where status = 'New' and deleted = 0 and date_entered >= %s and date_entered <= %s")
	cursor.execute(new_sql,(date_from, date_to))
	results_new = cursor.fetchone()
	final_dict["total_new_leads"] = results_new[0]

	assigned_sql = ("select count(*) from suitecrm.leads where status = 'Assigned' and deleted = 0 and date_entered >= %s and date_entered <= %s")
	cursor.execute(assigned_sql,(date_from, date_to))
	results_assigned = cursor.fetchone()
	final_dict["total_assigned"] = results_assigned[0]
		
	inprocess_sql = ("select count(*) from suitecrm.leads where status = 'In Process' and deleted = 0 and date_entered >= %s and date_entered <= %s")
	cursor.execute(inprocess_sql,(date_from, date_to))
	results_inprocess = cursor.fetchone()
	final_dict["total_inprocess"] = results_inprocess[0]
		
	converted_sql = ("select count(*) from suitecrm.leads where status = 'Converted' and deleted = 0 and date_entered >= %s and date_entered <= %s")
	cursor.execute(converted_sql,(date_from, date_to))
	results_converted = cursor.fetchone()
	final_dict["total_converted"] = results_converted[0]
		
	recycled_sql = ("select count(*) from suitecrm.leads where status = 'Recycled' and deleted = 0 and date_entered >= %s and date_entered <= %s")
	cursor.execute(recycled_sql,(date_from, date_to))
	results_recycled = cursor.fetchone()
	final_dict["total_recycled"] = results_recycled[0]
	
	dead_sql = ("select count(*) from suitecrm.leads where status = 'Dead' and deleted = 0 and date_entered >= %s and date_entered <= %s")
	cursor.execute(dead_sql,(date_from, date_to))
	results_dead = cursor.fetchone()
	final_dict["total_dead"] = results_dead[0]

	return {"data":final_dict}