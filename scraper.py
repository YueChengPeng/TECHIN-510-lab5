import re
import json
import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo
import html

import requests

from db import get_db_conn


URL = 'https://visitseattle.org/events/page/'
URL_LIST_FILE = './data/links.json'
URL_DETAIL_FILE = './data/data.json'

def list_links():
    res = requests.get(URL + '1/')
    last_page_no = int(re.findall(r'bpn-last-page-link"><a href=".+?/page/(\d+?)/.+" title="Navigate to last page">', res.text)[0])

    links = []
    for page_no in range(1, last_page_no + 1):
        res = requests.get(URL + str(page_no) + '/')
        links.extend(re.findall(r'<h3 class="event-title"><a href="(https://visitseattle.org/events/.+?/)" title=".+?">.+?</a></h3>', res.text))

    json.dump(links, open(URL_LIST_FILE, 'w'))

def get_detail_page():
    links = json.load(open(URL_LIST_FILE, 'r'))
    data = []
    for link in links:
        try:
            row = {}
            res = requests.get(link)
            row['title'] = html.unescape(re.findall(r'<h1 class="page-title" itemprop="headline">(.+?)</h1>', res.text)[0])
            datetime_venue = re.findall(r'<h4><span>.*?(\d{1,2}/\d{1,2}/\d{4})</span> \| <span>(.+?)</span></h4>', res.text)[0]
            row['date'] = datetime.datetime.strptime(datetime_venue[0], '%m/%d/%Y').replace(tzinfo=ZoneInfo('America/Los_Angeles')).isoformat()
            row['venue'] = datetime_venue[1].strip() # remove leading/trailing whitespaces
            metas = re.findall(r'<a href=".+?" class="button big medium black category">(.+?)</a>', res.text)
            row['category'] = html.unescape(metas[0])
            row['location'] = metas[1]
            row['geolocation'] = get_geolocation(row['venue'], row['location'])
            row['weather_condition'], row['temperature'] = get_weather(row['geolocation'], row['date'])
            data.append(row)
            # print(row)
        except IndexError as e:
            print(f'Error: {e}')
            print(f'Link: {link}')
    json.dump(data, open(URL_DETAIL_FILE, 'w'))

def get_geolocation(venue, location):
    cord_base_url = "https://nominatim.openstreetmap.org/search.php"
    try:
        # first try to find the location with the venue name
        query_params = {
            "q": venue + ", Seattle",
            "format": "jsonv2"
        }
        # specify headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Referer': 'https://nominatim.openstreetmap.org/ui/search.html'
        }
        res_cord = requests.get(cord_base_url, params=query_params, headers=headers)
        res_dict = res_cord.json()
        return (res_dict[0]['lat'], res_dict[0]['lon'])
    except:
        try: 
            # if not found, try to find location with location name
            query_params = {
                "q": location + ", Seattle",
                "format": "jsonv2"
            }
            # specify headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                'Referer': 'https://nominatim.openstreetmap.org/ui/search.html'
            }
            res_cord = requests.get(cord_base_url, params=query_params, headers=headers)
            res_dict = res_cord.json()
            return (res_dict[0]['lat'], res_dict[0]['lon'])
        except:
            return None


def get_weather(geolocation, date):
    if geolocation is None:
        return None, None

    weather_base_url = "https://api.weather.gov/points/"
    try:
        # get the weather data of the location
        res_weather = requests.get(weather_base_url + str(geolocation[0]) + "," + str(geolocation[1]))
        res_dict = res_weather.json()

        # use the forecast property to get the weather data
        res_weather_detail = requests.get(res_dict['properties']['forecast'])
        res_dict = res_weather_detail.json()

        # convert the date format e.g. '1/17/2024' to '2024-01-17'
        formatted_date = re.search(r'\d{4}-\d{2}-\d{2}', date).group(0)
        
        for period in res_dict["properties"]["periods"]:
            # we are interested in the weather data of the day time of that day
            if period["startTime"].startswith(formatted_date) and period["endTime"].startswith(formatted_date):
                return period["detailedForecast"], period["temperature"] # there are many attributes in the weather data, we are interested in the detailedForecast and temperature
    except Exception as ex:
        print('Exception:')
        print(ex)
        
    return None, None


def insert_to_pg():
    q = '''
    CREATE TABLE IF NOT EXISTS events (
        url TEXT PRIMARY KEY,
        title TEXT,
        date TIMESTAMP WITH TIME ZONE,
        venue TEXT,
        category TEXT,
        location TEXT
    );
    '''
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(q)
    
    urls = json.load(open(URL_LIST_FILE, 'r'))
    data = json.load(open(URL_DETAIL_FILE, 'r'))
    for url, row in zip(urls, data):
        q = '''
        INSERT INTO events (url, title, date, venue, category, location, latitude, longitude, weather_condition, temperature)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING;
        '''
        cur.execute(q, (url, row['title'], row['date'], row['venue'], row['category'], row['location'], row['geolocation'][0], row['geolocation'][1], row['weather_condition'], row['temperature']))

if __name__ == '__main__':
    list_links()
    get_detail_page()
    insert_to_pg()
