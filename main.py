from fastapi import FastAPI, HTTPException, Query
import aiohttp
from starlette.middleware.cors import CORSMiddleware
from os import environ as env
from dotenv import load_dotenv

print('До')
load_dotenv()
print("После")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shop-garden.prizma-dev.online/"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)


client_session = aiohttp.ClientSession()


@app.get("/get_np_API_cities")
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
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
async def shutdown_event():
    await client_session.close()
