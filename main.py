import json
from pprint import pprint

from fastapi import FastAPI, HTTPException, Query
import aiohttp
from os import environ as env
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shop-garden.prizma-dev.online", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=['*'],
)


def fill_hash_table():
    with open('nova_post_fullinfo.json', 'r', encoding='utf-8') as f:
        np_row_data = json.load(f)
    hash_table = {}
    for obj in np_row_data:
        city_ref = obj['cityRef']
        hash_table[city_ref] = obj
    print('ок хеш')
    return hash_table


hash_table_info = fill_hash_table()
client_session = aiohttp.ClientSession()


@app.get("/get_np_API_cities/")
async def get_np_API_cities(city_name: str = Query(...)):
    if not city_name:
        raise HTTPException(status_code=400, detail="Missing city_name parameter")

    url = str(env.get('NP_API_URL'))
    payload = {
        'apiKey': str(env.get('NP_API_KEY')),
        'modelName': 'Address',
        'calledMethod': 'searchSettlements',
        'methodProperties': {
            'CityName': city_name,
            'Limit': 5,
            'page': 1
        },
    }

    try:
        async with client_session.post(url, json=payload) as response:
            response.raise_for_status()
            response_json = await response.json()
            return response_json

    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail="something wrong")


@app.get("/get_np_API_warehouses/")
async def get_np_API_warehouses(city_ref: str = Query(...)):
    if not city_ref:
        raise HTTPException(status_code=400, detail="something wrong with city_ref")

    warehouses = hash_table_info[city_ref]
    print(warehouses)

    return warehouses


@app.on_event("shutdown")
async def shutdown_event():
    await client_session.close()
