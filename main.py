
from fastapi import FastAPI
from database import connect
from fastapi import HTTPException
from database import check_leads_name
from pydantic import BaseModel

app = FastAPI()

@app.post("/users/")
async def add_user(name: str, age: int):
    user_id = create_user(name, age)
    if user_id:
        return {"id": user_id, "name": name, "age": age}
    else:
        raise HTTPException(status_code=400, detail="User not created")

class ItemName(BaseModel):
    name: str

@app.post("/detail/")
async def item_detail(item: ItemName):
    if check_leads_name("tiktok"):
        return {"data" : True}
    else:
        return {"data": False}

@app.get("leads")
async def leads():
	return {"data": True}

@app.post("/leads/check/")
async def check_leads(item: ItemName):
    print(item.name)
    if check_leads_name(item.name):
        return {"data" : True}
    else:
        return {"data" : False}

