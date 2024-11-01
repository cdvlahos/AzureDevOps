#!/usr/bin/env python

import requests
import base64
import json
import argparse
from argparse import RawTextHelpFormatter
import os
from datetime import datetime, timedelta
from pprint import pprint

# return the json file containing the password info
def get_config_data(file):
    with open(file) as data_file:
        data = json.load(data_file)
    return data

def get_username_password():
    secrets = get_config_data(os.path.abspath(os.path.join(os.getenv('HOME'), '.gate_keeper.json')))

    # get secret information for azure and vsts, trying env vars first
    ado_username = os.getenv('ADO_USERNAME', None)
    ado_password = os.getenv('ADO_PASSWORD', None)

    if ado_password is None:
        ado_password = secrets.get('AZ_PASS', None)

    if ado_username is None:
        ado_username = secrets.get('AZ_USER', None)

    if ado_username is None:
        print("ERROR: Missing json AZ_USER parameter & ADO_USERNAME environment variable")
        exit(1)

    if ado_password is None:
        print("ERROR: Missing json AZ_PASS parameter & ADO_PASSWORD environment variable")
        exit(1)

    return ado_username, ado_password

def create_year(fiscal, user, password):
    url = f"https://dev.azure.com/{ORG_ID}/DevOps/_apis/wit/classificationnodes/iterations/DevOps?api-version=6.0"

    data = {
        "name": f"{fiscal}"
    }

    response = requests.patch(url, json=data, auth=(user, password), headers={'Content-type': 'application/json-patch+json'})

    return response.json()["id"]


def create_sprint(fiscal, user, password, start_date, sprint_number):
    url = f"https://dev.azure.com/{ORG_ID}/DevOps/_apis/wit/classificationnodes/iterations/{fiscal}?api-version=5.0"

    end_date = start_date + timedelta(days=13)

    # Convert start and finish date from 2024-04-02 00:00:00 to 2024-04-02T00:00:00Z
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")


    data = {
        "attributes": {
            "startDate": f"{start_date}T00:00:00Z",
            "finishDate": f"{end_date}T00:00:00Z"
        },
        "name": f"Sprint {sprint_number}"
    }

    response = requests.post(url, json=data, auth=(user, password))

    return response.json()["identifier"]

def create_work_item(user, password, iteration_id, title, sprint_number):
    work_item_type = 'User Story'
    url = f'https://dev.azure.com/{ORG_ID}/DevOps/_apis/wit/workitems/${work_item_type}?api-version=7.1'

    if user == "Constantine":
        person = "Constantine Vlahos"
    elif user == "Sai":
        person = "Sai Manasa Goka"
    elif user == "Marc":
        person = "Marc Chatel"
    elif user == "Sreekanth":
        person = "Sreekanth Yasa"
    elif user == "Himanshu":
        person = "Himanshu Bandhu"

    new_data = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": f'{title}'
        },
        {
            "op": "add",
            "path": "/fields/System.IterationPath",
            "value": f"DevOps\\FY25\\Sprint {sprint_number}"
        },
        {
            "op": "add",
            "path": "/fields/System.AssignedTo",
            "value": f"{person}"
        },
        {
            "op": "add",
            "path": "/fields/System.Description",
            "value": "Used to track unplanned work"
        }
    ]

    data = json.dumps(new_data)

    response = requests.post(url, json=new_data, headers={'Content-Type': 'application/json-patch+json'}, auth=(user, password))
    #pprint(response.json())

    return response.json()

def add_sprint_to_team(fiscal, user, password, iteration_id, team_id):
    # Set team_name to DevOps Team
    team_name = "DevOps Team"

    url = f"https://dev.azure.com/{ORG_ID}/DevOps/{team_id}/_apis/work/teamsettings/iterations?api-version=7.1"

    data = {
        "id": iteration_id
    }

    response = requests.post(url, json=data, auth=(user, password))


def get_team_id(user, password):
    url = f"https://dev.azure.com/{ORG_ID}/_apis/projects/DevOps/teams?api-version=7.1-preview.3"

    response = requests.get(url, auth=(user, password))

    return response.json()["value"][0]["id"]

def get_fiscal_start(year):
    d = datetime(int(year), 4, 1)
    offset = 1-d.weekday() #weekday = 1 means tuesday
    if offset < 0:
        offset+=7
    return d+timedelta(offset)

def main(args):
    # get the username and password
    username, password = get_username_password()
    users=["Users", "To", "Create", "Iterations", "For"]

    team_id = get_team_id(username, password)

    # get first Tuesday of April
    start_date = get_fiscal_start(args.year)

    # check if start_sprint is set
    if args.start_sprint:
        sprint_number=int(args.start_sprint)
    else:
        sprint_number=1

    i=1

    # create sprints between Sprint number and 27 if start_date is less than 365 days from start_date
    for i in range(1, 27):
        if start_date > get_fiscal_start(int(args.year)+1):
            break

        if i < sprint_number:
            start_date = start_date + timedelta(weeks=2)
            i += 1
            continue

        it_id = create_sprint(args.fiscal, username, password, start_date, sprint_number)

        for user in users:
            title = f"{user} DevOps - Unplanned Sprint {sprint_number}"
            create_work_item(username, password, it_id, title, sprint_number)

            title = f"{user} User Driven - unplanned Sprint {sprint_number}"
            create_work_item(username, password, it_id, title, sprint_number)


        add_sprint_to_team(args.fiscal, username, password, it_id, team_id)
        start_date = start_date + timedelta(weeks=2)
        sprint_number += 1
        i += 1

if __name__ == "__main__":
    des = '''
    This is designed to create all the sprints for a given fiscal year. It will create the sprints for the fiscal year
    '''
    # Initialize the parser and request account-ID to work with. By default will use all accounts.
    parser = argparse.ArgumentParser(description=des, formatter_class=RawTextHelpFormatter)
    parser.add_argument('--year', dest='year', help='Enter which year ex 2024')
    parser.add_argument('--fiscal', dest='fiscal', help='Enter which fiscal year ex FY25')
    parser.add_argument('--start_sprint', dest='start_sprint', help='Enter the number for which sprint to start at')

    args = parser.parse_args()

    main(args)
