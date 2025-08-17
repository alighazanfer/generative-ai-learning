import os
import requests


AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
OPENWEATHER_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")


def get_airport_iata(designation_name: str):
    params = {
        "access_key": AVIATIONSTACK_API_KEY,
        "search": designation_name
    }
    
    url = f"http://api.aviationstack.com/v1/airports"

    response = requests.get(url, params=params)
    data = response.json()

    return data


def get_weather(designation_name: str):
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": designation_name,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)
    data = response.json()
    return data
