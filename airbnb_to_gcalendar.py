from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time, os
import requests
import re
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import shutil
import os.path
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import BatchHttpRequest
import pytz
import locale

# Webdriver options
options = Options()
service = Service('chromedriver.exe')
service.start()
prefs = {"profile.default_content_settings.geolocation": 2}
options = webdriver.ChromeOptions()
options.headless = True
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option("prefs", prefs)
options.add_argument('--deny-permission-prompts')
options.add_argument('--no-sandbox')
options.add_argument("--log-level=3")
options.add_argument("--disable-blink-features=AutomationControlled") 
options.add_experimental_option("excludeSwitches", ["enable-automation"])
user=os.getlogin()
options.add_argument("user-data-dir=C:\\Users\\"+user+"\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

# Airbnb Login credentials
email = "EMAIL ADDRESS"
password = "PASSWORD"

# Google API credentials file
GOOGLE_CREDENTIALS_FILE = "GOOGLE_CREDENTIALS_FILE"
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Open Airbnb website
bot = webdriver.Chrome(ChromeDriverManager().install(),options=options);
print("------> Accessing Airbnb Reservations Page")
url="https://www.airbnb.com/hosting/reservations"
bot.get(url)

# Handling the login
print("------> Checking if we need to log In...")
try:
    emailBtn = bot.find_element(By.CSS_SELECTOR, "button[data-testid='social-auth-button-email']")
    emailBtn.click()
    print("------> Choosing to login with Email...")
    time.sleep(3)

    # Find the email and password fields and fill them out
    email_field = bot.find_element(By.ID,"email-login-email")
    email_field.send_keys(email)
    print("------> Email inserted...")

    nextBtn = bot.find_element(By.CSS_SELECTOR, "button[data-testid='signup-login-submit-btn']")
    nextBtn.click()

    time.sleep(3)
    password_field = bot.find_element(By.CSS_SELECTOR, "input[data-testid='email-signup-password']")
    password_field.send_keys(password)
    print("------> Password inserted...")

    loginBtn = bot.find_element(By.CSS_SELECTOR, "button[data-testid='signup-login-submit-btn']")
    loginBtn.click()

    time.sleep(3)
    try:
        #Handling SMS Verification
        smsCheck = bot.find_element(By.CSS_SELECTOR, "button[class='.l1j9v1wn.bbkw4bl.c1rxa9od.dir.dir-ltr']")
        smsCheck.click()
        print("------> Waiting for the user input. Please provide the sms code you've received...")
        smsCode = input("6-Digits SMS Code:")
        firstDigit = bot.find_element(By.CSS_SELECTOR, "input[id='airlock-code-input_codeinput_0']")
        firstDigit.send_keys(smsCode[0])
        secondDigit = bot.find_element(By.CSS_SELECTOR, "input[id='airlock-code-input_codeinput_1']")
        secondDigit.send_keys(smsCode[1])
        thirdDigit = bot.find_element(By.CSS_SELECTOR, "input[id='airlock-code-input_codeinput_2']")
        thirdDigit.send_keys(smsCode[2])
        fourthDigit = bot.find_element(By.CSS_SELECTOR, "input[id='airlock-code-input_codeinput_3']")
        fourthDigit.send_keys(smsCode[3])
        fifthDigit = bot.find_element(By.CSS_SELECTOR, "input[id='airlock-code-input_codeinput_4']")
        fifthDigit.send_keys(smsCode[4])
        sixthDigit = bot.find_element(By.CSS_SELECTOR, "input[id='airlock-code-input_codeinput_5']")
        sixthDigit.send_keys(smsCode[5])
    except NoSuchElementException:
        print("------> No SMS verification...")
    print("------> Logged In...")
except NoSuchElementException:
    print("------> Email or password input not found, continuing with scrapping the reservations information...")

# Wait for the page to load
time.sleep(5)

# Create a BeautifulSoup object from the response content
page_source = bot.page_source
soup = BeautifulSoup(page_source, 'lxml')

print("------> Extracting the Guest Name, Room Title, Check in and Check out dates from each reservation...")
guest_names=[]
check_ins= []
check_outs=[]
room_titles=[]
for guest_name in soup.find_all("a", {"class": "l1j9v1wn b1yf7320 c1uxatsa dir dir-ltr"}):
    guest_names.append(guest_name.text)

tds= soup.find_all("td", {"class": "_qjegjiv"})

i=0
for i in range(len(tds)):

    if(i==0):
        checkin = tds[i+2].text
        check_ins.append(checkin)
        checkout = tds[i+3].text
        check_outs.append(checkout)
        room_title = tds[i+5].text
        room_titles.append(room_title)
    else:
        i=i+(7*i)
        if(i == len(tds) or i > len(tds)):
            break
        checkin = tds[i+2].text
        check_ins.append(checkin)
        checkout = tds[i+3].text
        check_outs.append(checkout)
        room_title = tds[i+5].text
        room_titles.append(room_title)

time.sleep(5)
print("------> Connecting to Google Calendar...")
def get_calendar_service(credentials_path, SCOPES):
   creds = None
   # The file token.json stores the user's access and refresh tokens, and is
   # created automatically when the authorization flow completes for the first
   # time.
   if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
   # If there are no (valid) credentials available, let the user log in.
   if not creds or not creds.valid:
       if creds and creds.expired and creds.refresh_token:
           creds.refresh(Request())
       else:
           flow = InstalledAppFlow.from_client_secrets_file(
               credentials_path, SCOPES)
           creds = flow.run_local_server(port=0)

       # Save the credentials for the next run
       with open('token.json', 'w') as token:
           token.write(creds.to_json())

   service = build('calendar', 'v3', credentials=creds)
   return service

"""Adds booking events to Google Calendar using the given credentials."""
# Load the Google API credentials
service = get_calendar_service(GOOGLE_CREDENTIALS_FILE, SCOPES)

# Create a batch request object
batch = BatchHttpRequest()

for j in range(len(guest_names)):
    print("\033[1;31;40m ------> Creating Google Calendar Event...")
    # Create the Google Calendar event
    datetime_obj_in = datetime.strptime(str(check_ins[j]), "%b %d, %Y")
    checkinDate = datetime_obj_in.strftime("%Y-%m-%d")
    # Create the Google Calendar event
    datetime_obj_out = datetime.strptime(str(check_outs[j]), "%b %d, %Y")
    checkoutDate = datetime_obj_out.strftime("%Y-%m-%d")

    checkinFormat= datetime.strptime(str(checkinDate)+"T15:00:00", "%Y-%m-%dT%H:%M:%S")
    checkoutFormat= datetime.strptime(str(checkoutDate)+"T11:00:00", "%Y-%m-%dT%H:%M:%S")
    try:
        event = service.events().insert(calendarId='primary',
            body={
            'summary': 'Airbnb Reservation - ' +room_titles[j].lstrip().capitalize(),
            'description': guest_names[j].lstrip(),
            'start': {
                'dateTime': checkinFormat.isoformat(),
                'timeZone': 'Europe/Zagreb',
            },
            'end': {
                'dateTime': checkoutFormat.isoformat(),
                'timeZone': 'Europe/Zagreb',
            },
            'colorId': '2',
            'reminders': {
                'useDefault': True,
            },
        }).execute()
        print('------> EVENT SUMMARY \n')
        print('------> Guest Name: '+ guest_names[j].lstrip() +' \n')
        print('------> Room Title: '+room_titles[j].lstrip().capitalize()+' \n')
        print('------> Check-In Date: '+checkinFormat+' \n')
        print('------> Check-Out Date: '+checkoutFormat+' \n')
        print('------> Event created successfully. Google Calendar has been updated!')
    except HttpError as error:
        print('An error occurred: %s' % error)

#function to fetch all the upcoming event from Google Calendar
def fetch(GOOGLE_CREDENTIALS_FILE, SCOPES):
   service = get_calendar_service(GOOGLE_CREDENTIALS_FILE, SCOPES)
   # Call the Calendar API
   now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
   print('Getting List o 10 events')
   events_result = service.events().list(
       calendarId='primary', timeMin=now,
       maxResults=10, singleEvents=True,
       orderBy='startTime').execute()
   events = events_result.get('items', [])

   if not events:
       print('No upcoming events found.')
   for event in events:
       start = event['start'].get('dateTime', event['start'].get('date'))
       print(start, event['summary'])

fetch(GOOGLE_CREDENTIALS_FILE, SCOPES)

# Close the browser
bot.quit()
