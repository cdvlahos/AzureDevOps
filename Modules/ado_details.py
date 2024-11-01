#!/usr/bin/env python

import base64
import os
import requests
import Modules.variables as variables
import json
from azure.devops.connection import Connection  
from msrest.authentication import BasicAuthentication  
from azure.devops.v7_1.service_hooks.service_hooks_client import ServiceHooksClient  
from pprint import pprint

def get_project_id_from_name(name):
    try:
        auth, HEADERS = get_authentication()
        url = '%s%s?%s' % (variables.PROJECT_URL, name, variables.API_VERSION)
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        return r.json()['id']
    except:
        return None
    
def get_process_id_from_name(name):
    try:
        auth, HEADERS = get_authentication()
        print(variables.PROCESS_URL)
        r = requests.get(variables.PROCESS_URL, headers=HEADERS)
        r.raise_for_status()
        j = r.json()
        for p in j['value']:
            if p['name'] == name:
                return p['id']
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

    return None

def get_project_id():
    auth, HEADERS = get_authentication()
    try:
        r = requests.get('%s?%s' % (variables.PROJECT_URL, variables.API_VERSION), auth=get_authentication())
        r.raise_for_status()
        # Really nothing useful here to parse, so just dump it out
        return json.loads(r.text)
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

def get_secrets():
    with open(os.path.expanduser('~')+'/.vsts.json', 'r') as file:
        items = json.load(file)

    return items

def get_authentication():
    items = get_secrets()
    PERSONAL_AUTHENTICATION_TOKEN = items['ADO_PASSWORD']
    USERNAME = ""
    USER_PASS = USERNAME + ":" + PERSONAL_AUTHENTICATION_TOKEN
    B64USERPASS = base64.b64encode(USER_PASS.encode()).decode()
    auth = (variables.USERNAME, B64USERPASS)

    HEADERS = {
    'Authorization': 'Basic %s' % B64USERPASS
    }

    return auth,HEADERS

def get_hookClient():
    items = get_secrets()

    # Set up the connection to the Azure DevOps organization  
    personal_access_token = items['ADO_PASSWORD']
    organization_url = variables.NEW_VCS_ROOT
    credentials = BasicAuthentication('', personal_access_token)  
    connection = Connection(base_url=organization_url, creds=credentials) 

    # Set up the Service Hooks client  
    client = ServiceHooksClient(base_url=organization_url, creds=credentials)   

    return client

def get_userClient():
    items = get_secrets()

    # Set up the connection to the Azure DevOps organization  
    personal_access_token = items['ADO_PASSWORD']
    organization_url = variables.NEW_VCS_ROOT
    credentials = BasicAuthentication('', personal_access_token)  
    connection = Connection(base_url=organization_url, creds=credentials) 

    # Get the GraphClient for the organization  
    graph_client = connection.clients.get_graph_client()  

    return graph_client
