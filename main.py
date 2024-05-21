from fastapi import FastAPI, Request
from database import connect
from fastapi import HTTPException
from database import get_item_by_name,find_minimum_leads_by_sale,get_all_dashboard,get_this_month_dashboard,get_today_dashboard,export_all_leads_in_Malaysia,get_leads_today,get_leads_yesterday,get_active_sales,assign_sale_with_lead
from database import get_account_by_name, check_exist_email, check_email_lead, add_email_addressed, get_contact_by_name, get_contact_assigned_user, get_account_assigned_user, get_lead_assigned_user_by_contact, get_lead_assigned_user_by_account
from database import get_lead_count, get_all_dashboard_by_date
from pydantic import BaseModel
from contextlib import asynccontextmanager
#from psycopg_pool import AsyncConnectionPool

app = FastAPI()

class ItemName(BaseModel):
	name: str

class ItemCount(BaseModel):
	user_id: str

class LeadAssignRequest(BaseModel):
	lead_id: str
	sale_id: str

class ItemEmail(BaseModel):
	id: str
	email : str
	email_cap: str
class ItemLead(BaseModel):
	title: str
	last_name: str
	first_name : str

class ItemGetLeadCount(BaseModel):
	date_from: str
	date_to: str
	sale_id : str
class ItemDashBoardByDate(BaseModel):
	date_from: str
	date_to: str

@app.get("/")
def read_root():
	return {"Hello": "World"}

@app.post("/detail/")
async def item_detail(item: ItemName):
	if get_item_by_name("tiktok"):
		return {"data" : True}
	else:
		return {"data": False}

@app.get("leads")
async def leads():
	return {"data": True}

@app.post("/leads/check/")
async def check_leads(item: ItemLead):
	item_id = get_item_by_name(item.title, item.last_name, item.first_name)
	if item_id == "":
		return {"data" : "", "status" : "", "phone_work" : "", "phone_mobile": "", "phone_other": ""}
	else:
		phone_work = ""
		if item_id[17] is not None:
			phone_work = item_id[17]
		phone_mobile = ""
		if item_id[16] is not None:
			phone_mobile = item_id[16]
		phone_other = ""
		if item_id[18] is not None:
			phone_other = item_id[18]
		website = ""
		if item_id[53] is not None:
			website = item_id[53]
			
		return {"data" : item_id[0], "status" : item_id[39], "phone_work" : phone_work, "phone_mobile": phone_mobile, "phone_other": phone_other, "website" : website, "assigned_user": item_id[7]}

@app.get("/leads/find-minimum-sale")
async def find_sale():
	user_id = find_minimum_leads_by_sale()
	return {"data" : user_id }

@app.get("/dashboard")
async def dashboard():
	data = get_all_dashboard()
	return data

@app.get("/dashboard-all")
async def all_dashboard():
	data = get_all_dashboard()
	return data

@app.get("/dashboard-this-month")
async def this_month_dashboard():
	data = get_this_month_dashboard()
	return data

@app.get("/dashboard-today")
async def today_dashboard():
	data = get_today_dashboard()
	return data


@app.get("/malaysia")
async def malaysia():
	data = export_all_leads_in_Malaysia()
	return data

@app.get("/get_leads_today")
async def get_all_leads_today():
	data = get_leads_today()
	return data

@app.get("/get_leads_yesterday")
async def get_all_leads_yesterday():
	data = get_leads_yesterday()
	return data

@app.get("/get_active_sales")
async def get_all_active_sales():
	data = get_active_sales()
	return data

@app.post("/assign_sale_with_lead")
async def assign_lead(request: LeadAssignRequest):
	data = assign_sale_with_lead(request.sale_id,request.lead_id)
	return data
	
@app.post("/accounts/check/")
async def account_get(item: ItemName):
	item_id = get_account_by_name(item.name)
	if item_id == "":
		return {"data" : "", "des" : ""}
	else:
		return {"data" : item_id[0], "des" : item_id[6]}    
		
		
@app.post("/emails/check/")
async def email_get(item: ItemName):
	item_id = check_exist_email(item.name)
	if item_id is None:
		return {"data" : ""}
	else:
		return {"data" : item_id} 

@app.post("/emails/add/")
async def email_add(item : ItemEmail):
	item_id = add_email_addressed(item.id, item.email, item.email_cap)
	return {"data" : item_id} 
		
@app.post("/email_lead/check/")
async def email_lead_get(item: ItemName):
	data = check_email_lead(item.name)
	return data

@app.post("/contact/check/")
async def get_contact(item: ItemName):
	item_id = get_contact_by_name(item.name)
	if item_id == "":
		return {"data" : "", "des": ""}
	else:
		return {"data" : item_id[0], "des": item_id[5]}   

@app.post("/contact/getassigneduser/")
async def get_contact_assigned(item: ItemName):
	item_id = get_contact_assigned_user(item.name)
	return {"data" : item_id} 

@app.post("/account/getassigneduser/")
async def get_account_assigned(item: ItemName):
	item_id = get_account_assigned_user(item.name)
	return {"data" : item_id} 

@app.post("/lead/getassigneduserbycontact/")
async def get_lead_assignedId_by_contact(item: ItemName):
	item_id = get_lead_assigned_user_by_contact(item.name)
	if item_id is None:
		return {"data" : ""}
	else:
		return {"data" : item_id}    

@app.post("/lead/getassigneduserbyaccount/")
async def get_lead_assignedId_by_account(item: ItemName):
	item_id = get_lead_assigned_user_by_account(item.name)
	if item_id is None:
		return {"data" : ""}
	else:
		return {"data" : item_id}   


@app.get("/lead/getleadcount/")
async def get_lead_count_by_day(item: ItemGetLeadCount):
	lead_count = get_lead_count(item.date_from, item.date_to, item.sale_id)
	return lead_count

@app.get("/getdashboardbydate")
async def get_dashboard_by_date(item : ItemDashBoardByDate):
	data = get_all_dashboard_by_date(item.date_from, item.date_to)
	return data