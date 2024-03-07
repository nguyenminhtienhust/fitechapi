from fastapi import FastAPI, Request
from database import connect
from fastapi import HTTPException
from database import get_item_by_name,find_minimum_leads_by_sale,get_all_dashboard,get_this_month_dashboard,get_today_dashboard,export_all_leads_in_Malaysia,get_leads_today,get_leads_yesterday,get_active_sales,assign_sale_with_lead
from database import get_account_by_name, check_exist_email, check_email_lead, add_email_addressed, get_contact_by_name, get_contact_description
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
	item_id = get_item_by_name(item.title, item.last_name)
	if item_id is None:
		return {"data" : ""}
	else:
		return {"data" : item_id}

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
	if item_id is None:
		return {"data" : ""}
	else:
		return {"data" : item_id}    
		
		
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
	item_id = check_email_lead(item.name)
	if item_id is None:
		return {"data" : ""}
	else:
		return {"data" : item_id} 

@app.post("/contact/check/")
async def get_contact_by_name(item: ItemName):
	#item_id = get_contact_by_name(item.name)
	item_id = "aaaaa"
	if item_id is None:
		return {"data" : ""}
	else:
		return {"data" : item_id} 

@app.post("/contact/getdescription/")
async def get_contact_description(item: ItemName):
	item_id = get_contact_by_name(item.name)
	if item_id is None:
		return {"data" : ""}
	else:
		return {"data" : item_id} 