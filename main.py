from fastapi import FastAPI, Request
from database import connect
from fastapi import HTTPException
from database import get_item_by_name,find_minimum_leads_by_sale,get_all_dashboard,get_this_month_dashboard,get_today_dashboard,export_all_leads_in_Malaysia,get_leads_today,get_leads_yesterday,get_active_sales,assign_sale_with_lead
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
async def check_leads(item: ItemName):
    item_id = get_item_by_name(item.name)
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