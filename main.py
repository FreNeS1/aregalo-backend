from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import *
from aregalo import FileStore, PresentCreateData, PresentWishData, StoreService

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])
store = FileStore(data_path)
service = StoreService(store)


@app.get("/_status")
async def status():
    return {"status": "ok"}


@app.get("/aregalo/users")
async def get_users():
    return service.get_all_users()


@app.get("/aregalo/users/{user}")
async def get_user(user: str):
    return service.get_user_data(user)


@app.get("/aregalo/{user}/presents")
async def get_present_wish_list(user: str):
    return service.get_user_present_wish_list(user)


@app.post("/aregalo/{user}/presents")
async def create_present(user: str, present_data: PresentCreateData):
    return service.create_present(user, present_data)


@app.put("/aregalo/{user}/presents/{present_id}")
async def update_present(user: str, present_id: int, present_data: PresentWishData):
    return service.update_present(user, present_id, present_data)


@app.delete("/aregalo/{user}/presents/{present_id}")
async def delete_present(user: str, present_id: int):
    return service.delete_present(user, present_id)


@app.get("/aregalo/{gifter}/{wisher}/presents/")
async def get_present_gift_list(wisher: str):
    return service.get_user_present_gift_list(wisher)


@app.put("/aregalo/{gifter}/{wisher}/presents/{present_id}")
async def assign_user_to_present(gifter: str, wisher: str, present_id: int):
    return service.assign_user_to_present(wisher, present_id, gifter)


@app.delete("/aregalo/{gifter}/{wisher}/presents/{present_id}")
async def remove_user_from_present(gifter: str, wisher: str, present_id: int):
    return service.remove_user_from_present(wisher, present_id, gifter)
