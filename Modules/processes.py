#!/usr/bin/env python

import requests
import urllib.parse
from pprint import pprint
import Modules.variables as variables
import Modules.ado_details as tools

auth = tools.get_authentication()

def get_process_id_by_name(process_name):
    # Construct the API endpoint URL to list all processes
    url = '%s?%s' % (variables.PROCESS_URL % process, variables.API_VERSION)
    # Set the request headers and authentication
    headers = {
        "Content-Type": "application/json"
    }
    # Send the GET request to the API endpoint
    response = requests.get(url, headers=headers, auth=auth)
    # Check if the request was successful
    if response.status_code == 200:
        # Get the JSON response data
        processes = response.json()['value']
        # Find the process with the matching name
        for process in processes:
            if process['name'] == process_name:
                return process['id']
        # If no matching process is found
        print("Process not found: " + process_name)
        return None
    else:
        # Print the error message
        print("URL: " + url)
        print("Error: " + response.text)
        return None

def list_work_item_types(process):
    # Construct the API endpoint URL
    url = '%s?%s' % (variables.PROCESS_URL % process, variables.API_VERSION)
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
        print("URL: " + url)
        print("Error: " + response.text)


def list_work_item_type_details(process, work_item_type):
    # Construct the API endpoint URL
    encoded_process = urllib.parse.quote(process)
    url = '%s/%s?%s' % (variables.PROCESS_URL % encoded_process, work_item_type, variables.API_VERSION)
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
        print("URL: " + url)
        print("Error: " + response.text)


def update_work_item_type(process_name, work_item_type, element, values_list):
    # Construct the API endpoint URL
    url = '%s?%s' % (variables.PROCESS_URL % process, variables.API_VERSION)
    # Set the request headers and authentication
    headers = {
        "Content-Type": "application/json-patch+json"
    }
    # Construct the update data payload
    update_data = [
        {
            "op": "add",
            "path": "/%s" % element,
            "value": values_list
        }
    ]
    # Send the PATCH request to the API endpoint
    response = requests.patch(url, json=update_data, headers=headers, auth=auth)
    # Check if the request was successful
    if response.status_code == 200:
        # Print the JSON response data
        pprint(response.json())
    else:
        # Print the error message
        print("Error: " + response.text)

