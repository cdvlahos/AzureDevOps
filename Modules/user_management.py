#!/usr/bin/env python
import subprocess
import Modules.variables as variables
import Modules.ado_details as tools
import os
import json
from pprint import pprint

def remove_user(user_email):

    # Replace with your Azure DevOps organization URL, personal access token, and the email address of the user to remove
    items = tools.get_secrets()
    personal_access_token = items['{ORG_ID}']['password']

    # Get the Azure DevOps user descriptor for the user to remove
    get_user_descriptor_command = f"az devops user show --email-id {user_email} --organization {variables.NEW_VCS_ROOT} --detect false --query descriptor --output tsv"
    user_descriptor = subprocess.run(get_user_descriptor_command, shell=True, stdout=subprocess.PIPE).stdout.decode().strip()

    if user_descriptor:
        # Remove the user from the organization
        remove_user_command = f"az devops user remove --id {user_descriptor} --org {variables.NEW_VCS_ROOT} --yes"
        subprocess.run(remove_user_command, shell=True)
        print("User %s removed from the organization." % user_email)
    else:
        print("User not found in the organization.")

def find_user(user_email):
    # Get the Azure DevOps user descriptor for the user to remove

    # Get the Azure DevOps user descriptor for the user to remove
    get_user_descriptor_command = f"az devops user show --user {user_email} --organization {variables.NEW_VCS_ROOT} --output json"
    user_descriptor = subprocess.run(get_user_descriptor_command, shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
    # convert string to JSON
    json_data = json.loads(user_descriptor)
    if user_descriptor:
        pprint(json_data["user"])
    else:
        print("There is no user %s in the Azure DevOPs org" % user_email)
