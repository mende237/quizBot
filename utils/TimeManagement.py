import requests
from datetime import datetime
import locale
from decouple import config


def get_time(time_zone:str)-> datetime:
    config.encoding = locale.getpreferredencoding(False)
    api_time_url = "https://api.ipgeolocation.io/timezone?apiKey={api_key}&tz={time_zone}/{city}"
    api_key = config("API_TIME_ZONE_KEY")
    tab = time_zone.splite("/")
    country = tab[0]
    city = tab[1]
    response = requests.get(api_time_url.format(api_key=api_key , time_zone = country , city = city))
    result_json = response.json()
    date_time = result_json["date_time"].split(" ")
    date = date_time[0]
    time = date_time[1]
    date_tab = date.split("-")
    time_tab = time.split(":")
    return datetime(int(date_tab[0]) , int(date_tab[1]) , int(date_tab[2]) , int(time_tab[0]) , int(time_tab[1]) , int(time_tab[2]))


def time_in_second(time : datetime) -> int:
		return time.hour *3600 + time.minute*60 + time.second