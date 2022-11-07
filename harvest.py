from __main__ import app
import requests
from requests.structures import CaseInsensitiveDict
from models import db, Employee
from os import environ as env

HARVEST_ACCOUNT_ID = env.get('HARVEST_ACCOUNT_ID')
HARVEST_TOKEN = env.get('HARVEST_TOKEN')

def get_tracked(date, page):
    """
    Request hours from Harvest and return billable and non-billable hours
    """
    url = f"https://api.harvestapp.com/api/v2/time_entries?from={date}&to={date}&page={page}"
    headers = {
        "Authorization" : f"Bearer {HARVEST_TOKEN}",
        "Harvest-Account-Id": f"{HARVEST_ACCOUNT_ID}",
        "User-Agent": "Harvest API Example",
    }
    tracked = requests.get(url, headers=headers).json()

    return tracked['time_entries']


def tracked_length(tracked):
    return len(tracked)


def add_tracked_entries(tracked):
    for t in tracked:

        employee = Employee.query.filter_by(name=t['user']['name']).first()
        if employee is not None:
            if t['billable']:
                employee.billable_hours = employee.billable_hours + t['rounded_hours']
            else:
                employee.non_billable_hours = employee.billable_hours + t['rounded_hours']
            db.session.add(employee)
            db.session.commit()


