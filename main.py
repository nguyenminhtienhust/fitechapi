
from fastapi import FastAPI
from database import connect
from fastapi import HTTPException
from database import get_item_by_name
from pydantic import BaseModel

app = FastAPI()

class ItemName(BaseModel):
    name: str

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
    print(item.name)
    item_id = get_item_by_name(item.name)
    if item_id == -1:
        return {"data" : -1}
    else:
        return {"data" : item_id}

