from app import app
from datetime import datetime
from flask import request, json, render_template

import pytz
import geocoder
import requests

WEATHER_API_KEY = '1b3a741dcf79e9b639e6bf0ee916d553'
WEATHER_API_URL = 'http://api.openweathermap.org/data/2.5/weather'


@app.route('/weather/current/')
def index():
    try:
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        client_geo = geocoder.ipinfo(client_ip)
        lat, lon = client_geo.latlng
        timezone = client_geo.json['raw']['timezone']
        client_tz = pytz.timezone(timezone)
    except:
        return 'Sorry, we were unable to locate you.'

    try:
        api_url = f"{WEATHER_API_URL}?lat={lat}&lon={lon}&APPID={WEATHER_API_KEY}&units=metric"
        resp = requests.get(api_url)
        if resp.status_code == 200:
            weather_dict = json.loads(resp.text)
            weather_attrib = ['lat', 'lon', 'name', 'temp', 'humidity', 'pressure']
            weather_values = find_weather_values(weather_dict, weather_attrib)
            weather_values['timestamp'] = datetime.now(client_tz)
            return render_template('weather.json', items=weather_values)
        return 'Something went wrong with WeatherAPI or...\nTry again, please!'
    except:
        pass

    return 'Something went wrong.'


def find_weather_values(weather_dict, weather_attrib, result=None):
    result = {key: 0 for key in weather_attrib} if result is None else result
    if not isinstance(weather_dict, dict):
        return result
    for key, value in weather_dict.items():
        if isinstance(value, dict):
            find_weather_values(value, weather_attrib, result)
        elif key in weather_attrib:
            result[key] = value
    return result
