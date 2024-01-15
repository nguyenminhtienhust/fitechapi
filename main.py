from fastapi import FastAPI
from database import connect
from fastapi import HTTPException
from database import get_item_by_name,find_minimum_leads_by_sale
from pydantic import BaseModel
app = FastAPI()

class ItemName(BaseModel):
    name: str

class ItemCount(BaseModel):
    user_id: str
    
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
