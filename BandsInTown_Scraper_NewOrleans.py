#Dependencies

print ('Let bandsintown scraping commence!')

from bs4 import BeautifulSoup
import requests
import string
import json
import geocoder
import mapbox
import geopy
from geopy.geocoders import Nominatim
import selenium
from selenium import webdriver

from selenium import webdriver
from bs4 import BeautifulSoup as bs
import datetime
from datetime import datetime as dt
import re
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.common.by import By

import os
print(os.name)
print(os.listdir("."))
import sys
import subprocess

#Set driver options
#options = Options()
#options.add_argument('--no-sandbox') # Bypass OS security model
#ptions.add_argument("--disable-notifications")

#driverLocation = webdriver.Chrome(chrome_options=options, executable_path=r'/Applications/chromedriver 3')
#driverLocation.quit()

#set driver options
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--window-size=1420,1080')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.binary_location='/usr/bin/google-chrome-stable'
chrome_driver_binary = "/usr/bin/chromedriver"
driver = webdriver.Chrome(executable_path=chrome_driver_binary, chrome_options=chrome_options)

def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

# Set date one week from now
nowDate = datetime.datetime.now()
week = datetime.timedelta(weeks = 1)
oneWeek = custom_strftime('%A, %B {S}, %Y', dt.now() + week)
oneWeekSplit = oneWeek.split(',')
oneWeekDay = oneWeekSplit[1]
oneWeekDayCleaned = (re.sub(r'\D+$', '', oneWeekDay))
oneWeekDayFinal = (oneWeekSplit[0] + "," + oneWeekDayCleaned + "," + oneWeekSplit[2])
#p=datetime.datetime.strptime('June 5, 2019', '%b %d, %Y')
#print p
oneWeekDateTime = datetime.datetime.strptime(oneWeekDayFinal, '%A, %B %d, %Y')
print(oneWeekDateTime)

# For testing, set date one day from now
day = datetime.timedelta(days=3)
oneDay = custom_strftime('%A, %B {S}, %Y', dt.now() + day)
oneDaySplit = oneDay.split(',')
oneDayfromNow = oneDaySplit[1]
oneDayCleaned = (re.sub(r'\D+$', '', oneDayfromNow))
oneDayFinal = (oneDaySplit[0] + "," + oneDayCleaned + "," + oneDaySplit[2])
oneDayDateTime = datetime.datetime.strptime(oneDayFinal, '%A, %B %d, %Y')
print(oneDayDateTime, oneWeekDateTime)


#Set up geocoder
#geocoder = mapbox.Geocoder(access_token='pk.eyJ1Ijoic3RhcnJtb3NzMSIsImEiOiJjam13ZHlxbXgwdncwM3FvMnJjeGVubjI5In0.-ridMV6bkkyNhbPfMJhVzw')
#chrome_options = Options()
#Set up web driver and base URL
#driver = webdriver.Chrome(options=chrome_options, executable_path='/usr/bin/chromedriver')
#chrome_options.add_argument('--no-sandbox')
#chrome_options.add_argument('--disable-dev-shm-usage')
#chrome_options.add_argument('--disable-gpu')

#chrome_options.add_argument('--headless')



#Set base url (new orleans)
base_url = 'https://www.bandsintown.com/?place_id=ChIJZYIRslSkIIYRtNMiXuhbBts&page='#new orleans
#base_url = 'https://www.bandsintown.com/?place_id=ChIJOwg_06VPwokRYv534QaPC8g&page='


events = []
eventContainerBucket = []

for i in range(1,15):

    #cycle through pages in range
    driver.get(base_url + str(i))
    pageURL = base_url + str(i)

    # get events links
    event_list = driver.find_elements_by_css_selector('div[class^=_3buUBPWBhUz9KBQqgXm-gf] a[class^=_3UX9sLQPbNUbfbaigy35li]')
    # collect href attribute of events in even_list
    events.extend(list(event.get_attribute("href") for event in event_list))

print("total events: ", (len(events)))

#GET request user-agent
headers = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}


# iterate through all events and open them.
item = {}
allEvents = []
for event in events:

    driver.get(event)
    currentUrl = driver.current_url
    print(currentUrl)
    try:
        currentRequest = requests.get(currentUrl, headers=headers)
        print (currentRequest)

        #print currentRequest.status_code
    except requests.exceptions.RequestException as e:
        print(e)
        continue


    if currentRequest.status_code == 200:
        #print ("link working")

        try:
            driver.find_element_by_css_selector('[class^=_3aZc11p4HaXXFyJp1e_XlL]')
            print ("element exists!")
        except (ElementNotVisibleException, NoSuchElementException, TimeoutException):
            print ("element doesn't exist")
            pass


        try:
            soup = bs(driver.find_element_by_css_selector('[class^=_3aZc11p4HaXXFyJp1e_XlL]').get_attribute('outerHTML'))
            soup2 = bs(driver.find_element_by_css_selector('[class^=_3iav3Z5WtxzstYRQKmp3cW]').get_attribute('outerHTML'))
        except (ElementNotVisibleException, NoSuchElementException, TimeoutException):
            print('no soup for you!')
            continue
        #print(soup)
        #print(soup2)
        #containers = driver.find_elements_by_css_selector('div[class^=_3aZc11p4HaXXFyJp1e_XlL]')
        #date_time = containers[2].text.split('\n')
        #print(date_time)

        # Only pull one weeks worth of data
        # Find date of event and format to compare against one week from now date
        try:
            dateMatch = soup.select_one('._1uSR2i2AbCWQwvNtGHdKnz').text
            dateMatch = dateMatch.replace("th","")
            dateMatch = dateMatch.replace("st","")
            dateMatch = dateMatch.replace("nd","")
            dateMatch = dateMatch.replace("rd","")
            dateMatch = dateMatch.replace(".", "")
            dateMatch = dateMatch.replace(",", "")
            print(dateMatch)

            datetime_object = datetime.datetime.strptime(dateMatch, '%b %d %Y')
            datetime_object_str = datetime_object.strftime("%Y-%m-%d")
            print(datetime_object_str)

        except Exception:
            print('no date')
            continue

        #print dateMatchDate, oneWeekDateTime

        #compare date of event to one week from now date
        if datetime_object <= oneDayDateTime:
            print ("this event occurs one week or less from today")
            print("datetime object is", datetime_object)
            #print "this event occurs one week or less from today"

            # Get artist
            artist = soup.select_one('._2a7MPEB7nHW5q-0UQJsl6T').text
            #artist = driver.find_element_by_class_name('_2a7MPEB7nHW5q-0UQJsl6T').text
            print(artist)


            # Get date
            date = soup.select_one('._1uSR2i2AbCWQwvNtGHdKnz').text
            print(date)

            # Get time
            try:
                time = soup2.select_one('._1iK6x88EqsupILFxTvC9ip').text
                print(time)
            except (ElementNotVisibleException, NoSuchElementException, TimeoutException):
                print('no time given')
                pass

            # Get address
            try:
                address= soup2.select_one('._36ZCsgOz77AokAEvfUegFS').text
                print(address)
            except (ElementNotVisibleException, NoSuchElementException, TimeoutException):
                print('no address given')
                continue

            # Get venue
            try:
                venue = soup.select_one('._241_qbENUQasyRr7CHEJmo').text
                print(venue)
            except (ElementNotVisibleException, NoSuchElementException, TimeoutException):
                print('no venue given')
                pass

            #Get image
            artistImage = 'https://assets.prod.bandsintown.com/images/fallbackImage.png'
            try:
                artistImage = driver.find_element_by_xpath("//div[@class='_1tHUGDRLiXm3qKqo5etU7i']//img").get_attribute("src")
                print(artistImage)
            except (ElementNotVisibleException, NoSuchElementException, TimeoutException):
                pass


            #Get genre information
            
            try:
                #genre = driver.find_element_by_xpath("//div[@class='_1Se_dqLEba70e_1AFsdzO3']").text
                #genre = driver.find_element_by_class_name('_1Se_dqLEba70e_1AFsdzO3').text
                genre = ''
                listed_genres = driver.find_elements_by_xpath("//div[@class='_1Se_dqLEba70e_1AFsdzO3']")
                for str in listed_genres:
                    genre += (str.text + ',')
                genre = genre.rstrip(',')
                #add space between commas
                genre = genre.replace(",",", ")
                print(genre)
                if len(genre)==0:
                    genre = 'No genre available'
                #genre = genreContainer.select_one('._1Se_dqLEba70e_1AFsdzO3').text
                #print(genre)
            except (ElementNotVisibleException, NoSuchElementException):
                 genre = 'No genre available'

            except (TimeoutException):
                pass



            #Get other information
            otherInfo = "No event info available"
            try:
                otherInfo = driver.find_element_by_xpath("//div[@class='Wla7qETMG4RlwfQQMTIqx']").text
                print(otherInfo)
            except (ElementNotVisibleException, NoSuchElementException, TimeoutException):
                pass


            # Capture additional event info
            readMoreEventInfo = '_3oaUGN5TFR0ZX0m015tWoH'
            try:
                driver.find_element_by_xpath("//div[@class='_3oaUGN5TFR0ZX0m015tWoH']").click();
                #print(moreInfo)
            except (ElementNotVisibleException, NoSuchElementException):
                pass


            #Regardless of whether or not there is "Read More", print complete event info.
            moreEventInfo = "No event info available"
            try:
                moreEventInfo = driver.find_element_by_xpath("//div[@class='Wla7qETMG4RlwfQQMTIqx']").text
                print("more event info is:", moreEventInfo)
            except (ElementNotVisibleException, NoSuchElementException, TimeoutException):
                print('no event info')
                pass



            # Get artist bio
            artistBio = "No artist bio available"
            try:
                artistBio = driver.find_element_by_xpath("//div[@class='VYokpSM2h3BWCLr3umXTd']").text
            except (ElementNotVisibleException, NoSuchElementException, TimeoutException):
                pass

            # Capture additional bio info
            readMore = '_1XRy4PRswl0g1ImXMkYiQO'
            try:
                driver.find_element_by_xpath("//div[@class='_1XRy4PRswl0g1ImXMkYiQO']").click();
                #print(moreInfo)
            except (ElementNotVisibleException, NoSuchElementException, TimeoutException):
                pass

            #Regardless of whether or not there is "Read More", print complete bio info.
            moreBioInfo = "No artist bio available"
            try:
                moreBioInfo = driver.find_element_by_xpath("//div[@class='VYokpSM2h3BWCLr3umXTd']").text
                print("more bio info is:", moreBioInfo)
            except (ElementNotVisibleException, NoSuchElementException, TimeoutException):
                print('no moreBioInfo')
                pass




            #print artistBio, otherInfo, genre

            # #Geocode address with GEOPY
            # result = ''
            # try:
            #     geolocator = Nominatim(user_agent="starrmoss1@gmail.com")
            #     result = geolocator.geocode(address)
            #     if result is None:
            #         result = ''
            #         coord_list = [0.0,0.0]
            #         pass
            #     else:
            #         print((result.latitude, result.longitude))
            #         coord_list = [result[1][0], result[1][1]]
            #         print(coord_list)

            # except (ElementNotVisibleException, NoSuchElementException, TimeoutException):
            #     print('no geocode possible')
            #     pass


            #Geocode Address using Google API
            api_key = "AIzaSyA_YL0GLJSgUGFyJOEEzA1eH_gQzqiWkyY"
            try:
                api_response = requests.get(
                    'https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'.format(address, api_key))
                api_response_dict = api_response.json()
                if api_response_dict['status'] == 'OK':
                    latitude = api_response_dict['results'][0]['geometry']['location']['lat']
                    longitude = api_response_dict['results'][0]['geometry']['location']['lng']
                    coord_list = [latitude, longitude]
                    print(coord_list)
                else:
                    print('geocoding not successful!')
                    pass
            except Exception as e:
                print('no result from geocode')
                pass


            #Bin information into 'item'
            item['Artist'] = artist
            item['Date'] = datetime_object_str
            item['eventDate'] = date
            item['Time'] = time
            item['Venue'] = venue
            item['Address'] = address
            item['artistImage'] = artistImage
            item['genre'] = genre
            item['otherInfo'] = moreEventInfo
            item['moreBioInfo'] = moreBioInfo
            #print(moreBioInfo)

            # Get latitude, longitude
            item['Coordinates'] = coord_list

            # Format output to JSON
            case = {'Artist': item['Artist'], 'Date': item['Date'], 'EventDate': item['eventDate'], 'Time': item['Time'], 'Venue': item['Venue'],
            'Address': item['Address'], 'Coordinates': coord_list, 'ArtistImage': item['artistImage'], 'Genre': item['genre'], 'otherInfo': item['otherInfo'], 'moreBioInfo': item['moreBioInfo']}

            item[event] = case

            #print case
            allEvents.append(case)


        elif currentRequest.status_code != 200:  # could also check == requests.codes.ok
            continue

        elif datetime_object > oneDayDateTime:
            print('event is over 3 days away')
            break

#eventsVariable = "var SFEvents = "
#print item
#print allEvents
#allEvents = eventsVariable + allEvents

#with open("testScrape.json", "w") as writeJSON:
   #file_str = json.dumps(allEvents, sort_keys=True)
   #file_str = "var events = " + file_str
   #writeJSON.write(file_str)

with open("/home/ubuntu/bandsintown/neworleans_events.json", "w") as writeJSON:
    file_str = json.dumps(allEvents, sort_keys=True)
    print('allEvents is',allEvents)
    print('filestr is',file_str)
    file_str = "var neworleans_events = " + file_str
    writeJSON.write(file_str)
driver.quit()

#tmp = subprocess.call("TASKKILL /f  /IM  /usr/bin/google-chrome-stable.EXE")
# #os.system("taskkill /f /im chromedriver.exe /T")
# if tmp!=0:
#     if tmp==1:
#         raise TaskkillError('Acces denided') #Error code=1 Permission Error 
#     if tmp==128:
#         raise TaskkillError("Process not found") #Error code=128 Process not found
#     else:
#         raise TaskkillError("UnknowError Error Code returned by taskkill:"+str(tmp))
# else:
#     print("Task succesfully killed")
#browserExe = "chrome" 
tmp = os.system("pkill chrome") 
print(tmp)
if tmp!=0:
    print('not sucessfull')
else:
    print("Task succesfully killed")

os.system("pkill chrome") 

print ("Data pull complete!")