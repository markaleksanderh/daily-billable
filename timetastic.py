from __main__ import app
import requests
from requests.structures import CaseInsensitiveDict
from models import db, Employee
from os import environ as env

TIMETASTIC_TOKEN = env.get('TIMETASTIC_TOKEN')

def get_absences(date):
    """
    Request absences from TimeTastic and return holidays filtered according to leave types
    Ignore 'Working in Office' type
    """
    url = f"https://app.timetastic.co.uk/api/holidays?Start={date}&End={date}"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = f"Bearer {TIMETASTIC_TOKEN}"
    absences = requests.get(url, headers=headers).json()['holidays']
    return absences


def add_absences(absences):
    for a in absences:
        employee = Employee.query.filter_by(name=a['userName']).first()
        if employee is not None:
            employee.absence = a['leaveType']
            db.session.add(employee)
            db.session.commit()