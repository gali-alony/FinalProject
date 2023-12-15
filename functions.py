from newsapi import NewsApiClient
import keys
import urllib.request
import urllib.parse
import json
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

#retrieve the time and date at the zone asked for by the user
#returns a list of first time, then date
def what_time_date_is_it_at(location):
    lat_lng_location = geocode(location) #user: "Seattle" #FINDS LNG LAT PAIR as a tuple

    time_zone_location = time_zone_finder(lat_lng_location) #returns the time zone as "Asia/Jeruselam"
    time_zone_location_split = time_zone_location.split("/")
    #assumption made here is that there will be 2 OR 3 NEVER 1, no ASIA but Asia/something/something or ^
    if len(time_zone_location_split) == 2: #check if there is 2 OR 3... aka area, location AND region
        AREA = time_zone_location_split[0]
        LOCATION = time_zone_location_split[1]
        time = retrieve_time_in_area_safe(AREA, LOCATION)
        date = retrieve_date_in_area_safe(AREA, LOCATION)
    elif len(time_zone_location_split) == 3:
        AREA = time_zone_location_split[0]
        LOCATION = time_zone_location_split[1]
        REGION = time_zone_location_split[2]
        time = retrieve_time_in_area_safe(AREA, LOCATION, REGION)
        date = retrieve_time_in_date_safe(AREA, LOCATION, REGION)
    return [time, date]


#top 10 headlines and links to news articles in that location given location and key word
#param : list of key words from the user for what to search for
def get_top_headlines(location, word, word2=None, word3=None):
    #https://newsapi.org/v2/top-headlines?country=il&apiKey=109d3a6f5bc845dd8d4077fc80d2cf73
    newsapi = NewsApiClient(keys.NEWS_API_KEY)
    #top_headlines = newsapi.get_top_headlines(q="Washington")
    q_input = location + " AND " + word  #i.e : "Paris AND business"
    top_headlines = newsapi.get_everything(q=q_input, page_size= 10, sort_by="popularity")
    #sort by latest
    #print(top_headlines)
    return top_headlines

#TEST CODE
#print(get_top_headlines("Seattle", "work"))


#HELPER FUNCTIONS FOR WORLDTIMEAPI FUNCTIONALITY PLUS WORLDNEWSAPI
######################################################
#param: location (i.e "Seattle")
#return: (lat, lng) tuple of given location
def geocode(place):
    geolocator = Nominatim(user_agent="Learning Flask")
    location = geolocator.geocode(place)
    if location is None: #When there are no results found, returns None.
        return location
    latlng_tuple = (location.latitude, location.longitude)
    return latlng_tuple

#param: tuple (lat, lng)
#return: 'Asia/Kolkata' for example
def time_zone_finder(latlng):
    time_zone_finder_obj = TimezoneFinder()
    time_zone_at_location = time_zone_finder_obj.timezone_at(lng=latlng[1], lat=latlng[0])
    return time_zone_at_location



######################################################

#retrieve top news articles according to location
'''''''''
possible countriies for NEWSAPI -- ....
ar at au be bg br ca ch cn co cu cz de eg fr gb gr hk hu id ie il in it jp kr lt lv ma mx my ng nl no nz ph pl pt ro rs ru sa se sg si sk th tr tw ua us ve za
'''''''''
#/v2/top-headlines



#print(get_top_headlines('Seattle', 'business'))

def retrieve_area_time_info(area, location, region=None):

    baseurl = "http://worldtimeapi.org/api/timezone"

    # Encode the query parameters using urllib.parse.urlencode()
    param_dict = {'area': area, 'location': location, 'region': region}
    if region == None:
        paramstr = param_dict["area"] + "/" + param_dict["location"]
    else:
        paramstr = param_dict["area"] + "/" + param_dict["location"] + "/" + param_dict["region"]

    # Concatenate the base URL and the encoded query parameters
    url = baseurl + "/" + paramstr

    # Print the complete URL

    with urllib.request.urlopen(url) as response:
        time_zone_info = response.read().decode()
        time_zone_info_json = json.loads(time_zone_info)

        return time_zone_info_json

#area should be America, Europe, Asia, Pacific, Atlantic, Africa
def retrieve_area_time_info_safe(area, location, region=None):
    try:
        return retrieve_area_time_info(area, location, region)
    except urllib.error.URLError as e:
        print(f"Error trying to retrieve data {e}")
    except urllib.error.HTTPError as e:
        print(f"Error trying to retrieve data {e}")

def time_in_area(time_zone_info_json):
    return time_zone_info_json["datetime"]

#Retrieves the time in the area asked for in a safe manner
def retrieve_time_in_area_safe(area, location, region=None):
    time_zone_info_json = retrieve_area_time_info_safe(area, location, region)
    split_date_time = time_zone_info_json["datetime"].split("T")
    time = split_date_time[1]
    #take out details after seconds
    time_split = time.split('.')
    clean_time = time_split[0]
    #take out seconds to just hours and min
    time_hours_min = clean_time.split(":")
    hour_min = (time_hours_min[0], time_hours_min[1])
    #return tuple (hour, min)
    final_time_format = twentyfour_time_to_twelve(hour_min)
    return final_time_format

#Retrieves the date in the are asked for in a safe manner
def retrieve_date_in_area_safe(area, location, region=None):
    time_zone_info_json = retrieve_area_time_info_safe(area, location, region)
    split_date_time = time_zone_info_json["datetime"].split("T")
    date = split_date_time[0]
    return date

#HELPER METHOD
######################################################################
#convert 24 hour time to 12 hour time (am/pm)
def twentyfour_time_to_twelve(hour_min): #takes tuple of hour and min
    hour = int(hour_min[0])
    min = int(hour_min[1])
    #if 23, 22, 21, 20, 19,19,17,16,15,14,13
    if hour > 12:
        hour = hour - 12
        return str(hour) + ":" + str(min) + " pm"
    #if 12 = 12pm
    if hour == 12:
        return str(hour) + ":" + str(min) + " pm"
    #if 12 pm 11 am
    elif hour < 12 and hour > 0:
        return str(hour) + ":" + str(min) + " am"
    else: #if 0
        return "12:" + str(min) + " am"
######################################################################







