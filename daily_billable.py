from dotenv import dotenv_values
import requests
from requests.structures import CaseInsensitiveDict
from tabulate import tabulate

config = dotenv_values(".env")

# Valid leave types - ignore working from office:
# Sick Leave
# Holiday
# Maternity
leave_types = {"Sick Leave", "Holiday", "Maternity"}

# Fix with regex
date = input("Enter date in YYYY-MM-DD format:\n")

# Request absences from TimeTastic and return holidays filtered according to leave types
def get_absences(date):
    url = "https://app.timetastic.co.uk/api/holidays?Start={}&End={}".format(date, date)
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer {}".format(config['TIMETASTIC_TOKEN'])
    absences = requests.get(url, headers=headers).json()['holidays']
    valid_absences = [[i['userName'], i['startDateString'], i['endDateString'], i['leaveType']] for i in absences if i['leaveType'] in leave_types]
    return valid_absences    

absences = get_absences(date)

print(tabulate(absences, headers=["Name", "Start Date", "End Date", "Leave Type"]))



