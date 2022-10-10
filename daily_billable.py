from dotenv import dotenv_values
import requests
from requests.structures import CaseInsensitiveDict
from tabulate import tabulate
import sqlite3
from sqlite3 import Error
import os

config = dotenv_values(".env")

def create_connection(db_file):
    """
    Create DB and return connection
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """
    Create table in database
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def get_team(file):
    """
    Load team member names from text file
    """
    with open(file) as f:
        contents = f.readlines()
        team = [line.strip() for line in contents]
    return team

def create_team(conn, team_member_name):
    """
    Add team member to db
    """
    cur = conn.cursor()
    cur.execute('INSERT INTO team VALUES(?,?,?,?,?,?,?,?)', (None, team_member_name, "", "", "", 0, 0, 0))
    conn.commit()
    return cur.lastrowid

def add_all_team(team_list, conn):
    """
    Iterate through list of team and add to db
    """
    for i in team_list:
        create_team(conn, i)
    pass

def get_user_date():
    """
    Get date from user in YYYY-MM-DD format
    """
    date = input("Enter date in YYYY-MM-DD format:\n")
    return date

def get_absences(date):
    """
    Request absences from TimeTastic and return holidays filtered according to leave types
    Ignore 'Working in Office' type
    """
    url = "https://app.timetastic.co.uk/api/holidays?Start={}&End={}".format(date, date)
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer {}".format(config['TIMETASTIC_TOKEN'])
    absences = requests.get(url, headers=headers).json()['holidays']
    valid_absences = [[i['userName'], i['startDateString'], i['endDateString'], i['leaveType']] for i in absences if i['leaveType'] != "Working in Office"]
    return valid_absences
    
def update_absence(conn, absence):
    """
    Select by name and update absence start date, absence end date and absence type
    """
    cur = conn.cursor()
    sql = ''' UPDATE team
              SET absence_start_date = ? ,
                  absence_end_date = ? ,
                  absence_type = ? 
              WHERE name = ? '''
    cur.execute(sql, (absence[1], absence[2], absence[3], absence[0]))    
    conn.commit()
    return cur.lastrowid

def update_all_absences(absence_list, conn):
    for i in absence_list:
        update_absence(conn, i)
    pass

def get_tracked(date):
    """
    Request hours from Harvest and return billable and non-billable hours
    """
    url = "https://api.harvestapp.com/api/v2/time_entries?from={}&to={}".format(date, date)
    headers = {
        "Authorization" : "Bearer {}".format(config['HARVEST_TOKEN']),
        "Harvest-Account-Id": "{}".format(config['HARVEST_ACCOUNT_ID']),
        "User-Agent": "Harvest API Example",
    }

    tracked = requests.get(url, headers=headers).json()['time_entries']
    tracked_hour_entries = [[i['user']['name'], i['hours'], i['billable']] for i in tracked]
    return tracked_hour_entries

def update_hour(conn, tracked_hour_entry):
    """
    Check if billable or not
    Add to existing value
    """
    if tracked_hour_entry[2] == True:
        sql = ''' UPDATE team
                SET hours = hours + ? ,
                    billable_hours = billable_hours + ? 
                WHERE name = ? '''
        cur = conn.cursor()
        cur.execute(sql, (tracked_hour_entry[1], tracked_hour_entry[1], tracked_hour_entry[0],)) 
        conn.commit()
        return cur.lastrowid
    elif tracked_hour_entry[2] == False:
        sql = ''' UPDATE team
                SET hours = hours + ? ,
                    non_billable_hours = non_billable_hours + ? 
                WHERE name = ? '''
        cur = conn.cursor()
        cur.execute(sql, (tracked_hour_entry[1], tracked_hour_entry[1], tracked_hour_entry[0],))           
        conn.commit()
        return cur.lastrowid

def update_all_hours(conn, tracked_hour_entries):
    """
    Iterate through tracked hours and set billable and non-billable columns according to tracked hour type
    """
    for i in tracked_hour_entries:
        update_hour(conn, i)
    pass

def get_missing_entries():
    """"
    Get all 
    """
    pass

# def display_table(conn):
#     with conn:
#         cur = conn.cursor()
#         cur.execute("SELECT * FROM team")
#         print(cur.fetchall())


def main():
    os.remove('daily_billable.db')
    # database = ':memory:'
    database = 'daily_billable.db'
    sql_create_team_table = """ CREATE TABLE IF NOT EXISTS team (
        id integer PRIMARY KEY,
        name text NOT NULL,
        absence_start_date text,
        absence_end_date text,
        absence_type text,
        hours integer,
        billable_hours integer,
        non_billable_hours integer
        ); """
    conn = create_connection(database)
    if conn is not None:
        create_table(conn, sql_create_team_table)
    else:
        print("Cannot create db connection")

    team_file = 'team.txt'
    team = get_team(team_file)
    add_all_team(team, conn)
    selected_date = "2022-10-07"
    absence_list = get_absences(selected_date)
    update_all_absences(absence_list, conn)
    tracked_hour_entries = get_tracked(selected_date)
    update_all_hours(conn, tracked_hour_entries)
    


if __name__ == '__main__':
    main()
