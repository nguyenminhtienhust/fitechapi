
import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone, date
import calendar
import requests
import time
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

		response_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Response' and deleted = 0")
		cursor.execute(response_sql,(sale[0],))
		results_response = cursor.fetchone()
		detail_dict["total_response"] = results_response[0]
		
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
	supersale_response_count = ("select count(*) from suitecrm.leads where created_by = '6d14a07c-f8d3-d21a-f31c-6592da7f6c30' and deleted = 0 and status = 'Response'" )
	cursor.execute(supersale_response_count,())
	total_responsed_supersale = cursor.fetchone()
	final_dict["total_responsed_supersale"] = total_responsed_supersale[0]


	admin_sql = ("select count(*) from suitecrm.leads where created_by = '1' and deleted = 0")
	cursor.execute(admin_sql,())
	total_leads_by_admin = cursor.fetchone()
	final_dict["total_leads_by_admin"] = total_leads_by_admin[0]
	admin_response_count = ("select count(*) from suitecrm.leads where created_by = '1' and deleted = 0 and status = 'Response'" )
	cursor.execute(admin_response_count,())
	total_responsed_admin = cursor.fetchone()
	final_dict["total_responsed_admin"] = total_responsed_admin[0] 
	admin_process_count = ("select count(*) from suitecrm.leads where created_by = '1' and deleted = 0 and status = 'In Process'" )
	cursor.execute(admin_process_count,())
	total_process_admin = cursor.fetchone()
	final_dict["total_process_admin"] = total_process_admin[0] 
	admin_converted_count = ("select count(*) from suitecrm.leads where created_by = '1' and deleted = 0 and status = 'Converted'" )
	cursor.execute(admin_converted_count,())
	total_converted_admin = cursor.fetchone()
	final_dict["total_converted_admin"] = total_converted_admin[0] 
	admin_mess_sent_count = ("select count(*) from suitecrm.leads where created_by = '1' and deleted = 0 and status_description LIKE '%AdminAccount%'" )
	cursor.execute(admin_mess_sent_count,())
	total_mess_sent_lead_admin = cursor.fetchone()
	final_dict["total_mess_sent_lead_admin"] = total_mess_sent_lead_admin[0] 
	admin_res_count = ("select count(*) from suitecrm.leads where created_by = '1' and deleted = 0 and (status_description LIKE '%yes%' or status = 'Response')" )
	cursor.execute(admin_res_count,())
	total_mess_res_lead_admin = cursor.fetchone()
	final_dict["total_mess_res_lead_admin"] = total_mess_res_lead_admin[0] 
	# mess_count = get_num_mess_sent_lead("","")
	# final_dict["total_mess_sent_lead_admin"] = mess_count["sent_count"]
	# final_dict["total_mess_res_lead_admin"] = mess_count["res_count"]

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
	conn.close()
	return {"data":final_dict}

def get_this_month_dashboard():
	today = datetime.today()
	input_dt = today.date()
	day_num = input_dt.strftime("%d")
	first_date = input_dt - timedelta(days=int(day_num) - 1)
	first_date_str = first_date.strftime('%Y-%m-%d')
	dtfrom = datetime.fromisoformat(first_date_str)
	first_date_utc = dtfrom.astimezone(timezone.utc)
	#first_date_string = first_date.strftime('%Y-%m-%d')
	first_date_string = first_date_utc.strftime("%Y-%m-%d %H:%M:%S")
	
	current_year = first_date.year
	current_month = first_date.month
	number_day_per_month = calendar.monthrange(current_year, current_month)
	last_date = first_date.replace(day=number_day_per_month[1])
	last_date_str = last_date.strftime('%Y-%m-%d')
	dtTo = datetime.fromisoformat(last_date_str) + timedelta(1)
	last_date_utc = dtTo.astimezone(timezone.utc) - timedelta(seconds=1)
	#last_date_string = last_date.strftime('%Y-%m-%d')
	last_date_string = last_date_utc.strftime("%Y-%m-%d %H:%M:%S")
	conn = connect()
	cursor = conn.cursor()
	sql = ("select * from suitecrm.users where status = 'Active' and id != '6d14a07c-f8d3-d21a-f31c-6592da7f6c30' and is_admin = 'False';")
	cursor.execute(sql,())
	sales = cursor.fetchall()
	sales_list = []
	for sale in sales:
		full_name = sale[8] + " " + sale[7]
		detail_dict = {"full_name":full_name}

		total_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and date_entered >= %s and date_entered < %s and deleted = 0")
		cursor.execute(total_sql,(sale[0],first_date_string,last_date_string))                                                                                                                                                               
		results_total = cursor.fetchone()                                                                                                                                                   
		detail_dict["total_leads"] = results_total[0]

		new_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'New' and date_entered >= %s and date_entered < %s and deleted = 0")
		cursor.execute(new_sql,(sale[0],first_date_string,last_date_string))
		results_new = cursor.fetchone()
		detail_dict["total_new"] = results_new[0]

		assigned_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Assigned' and date_modified >= %s and date_modified < %s and deleted = 0")
		cursor.execute(assigned_sql,(sale[0],first_date_string,last_date_string))
		results_assigned = cursor.fetchone()
		detail_dict["total_assigned"] = results_assigned[0]

		response_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Response' and date_modified >= %s and date_modified < %s and deleted = 0")
		cursor.execute(response_sql,(sale[0],first_date_string,last_date_string))
		results_response = cursor.fetchone()
		detail_dict["total_response"] = results_response[0]
		
		inprocess_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'In Process' and date_modified >= %s and date_modified < %s and deleted = 0")
		cursor.execute(inprocess_sql,(sale[0],first_date_string,last_date_string))
		results_inprocess = cursor.fetchone()
		detail_dict["total_inprocess"] = results_inprocess[0]
		
		converted_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Converted' and date_modified >= %s and date_modified < %s and deleted = 0")
		cursor.execute(converted_sql,(sale[0],first_date_string,last_date_string))
		results_converted = cursor.fetchone()
		detail_dict["total_converted"] = results_converted[0]
		
		recycled_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Recycled' and date_modified >= %s and date_modified < %s and deleted = 0")
		cursor.execute(recycled_sql,(sale[0],first_date_string,last_date_string))
		results_recycled = cursor.fetchone()
		detail_dict["total_recycled"] = results_recycled[0]
		
		dead_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Dead' and date_modified >= %s and date_modified < %s and deleted = 0")
		cursor.execute(dead_sql,(sale[0],first_date_string,last_date_string))
		results_dead = cursor.fetchone()
		detail_dict["total_dead"] = results_dead[0]
		
		sales_list.append(detail_dict)
	final_dict = {"sales": sales_list}
	print(final_dict)
	sumary_sql = ("select count(*) from suitecrm.leads where date_entered >= %s and date_entered < %s and deleted = 0")
	cursor.execute(sumary_sql,(first_date_string,last_date_string))
	total_leads_result = cursor.fetchone()
	final_dict["total_leads"] = total_leads_result[0]

	supersale_sql = ("select count(*) from suitecrm.leads where created_by = '6d14a07c-f8d3-d21a-f31c-6592da7f6c30' and date_entered >= %s and date_entered < %s and deleted = 0")
	cursor.execute(supersale_sql,(first_date_string,last_date_string,))
	total_leads_by_supersale = cursor.fetchone()
	final_dict["total_leads_by_supersale"] = total_leads_by_supersale[0]
	supersale_response_count = ("select count(*) from suitecrm.leads where created_by = '6d14a07c-f8d3-d21a-f31c-6592da7f6c30' and date_modified >= %s and date_modified < %s and deleted = 0 and status = 'Response'" )
	cursor.execute(supersale_response_count,(first_date_string,last_date_string))
	total_responsed_supersale = cursor.fetchone()
	final_dict["total_responsed_supersale"] = total_responsed_supersale[0]

	admin_sql = ("select count(*) from suitecrm.leads where created_by = '1' and date_entered >= %s and date_entered < %s and deleted = 0")
	cursor.execute(admin_sql,(first_date_string,last_date_string))
	total_leads_by_admin = cursor.fetchone()
	final_dict["total_leads_by_admin"] = total_leads_by_admin[0]
	admin_response_count = ("select count(*) from suitecrm.leads where created_by = '1' and date_modified >= %s and date_modified < %s and deleted = 0 and status = 'Response'" )
	cursor.execute(admin_response_count,(first_date_string,last_date_string))
	total_responsed_admin = cursor.fetchone()
	final_dict["total_responsed_admin"] = total_responsed_admin[0]
	admin_process_count = ("select count(*) from suitecrm.leads where created_by = '1' and deleted = 0 and status = 'In Process' and date_modified >= %s and date_modified < %s" )
	cursor.execute(admin_process_count,(first_date_string,last_date_string))
	total_process_admin = cursor.fetchone()
	final_dict["total_process_admin"] = total_process_admin[0] 
	admin_converted_count = ("select count(*) from suitecrm.leads where created_by = '1' and deleted = 0 and status = 'Converted' and date_modified >= %s and date_modified < %s" )
	cursor.execute(admin_converted_count,(first_date_string,last_date_string))
	total_converted_admin = cursor.fetchone()
	final_dict["total_converted_admin"] = total_converted_admin[0] 
	admin_mess_sent_count = ("select count(*) from suitecrm.leads where created_by = '1' and deleted = 0 and date_entered >= %s and date_entered < %s and status_description LIKE '%AdminAccount%'" )
	cursor.execute(admin_mess_sent_count,(first_date_string,last_date_string))
	total_mess_sent_lead_admin = cursor.fetchone()
	final_dict["total_mess_sent_lead_admin"] = total_mess_sent_lead_admin[0] 
	admin_res_count = ("select count(*) from suitecrm.leads where created_by = '1' and deleted = 0 and date_modified >= %s and date_modified < %s and (status_description LIKE '%yes%' or status = 'Response')" )
	cursor.execute(admin_res_count,(first_date_string,last_date_string))
	total_mess_res_lead_admin = cursor.fetchone()
	final_dict["total_mess_res_lead_admin"] = total_mess_res_lead_admin[0] 
	# mess_count = get_num_mess_sent_lead(first_date_string,last_date_string)
	# final_dict["total_mess_sent_lead_admin"] = mess_count["sent_count"]
	# final_dict["total_mess_res_lead_admin"] = mess_count["res_count"]

	new_sql = ("select count(*) from suitecrm.leads where status = 'New' and date_entered >= %s and date_entered < %s and deleted = 0")
	cursor.execute(new_sql,(first_date_string,last_date_string))
	results_new = cursor.fetchone()
	final_dict["total_new_leads"] = results_new[0]

	assigned_sql = ("select count(*) from suitecrm.leads where status = 'Assigned' and date_entered >= %s and date_entered < %s and deleted = 0")
	cursor.execute(assigned_sql,(first_date_string,last_date_string))
	results_assigned = cursor.fetchone()
	final_dict["total_assigned"] = results_assigned[0]
		
	inprocess_sql = ("select count(*) from suitecrm.leads where status = 'In Process' and date_entered >= %s and date_entered < %s and deleted = 0")
	cursor.execute(inprocess_sql,(first_date_string,last_date_string))
	results_inprocess = cursor.fetchone()
	final_dict["total_inprocess"] = results_inprocess[0]
		
	converted_sql = ("select count(*) from suitecrm.leads where status = 'Converted' and date_entered >= %s and date_entered < %s and deleted = 0")
	cursor.execute(converted_sql,(first_date_string,last_date_string))
	results_converted = cursor.fetchone()
	final_dict["total_converted"] = results_converted[0]
		
	recycled_sql = ("select count(*) from suitecrm.leads where status = 'Recycled' and date_entered >= %s and date_entered < %s and deleted = 0")
	cursor.execute(recycled_sql,(first_date_string,last_date_string))
	results_recycled = cursor.fetchone()
	final_dict["total_recycled"] = results_recycled[0]
	
	dead_sql = ("select count(*) from suitecrm.leads where status = 'Dead' and date_entered >= %s and date_entered < %s and deleted = 0")
	cursor.execute(dead_sql,(first_date_string,last_date_string))
	results_dead = cursor.fetchone()
	final_dict["total_dead"] = results_dead[0]
	conn.close()
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
	conn.close()
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
	sql = ("SELECT assigned_user_id,date_entered FROM suitecrm.leads where first_name = %s and assigned_user_id is not null and assigned_user_id <> '' and assigned_user_id <> 'd6ea87ac-8c7e-a4ed-ba81-65f500a98e58' and assigned_user_id <> '1' and assigned_user_id <> '62b60dd0-9ab9-735e-e291-65d2cd0ab68e' ORDER BY date_entered desc limit 1 ")
	cursor.execute(sql, (name,))
	result = cursor.fetchone()
	conn.close()
	if result is None:
		return ""
	else:
		limit_date = datetime.today() + timedelta(-30)
		if(result[1] > limit_date):
			return "d6ea87ac-8c7e-a4ed-ba81-65f500a98e58"
		else:
			return result[0]

def get_lead_assigned_user_by_account(name):
	conn = connect()
	cursor = conn.cursor()
	sql = ("SELECT assigned_user_id,date_entered FROM suitecrm.leads where last_name = %s and assigned_user_id is not null and assigned_user_id <> '' and assigned_user_id <> 'd6ea87ac-8c7e-a4ed-ba81-65f500a98e58' and assigned_user_id <> '1' and assigned_user_id <> '62b60dd0-9ab9-735e-e291-65d2cd0ab68e' ORDER BY date_entered desc limit 1 ")
	cursor.execute(sql, (name,))
	result = cursor.fetchone()
	conn.close()
	if result is None:
		return ""
	else:
		limit_date = datetime.today() + timedelta(-30)
		if(result[1] > limit_date):
			return "d6ea87ac-8c7e-a4ed-ba81-65f500a98e58"
		else:
			return result[0]

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

		total_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and deleted = 0 and date_entered >= %s and date_entered < %s")
		cursor.execute(total_sql,(sale[0],date_from,date_to,))                                                                                                                                                               
		results_total = cursor.fetchone()                                                                                                                                                   
		detail_dict["total_leads"] = results_total[0]

		new_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'New' and deleted = 0 and date_entered >= %s and date_entered < %s" )
		cursor.execute(new_sql,(sale[0],date_from, date_to,))
		results_new = cursor.fetchone()
		detail_dict["total_new"] = results_new[0]

		assigned_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Assigned' and deleted = 0 and date_modified >= %s and date_modified < %s")
		cursor.execute(assigned_sql,(sale[0],date_from, date_to,))
		results_assigned = cursor.fetchone()
		detail_dict["total_assigned"] = results_assigned[0]

		response_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Response' and date_modified >= %s and date_modified < %s and deleted = 0")
		cursor.execute(response_sql,(sale[0],date_from, date_to,))
		results_response = cursor.fetchone()
		detail_dict["total_response"] = results_response[0]
		
		inprocess_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'In Process' and deleted = 0 and date_modified >= %s and date_modified < %s")
		cursor.execute(inprocess_sql,(sale[0],date_from, date_to,))
		results_inprocess = cursor.fetchone()
		detail_dict["total_inprocess"] = results_inprocess[0]
		
		converted_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Converted' and deleted = 0 and date_modified >= %s and date_modified < %s")
		cursor.execute(converted_sql,(sale[0],date_from, date_to,))
		results_converted = cursor.fetchone()
		detail_dict["total_converted"] = results_converted[0]
		
		recycled_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Recycled' and deleted = 0 and date_modified >= %s and date_modified < %s")
		cursor.execute(recycled_sql,(sale[0],date_from, date_to,))
		results_recycled = cursor.fetchone()
		detail_dict["total_recycled"] = results_recycled[0]
		
		dead_sql = ("select count(*) from suitecrm.leads where assigned_user_id = %s and status = 'Dead' and deleted = 0 and date_modified >= %s and date_modified < %s")
		cursor.execute(dead_sql,(sale[0],date_from, date_to))
		results_dead = cursor.fetchone()
		detail_dict["total_dead"] = results_dead[0]
		
		sales_list.append(detail_dict)
	final_dict = {"sales": sales_list}

	sumary_sql = ("select count(*) from suitecrm.leads where deleted = 0 and date_entered >= %s and date_entered < %s")
	cursor.execute(sumary_sql,(date_from, date_to,))
	total_leads_result = cursor.fetchone()
	final_dict["total_leads"] = total_leads_result[0]

	supersale_sql = ("select count(*) from suitecrm.leads where created_by = '6d14a07c-f8d3-d21a-f31c-6592da7f6c30' and deleted = 0 and date_entered >= %s and date_entered < %s")
	cursor.execute(supersale_sql,(date_from, date_to))
	total_leads_by_supersale = cursor.fetchone()
	final_dict["total_leads_by_supersale"] = total_leads_by_supersale[0]
	supersale_response_count = ("select count(*) from suitecrm.leads where created_by = '6d14a07c-f8d3-d21a-f31c-6592da7f6c30' and date_modified >= %s and date_modified < %s and deleted = 0 and status = 'Response'" )
	cursor.execute(supersale_response_count,(date_from, date_to))
	total_responsed_supersale = cursor.fetchone()
	final_dict["total_responsed_supersale"] = total_responsed_supersale[0]

	admin_sql = ("select count(*) from suitecrm.leads where created_by = '1' and deleted = 0 and date_entered >= %s and date_entered < %s")
	cursor.execute(admin_sql,(date_from, date_to))
	total_leads_by_admin = cursor.fetchone()
	final_dict["total_leads_by_admin"] = total_leads_by_admin[0]
	admin_response_count = ("select count(*) from suitecrm.leads where created_by = '1' and date_modified >= %s and date_modified < %s and deleted = 0 and status = 'Response'" )
	cursor.execute(admin_response_count,(date_from, date_to))
	total_responsed_admin = cursor.fetchone()
	final_dict["total_responsed_admin"] = total_responsed_admin[0]
	admin_process_count = ("select count(*) from suitecrm.leads where created_by = '1' and deleted = 0 and status = 'In Process' and date_modified >= %s and date_modified < %s" )
	cursor.execute(admin_process_count,(date_from, date_to))
	total_process_admin = cursor.fetchone()
	final_dict["total_process_admin"] = total_process_admin[0] 
	admin_converted_count = ("select count(*) from suitecrm.leads where created_by = '1' and deleted = 0 and status = 'Converted' and date_modified >= %s and date_modified < %s" )
	cursor.execute(admin_converted_count,(date_from, date_to))
	total_converted_admin = cursor.fetchone()
	final_dict["total_converted_admin"] = total_converted_admin[0] 
	admin_mess_sent_count = ("select count(*) from suitecrm.leads where created_by = '1' and deleted = 0 and date_entered >= %s and date_entered < %s and status_description LIKE '%AdminAccount%'" )
	cursor.execute(admin_mess_sent_count,(date_from, date_to))
	total_mess_sent_lead_admin = cursor.fetchone()
	final_dict["total_mess_sent_lead_admin"] = total_mess_sent_lead_admin[0] 
	admin_res_count = ("select count(*) from suitecrm.leads where created_by = '1' and deleted = 0 and date_modified >= %s and date_modified < %s and (status_description LIKE '%yes%' or status = 'Response')" )
	cursor.execute(admin_res_count,(date_from, date_to))
	total_mess_res_lead_admin = cursor.fetchone()
	final_dict["total_mess_res_lead_admin"] = total_mess_res_lead_admin[0] 
	# mess_count = get_num_mess_sent_lead(date_from,date_to)
	# final_dict["total_mess_sent_lead_admin"] = mess_count["sent_count"]
	# final_dict["total_mess_res_lead_admin"] = mess_count["res_count"]

	new_sql = ("select count(*) from suitecrm.leads where status = 'New' and deleted = 0 and date_entered >= %s and date_entered < %s")
	cursor.execute(new_sql,(date_from, date_to))
	results_new = cursor.fetchone()
	final_dict["total_new_leads"] = results_new[0]

	assigned_sql = ("select count(*) from suitecrm.leads where status = 'Assigned' and deleted = 0 and date_modified >= %s and date_modified < %s")
	cursor.execute(assigned_sql,(date_from, date_to))
	results_assigned = cursor.fetchone()
	final_dict["total_assigned"] = results_assigned[0]
		
	inprocess_sql = ("select count(*) from suitecrm.leads where status = 'In Process' and deleted = 0 and date_modified >= %s and date_modified < %s")
	cursor.execute(inprocess_sql,(date_from, date_to))
	results_inprocess = cursor.fetchone()
	final_dict["total_inprocess"] = results_inprocess[0]
		
	converted_sql = ("select count(*) from suitecrm.leads where status = 'Converted' and deleted = 0 and date_modified >= %s and date_modified < %s")
	cursor.execute(converted_sql,(date_from, date_to))
	results_converted = cursor.fetchone()
	final_dict["total_converted"] = results_converted[0]
		
	recycled_sql = ("select count(*) from suitecrm.leads where status = 'Recycled' and deleted = 0 and date_modified >= %s and date_modified < %s")
	cursor.execute(recycled_sql,(date_from, date_to))
	results_recycled = cursor.fetchone()
	final_dict["total_recycled"] = results_recycled[0]
	
	dead_sql = ("select count(*) from suitecrm.leads where status = 'Dead' and deleted = 0 and date_modified >= %s and date_modified < %s")
	cursor.execute(dead_sql,(date_from, date_to))
	results_dead = cursor.fetchone()
	final_dict["total_dead"] = results_dead[0]
	conn.close()
	return {"data":final_dict}

def login_crm():
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	jsondata = {}
	login_api = "https://crm.fitech.com.vn/Api/access_token"
	
	jsondata["grant_type"] = "client_credentials"
	jsondata["client_id"] = "ccfd00e1-307e-e56f-1e06-6592d6c95397"
	jsondata["client_secret"] = "apiuser@Fitech#vn"
	print(type(jsondata))
	data = requests.post(login_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		return json_object["access_token"]

def get_num_mess_sent_lead(date_from, date_to):
	access_token = login_crm()
	sent_count = 0
	res_count = 0
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	sent_sql = "https://crm.fitech.com.vn/Api/V8/module/Leads?filter[mess_sent_c][eq]=1"
	if(date_from != ""):
		sent_sql = "https://crm.fitech.com.vn/Api/V8/module/Leads?filter[mess_sent_c][eq]=1&filter[date_entered][GTE]=" + date_from + "&filter[date_entered][LTE]=" + date_to
	sent_data = requests.get(sent_sql,headers=headers)
	time.sleep(2)
	if sent_data.status_code != 200:
		print(sent_data.status_code)
		print(sent_data.reason)
		sent_count = -1
	else:
		json_object = sent_data.json()
		sent_count = len(json_object["data"])
	res_sql = "https://crm.fitech.com.vn/Api/V8/module/Leads?filter[mess_sent_c][eq]=1&filter[status][eq]=Response"
	if(date_from != ""):
		res_sql = "https://crm.fitech.com.vn/Api/V8/module/Leads?filter[mess_sent_c][eq]=1&filter[date_entered][GTE]=" + date_from + "&filter[date_entered][LTE]=" + date_to + "&filter[status][eq]=Response"
	res_data = requests.get(res_sql,headers=headers)
	time.sleep(2)
	if res_data.status_code != 200:
		print(res_data.status_code)
		print(res_data.reason)
		res_count = -1
	else:
		json_object = res_data.json()
		res_count = len(json_object["data"])
	return {"sent_count" : sent_count, "res_count": res_count} 


def get_email_exist(email):
	#datetime_object = datetime.strptime(date_from, '%m/%d/%y %H:%M:%S')
	conn = connect()
	cursor = conn.cursor()
	sql_get_email = ("SELECT id FROM suitecrm.email_addresses where email_address = %s and deleted = 0")
	cursor.execute(sql_get_email, (email,))
	email_id = cursor.fetchone()
	if email_id is None:
		conn.close()
		return 0
	else:
		query_date = datetime.today() + timedelta(-30)
		query_date_string = query_date.strftime("%Y-%m-%d %H:%M:%S")
		sql = ("SELECT count(*) from suitecrm.leads where id in (SELECT bean_id from suitecrm.email_addr_bean_rel where email_address_id = %s) and date_entered > %s and assigned_user_id is not Null and assigned_user_id <> '' ")
		cursor.execute(sql, (email_id[0],query_date_string,))
		lead_count = cursor.fetchone()
		conn.close()
		return lead_count[0]
	

def get_performance_report(saleMember, input_year):
	print(saleMember,"saleMember")
	current_month = datetime.now().month
	current_year = datetime.now().year
	search_year = int(input_year)
	if(search_year != current_year):
		current_month = 12
	month = 1
	conn = connect()
	cursor = conn.cursor()
	detail_list = []
	if saleMember:
		where_sql = " and assigned_user_id = %s"
		while month <= current_month:
			detail_dict = {"month":month}
			number_day_per_month = calendar.monthrange(search_year, month)
			first_date = date(search_year, month, 1)
			first_date_str = first_date.strftime('%Y-%m-%d')
			dtfrom = datetime.fromisoformat(first_date_str)
			first_date_utc = dtfrom.astimezone(timezone.utc)
			first_date_string = first_date_utc.strftime("%Y-%m-%d %H:%M:%S")
			last_date = first_date.replace(day=number_day_per_month[1])
			last_date_str = last_date.strftime('%Y-%m-%d')
			dtTo = datetime.fromisoformat(last_date_str) + timedelta(1)
			last_date_utc = dtTo.astimezone(timezone.utc) - timedelta(seconds=1)
			last_date_string = last_date_utc.strftime("%Y-%m-%d %H:%M:%S")
			sql_total = "Select count(*) from leads where deleted = 0 and date_entered >= %s and date_entered < %s" + where_sql
			cursor.execute(sql_total,(first_date_string,last_date_string,saleMember)) 
			total_leads = cursor.fetchone()
			detail_dict["total_lead"] = total_leads[0]
			detail_dict["total_leads_assigned"] = total_leads[0]
			sql_total_contact = "Select count(*) from leads where deleted = 0 and date_entered >= %s and date_entered < %s and (status_description LIKE '%AdminAccount%' or status in ('Assigned', 'Response','In Process','Converted') )" + where_sql
			cursor.execute(sql_total_contact,(first_date_string,last_date_string,saleMember))
			total_leads_contact = cursor.fetchone()
			detail_dict["total_lead_contact"] = total_leads_contact[0]
			if(detail_dict["total_lead"] != 0):
				detail_dict["contact_rate"] = round((detail_dict["total_lead_contact"]/detail_dict["total_lead"])*100,3)
			else:
				detail_dict["contact_rate"] = 'NaN'
			detail_dict["assigned_rate"] = detail_dict["contact_rate"]
			sql_replied_count = "Select count(*) from leads where deleted = 0 and date_entered >= %s and date_entered < %s and (status in ('Response','In Process','Converted') or status_description LIKE '%yes%' )" + where_sql
			cursor.execute(sql_replied_count,(first_date_string,last_date_string,saleMember))
			total_replied_contact = cursor.fetchone()
			detail_dict["total_replied_contact"] = total_replied_contact[0]
			if(detail_dict["total_lead_contact"] != 0):
				detail_dict["replied_rate"] = round((detail_dict["total_replied_contact"]/detail_dict["total_lead_contact"])*100,3)
			else:
				detail_dict["replied_rate"] = 'NaN'
			sql_meeting_count = "Select id from meetings where deleted = 0 and parent_id in (select id from leads where deleted = 0 and date_entered >= %s and date_entered < %s " + where_sql + ")" 
			#sql_meeting_count = "Select count(*) from leads where deleted = 0 and date_entered >= %s and date_entered < %s and id in (select parent_id from meetings)" + where_sql
			cursor.execute(sql_meeting_count,(first_date_string,last_date_string,saleMember))
			# total_meeting = cursor.fetchone()
			# detail_dict["total_meeting"] = total_meeting[0]
			total_meeting = cursor.fetchall()
			detail_dict["total_meeting"] = len(total_meeting)
			meeting_list = []
			for meeing in total_meeting:
				meeting_list.append(meeing[0])
			detail_dict["meeting_list"] = meeting_list
			if(detail_dict["total_lead_contact"] != 0):
				detail_dict["meeting_rate"] = round((detail_dict["total_meeting"]/detail_dict["total_lead_contact"])*100,3)
			else:
				detail_dict["meeting_rate"] = 'NaN'
			detail_dict["from_date"] = first_date_string
			detail_dict["to_date"] = last_date_string
			detail_list.append(detail_dict)
			month = month + 1
		final_dict = {"report": detail_list}
		conn.close()
		return final_dict
	else:
		while month <= current_month:
			detail_dict = {"month":month}
			number_day_per_month = calendar.monthrange(search_year, month)
			first_date = date(search_year, month, 1)
			first_date_str = first_date.strftime('%Y-%m-%d')
			dtfrom = datetime.fromisoformat(first_date_str)
			first_date_utc = dtfrom.astimezone(timezone.utc)
			first_date_string = first_date_utc.strftime("%Y-%m-%d %H:%M:%S")
			last_date = first_date.replace(day=number_day_per_month[1])
			last_date_str = last_date.strftime('%Y-%m-%d')
			dtTo = datetime.fromisoformat(last_date_str) + timedelta(1)
			last_date_utc = dtTo.astimezone(timezone.utc) - timedelta(seconds=1)
			last_date_string = last_date_utc.strftime("%Y-%m-%d %H:%M:%S")
			sql_total = "Select count(*) from leads where deleted = 0 and date_entered >= %s and date_entered < %s"
			cursor.execute(sql_total,(first_date_string,last_date_string))
			total_leads = cursor.fetchone()
			detail_dict["total_lead"] = total_leads[0]
			sql_total_assigned = "Select count(*) from leads where deleted = 0 and date_entered >= %s and date_entered < %s and (assigned_user_id is not null and assigned_user_id <> '')"
			cursor.execute(sql_total_assigned,(first_date_string,last_date_string))
			total_leads_assigned = cursor.fetchone()
			detail_dict["total_leads_assigned"] = total_leads_assigned[0]
			if(detail_dict["total_lead"] != 0):
				detail_dict["assigned_rate"] = round((detail_dict["total_leads_assigned"]/detail_dict["total_lead"])*100,3)
			else:
				detail_dict["assigned_rate"] = 'NaN'
			sql_total_contact = "Select count(*) from leads where deleted = 0 and date_entered >= %s and date_entered < %s and (status_description LIKE '%AdminAccount%' or status in ('Assigned', 'Response','In Process','Converted') )"
			cursor.execute(sql_total_contact,(first_date_string,last_date_string))
			total_leads_contact = cursor.fetchone()
			detail_dict["total_lead_contact"] = total_leads_contact[0]
			if(detail_dict["total_leads_assigned"] != 0):
				detail_dict["contact_rate"] = round((detail_dict["total_lead_contact"]/detail_dict["total_leads_assigned"])*100,3)
			else:
				detail_dict["contact_rate"] = 'NaN'
			sql_replied_count = "Select count(*) from leads where deleted = 0 and date_entered >= %s and date_entered < %s and (status in ('Response','In Process','Converted') or status_description LIKE '%yes%' )" 
			cursor.execute(sql_replied_count,(first_date_string,last_date_string))
			total_replied_contact = cursor.fetchone()
			detail_dict["total_replied_contact"] = total_replied_contact[0]
			if(detail_dict["total_lead_contact"] != 0):
				detail_dict["replied_rate"] = round((detail_dict["total_replied_contact"]/detail_dict["total_lead_contact"])*100,3)
			else:
				detail_dict["replied_rate"] = 'NaN'
			sql_meeting_count = "Select id from meetings where deleted = 0 and parent_id in (select id from leads where deleted = 0 and date_entered >= %s and date_entered < %s)" 
			#sql_meeting_count = "Select count(*) from leads where deleted = 0 and date_entered >= %s and date_entered < %s and id in (select parent_id from meetings)" 
			cursor.execute(sql_meeting_count,(first_date_string,last_date_string))
			#total_meeting = cursor.fetchone()
			#detail_dict["total_meeting"] = total_meeting[0]
			total_meeting = cursor.fetchall()
			detail_dict["total_meeting"] = len(total_meeting)
			meeting_list = []
			for meeing in total_meeting:
				meeting_list.append(meeing[0])
			detail_dict["meeting_list"] = meeting_list
			if(detail_dict["total_lead_contact"] != 0):
				detail_dict["meeting_rate"] = round((detail_dict["total_meeting"]/detail_dict["total_lead_contact"])*100,3)
			else:
				detail_dict["meeting_rate"] = 'NaN'
			detail_dict["from_date"] = first_date_string
			detail_dict["to_date"] = last_date_string
			detail_list.append(detail_dict)
			month = month + 1
		final_dict = {"report": detail_list}
		conn.close()
		return final_dict
	

def get_meetings(meeting_ids):
	if meeting_ids:
		arr = meeting_ids.split(",")
		meeting_list=[]
		if (len(arr) == 1):
			sql = "Select l.last_name,l.id as lead_id,usr.first_name, m.* from meetings m left join leads l on m.parent_id = l.id left join users usr on usr.id = m.created_by where m.id = %s"
			conn = connect()
			cursor = conn.cursor()
			cursor.execute(sql,(arr[0],))
			total_meeting = cursor.fetchall()
			for meeting in total_meeting:
				meeting_dict={"Lead" : meeting[0]}
				#meeting_dict["Created_Date"] = meeting[5]
				utc_time= utc_to_local(meeting[5])
				meeting_dict["Created_Date"] = utc_time.strftime("%d-%m-%Y %H:%M:%S")
				meeting_dict["Name"] = meeting[4]
				meeting_dict["Created_By"] = meeting[2]
				meeting_dict["Lead_id"] = meeting[1]
				meeting_list.append(meeting_dict)
			final_dict = {"meeting":meeting_list}
			conn.close()
			return final_dict
		else:
			t = tuple(arr)
			sql = "select l.last_name,l.id as lead_id,usr.first_name, m.* from meetings m left join leads l on m.parent_id = l.id left join users usr on usr.id = m.created_by where m.id IN {}".format(t)
			conn = connect()
			cursor = conn.cursor()
			cursor.execute(sql)
			total_meeting = cursor.fetchall()
			for meeting in total_meeting:
				meeting_dict={"Lead" : meeting[0]}
				#meeting_dict["Created_Date"] = meeting[5]
				utc_time= utc_to_local(meeting[5])
				meeting_dict["Created_Date"] = utc_time.strftime("%d-%m-%Y %H:%M:%S")
				meeting_dict["Name"] = meeting[4]
				meeting_dict["Created_By"] = meeting[2]
				meeting_dict["Lead_id"] = meeting[1]
				meeting_list.append(meeting_dict)
			final_dict = {"meeting":meeting_list}
			conn.close()
			return final_dict
	else:
		meeting_list=[]
		sql = "select l.last_name,l.id as lead_id,usr.first_name, m.* from meetings m left join leads l on m.parent_id = l.id left join users usr on usr.id = m.created_by"
		conn = connect()
		cursor = conn.cursor()
		cursor.execute(sql)
		total_meeting = cursor.fetchall()
		for meeting in total_meeting:
			meeting_dict={"Lead" : meeting[0]}
			#meeting_dict["Created_Date"] = meeting[5]
			utc_time= utc_to_local(meeting[5])
			meeting_dict["Created_Date"] = utc_time.strftime("%d-%m-%Y %H:%M:%S")
			meeting_dict["Name"] = meeting[4]
			meeting_dict["Created_By"] = meeting[2]
			meeting_dict["Lead_id"] = meeting[1]
			meeting_list.append(meeting_dict)
		final_dict = {"meeting":meeting_list}
		conn.close()
		return final_dict


def get_lead_status_with_email(email):
	#datetime_object = datetime.strptime(date_from, '%m/%d/%y %H:%M:%S')
	conn = connect()
	cursor = conn.cursor()
	sql_get_email = ("SELECT id FROM suitecrm.email_addresses where email_address = %s and deleted = 0")
	cursor.execute(sql_get_email, (email,))
	email_id = cursor.fetchone()
	if email_id is None:
		conn.close()
		return 0
	else:
		sql = ("SELECT count(*) from suitecrm.leads where id in (SELECT bean_id from suitecrm.email_addr_bean_rel where email_address_id = %s) and status in ('Response', 'In Process','Converted') ")
		cursor.execute(sql, (email_id[0],))
		lead_count = cursor.fetchone()
		conn.close()
		return lead_count[0]
	

def getMeeting_By_Date(from_date, to_date, saleMember):
	meeting_list=[]
	conn = connect()
	cursor = conn.cursor()
	formated_from_date = from_date.replace("_"," ")
	formated_to_date = to_date.replace("_"," ")
	from_date_obj = datetime.strptime(formated_from_date, '%Y-%m-%d %H:%M:%S')
	to_date_obj = datetime.strptime(formated_to_date, '%Y-%m-%d %H:%M:%S')
	if saleMember:
		sql_meeting_count = "select l.last_name,l.id as lead_id,usr.first_name, m.* from meetings m left join leads l on m.parent_id = l.id left join users usr on usr.id = m.created_by where m.deleted = 0 and parent_id in (select id from leads where deleted = 0 and date_entered >= %s and date_entered < %s and assigned_user_id = %s) order by m.date_entered asc" 
		cursor.execute(sql_meeting_count,(formated_from_date,formated_to_date,saleMember,))
		total_meeting = cursor.fetchall()
		for meeting in total_meeting:
			meeting_dict={"Lead" : meeting[0]}
			#meeting_dict["Created_Date"] = meeting[5]
			utc_time= utc_to_local(meeting[5])
			meeting_dict["Created_Date"] = utc_time.strftime("%d-%m-%Y %H:%M:%S")
			meeting_dict["Name"] = meeting[4]
			meeting_dict["Created_By"] = meeting[2]
			meeting_dict["Lead_id"] = meeting[1]
			meeting_list.append(meeting_dict)
		final_dict = {"meeting":meeting_list}
		conn.close()
		return final_dict
	else:
		sql_meeting_count = "select l.last_name,l.id as lead_id,usr.first_name, m.* from meetings m left join leads l on m.parent_id = l.id left join users usr on usr.id = m.created_by where m.deleted = 0 and parent_id in (select id from leads where deleted = 0 and date_entered >= %s and date_entered < %s) order by m.date_entered asc" 
		cursor.execute(sql_meeting_count,(formated_from_date,formated_to_date,))
		total_meeting = cursor.fetchall()
		for meeting in total_meeting:
			meeting_dict={"Lead" : meeting[0]}
			#meeting_dict["Created_Date"] = meeting[5]
			utc_time= utc_to_local(meeting[5])
			meeting_dict["Created_Date"] = utc_time.strftime("%d-%m-%Y %H:%M:%S")
			meeting_dict["Name"] = meeting[4]
			meeting_dict["Created_By"] = meeting[2]
			meeting_dict["Lead_id"] = meeting[1]
			meeting_list.append(meeting_dict)
		final_dict = {"meeting":meeting_list}
		conn.close()
		return final_dict

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
# def responsed_lead_count_by_company(account):
# 	conn = connect()
# 	cursor = conn.cursor()
# 	sql = ("SELECT count(*) from leads where ")