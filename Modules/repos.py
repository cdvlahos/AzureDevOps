#!/usr/bin/env python

import requests
from pprint import pprint
import Modules.variables as variables
import Modules.ado_details as tools

auth = tools.get_authentication()

def get_repository(project, name):
    # Construct the API endpoint URL
    url = '%s/%s/?%s' % (variables.REPOSITORY_URL % project, name, variables.API_VERSION)

    # Set the request headers and authentication
    headers = {
        "Content-Type": "application/json"
    }

    # Send the GET request to the API endpoint
    response = requests.get(url, headers=headers, auth=auth)

    # Check if the request was successful
    if response.status_code == 200:
        # Print the JSON response data
        pprint(response.json())
    else:
        # Print the error message
        print("Error: " + response.text)

def list_repositories(project):
    # Construct the API endpoint URL
    url = '%s?%s' % (variables.REPOSITORY_URL % project, variables.API_VERSION)

    # Set the request headers and authentication
    headers = {
        "Content-Type": "application/json"
    }

    # Send the GET request to the API endpoint
    response = requests.get(url, headers=headers, auth=auth)

    # Check if the request was successful
    if response.status_code == 200:
        # Print the JSON response data
        pprint(response.json())
    else:
        # Print the error message
        print("Error: " + response.text)

def create_repository(project, name):
    pid = tools.get_project_id_from_name(project)
    if pid is None:
        print('Project %s does not exist.' % project)
        return False
    data = {"name": name, "project": {"id": pid}}
    try:
        url = '%s?%s' % (variables.REPOSITORY_URL % project, variables.API_VERSION)
        r = requests.post(url, json=data, auth=auth)
        r.raise_for_status()
        print(r.json()['remoteUrl'])
        return True
    except requests.exceptions.HTTPError:
        j = r.json()
        if 'errorCode' in j:
            # Error occurred - pull out the message
            print(j['message'])
        else:
            print('Failed to parse resulting JSON')
            print('HTTP Code: %d\n%s' % (r.status_code, r.text))
    except ValueError:
        print('Failed to parse resulting JSON')
        print('HTTP Code: %d\n%s' % (r.status_code, r.text))
    return False

def delete_repository(project, name):
    # get the repo ID from project
    pid = tools.get_project_id_from_name(project)
    if pid is None:
        print('Project %s does not exist.' % project)
        return None
    rid = tools.get_repository_id_from_name(pid, name)
    if rid is None:
        print('Repository %s does not exist in project %s.' % (name, project))
        return False
    
    try:
        url = '%s%s?%s' % (variables.REPOSITORY_URL % project, rid, variables.API_VERSION)
        r = requests.delete(url, auth=auth)
        r.raise_for_status()
        print('Successfully deleted repository %s:%s' % (name, rid))
        return True
    except requests.exceptions.HTTPError:
        j = r.json()
        if 'errorCode' in j:
            # Error occurred - pull out the message
            print(j['message'])
        else:
            print('Failed to parse resulting JSON')
            print('HTTP Code: %d\n%s' % (r.status_code, r.text))
    except ValueError:
        print('Failed to parse resulting JSON')
        print('HTTP Code: %d\n%s' % (r.status_code, r.text))
    return False

def restore_deleted(project, name):
    pid = tools.get_project_id_from_name(project)
    if pid is None:
        print('Project %s does not exist.' % project)
        return None
    rid = tools.get_repository_id_from_name(pid, name)
    if rid is None:
        print('Repository %s does not exist in project %s.' % (name, project))
        return False
    try:
        url = '%s%s?%s' % (variables.REPOSITORY_URL % project, rid, variables.API_VERSION)
        r = requests.delete(url, auth=auth)
        r.raise_for_status()
        print('Successfully deleted repository %s:%s' % (name, rid))
        return True
    except requests.exceptions.HTTPError:
        j = r.json()
        if 'errorCode' in j:
            # Error occurred - pull out the message
            print(j['message'])
        else:
            print('Failed to parse resulting JSON')
            print('HTTP Code: %d\n%s' % (r.status_code, r.text))
    except ValueError:
        print('Failed to parse resulting JSON')
        print('HTTP Code: %d\n%s' % (r.status_code, r.text))
    return False

def list_deleted(project):
    try:
        url = variables.PROJECT_REPO_URL % (project, 'recycleBin')
        r = requests.get(url, auth=auth)
        r.raise_for_status()
        # Really nothing useful here to parse, so just dump it out
        pprint(r.text)
        return True
    except requests.exceptions.HTTPError:
        j = r.json()
        if 'errorCode' in j:
            # Error occurred - pull out the message
            print(j['message'])
        else:
            print('Failed to parse resulting JSON')
            print('HTTP Code: %d\n%s' % (r.status_code, r.text))
    except ValueError:
        print('Failed to parse resulting JSON')
        print('HTTP Code: %d\n%s' % (r.status_code, r.text))
    return False

