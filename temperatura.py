#!/usr/bin/python

import json
import sys
import datetime
import os
import glob
import time
from time import strftime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
temp_sensor = '/sys/bus/w1/devices/28-0000031b9ad4/w1_slave'

GDOCS_OAUTH_JSON       = 'credentials.json'

# Google Docs spreadsheet name.
GDOCS_SPREADSHEET_NAME = 'Temperatura'

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS      = 360

def login_open_sheet(oauth_key_file, spreadsheet):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
        scope =  ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(oauth_key_file, scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open(spreadsheet).sheet1
        return worksheet
    except Exception as ex:
        print('Unable to login and get spreadsheet.  Check OAuth credentials, spreadsheet name, and make sure spreadsheet is shared to the client_email address in the OAuth .json file!')
        print('Google sheet login failed with error:', ex)
        sys.exit(1)
def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
    return temp 

def tempRead():
    t = open(temp_sensor, 'r')
    lines = t.readlines()
    t.close()
 
    temp_output = lines[1].find('t=')
    if temp_output != -1:
        temp_string = lines[1].strip()[temp_output+2:]
        temp_c = float(temp_string)/1000.0
    return round(temp_c,1)


print('Logging sensor measurements to {0} spreadsheet every {1} seconds.'.format(GDOCS_SPREADSHEET_NAME, FREQUENCY_SECONDS))
print('Press Ctrl-C to quit.')
worksheet = None
while True:
    # Login if necessary.
    if worksheet is None:
        worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)

    temp = tempRead()

    if temp is None:
        time.sleep(2)
        continue

    print(datetime.datetime.now().strftime('%Y-%m-%d') +' '+ datetime.datetime.now().strftime('%H:%M'), temp)
    try:
        worksheet.insert_row((datetime.datetime.now().strftime('%Y-%m-%d') +' '+ datetime.datetime.now().strftime('%H:%M'), temp))
    except:
        print('Append error, logging in again')
        worksheet = None
        time.sleep(FREQUENCY_SECONDS)
        continue

    # Wait 30 seconds before continuing
    print('Wrote a row to {0}'.format(GDOCS_SPREADSHEET_NAME))
    time.sleep(FREQUENCY_SECONDS)

