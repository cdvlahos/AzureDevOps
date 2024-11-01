#!/usr/bin/env python
import requests
import Modules.variables as variables
import time
from Modules.hooks import create_hooks
from Modules.hooks import create_crn
import Modules.ado_details as tools
from pprint import pprint

def create_project(name, subscriptions, desc='', process='PROCESS_NAME', nohook=False):
    # create action requires name, and optional description and nohook flag
    data = {"capabilities": {"versioncontrol": {"sourceControlType": "Git"}}}
    processId = tools.get_process_id_from_name(process)
    if processId is None:
        print("Error: Could not find process %s" % process)
        return False
    data['name'] = name
    data['description'] = desc
    data['capabilities']['processTemplate'] = {"templateTypeId": processId}
    try:
        auth, HEADERS = tools.get_authentication()
        r = requests.post('%s?%s' % (variables.PROJECT_URL, variables.API_VERSION), json=data, headers=HEADERS)
        r.raise_for_status()
        j = r.json()
        # We need to wait for status of "succeeded"
        # Before we can add the service hook
        print('Creation sent, waiting for completion')
        while j['status'] == 'notSet' or j['status'] == 'inProgress':
            # I hate sleep, but what can we do in a polling methodology
            time.sleep(2)
            r = requests.get(j['url'], headers=HEADERS)
            r.raise_for_status()
            j = r.json()

        print('Done')
        if j['status'] != 'succeeded':
            print(r.text)
        else:
            # The API doesn't give you the projectID of the project in
            # any JSON results, so once it's done, we need to get it
            pid = tools.get_project_id_from_name(name)
            print('Project %s with id %s successfully created' % (name, pid))
            if nohook is False:
                # Create VSTS hook as well
                return create_hooks(name, subscriptions)
            else:
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

def create_team(name, project, desc=''):
    # create action requires name, and optional description
    data = {}
    data['name'] = name
    data['description'] = desc
    try:
        auth, HEADERS = tools.get_authentication()
        r = requests.post('%s/%s/teams?%s' % (variables.PROJECT_URL, project, variables.API_VERSION), json=data, headers=HEADERS)
        r.raise_for_status()
        j = r.json()

        print('Team %s in project %s successfully created' % (name, project))

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


def delete_project(name):
    pid = tools.get_project_id_from_name(name)
    if pid is None:
        print('Project %s does not exist.' % name)
        return False
    else:
        try:
            auth, HEADERS = tools.get_authentication()
            r = requests.delete('%s%s?%s' % (variables.PROJECT_URL, pid, variables.API_VERSION), headers=HEADERS)
            r.raise_for_status()
            print('Successfully deleted project %s:%s' % (name, pid))
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

def get_project(name):
    pid = tools.get_project_id_from_name(name)
    if pid is None:
        print('Project %s does not exist.' % name)
        return False
    else:
        try:
            auth, HEADERS = tools.get_authentication()
            r = requests.get('%s%s?%s' % (variables.PROJECT_URL, pid, variables.API_VERSION), header=HEADERS)
            r.raise_for_status()
            # Really nothing useful here to parse, so just dump it out
            print(r.text)
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

def list_project():
    auth, HEADERS = tools.get_authentication()
    try:
        r = requests.get('%s?%s' % (variables.PROJECT_URL, variables.API_VERSION),headers=HEADERS)
        r.raise_for_status()
        j = r.json()
        # Really nothing useful here to parse, so just dump it out
        pprint(j)
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

def get_projects():
    auth, HEADERS = tools.get_authentication()
    try:
        r = requests.get('%s?%s' % (variables.PROJECT_URL, variables.API_VERSION),headers=HEADERS)
        r.raise_for_status()
        data = r.json()

        # Get the list of all project names
        project_names = [project['name'] for project in data['value']]
        return project_names

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

def update_project(name, desc, process, crn=False):
    if crn:
        create_crn(name)
    if not desc == "":
        print("Implement ability to update project description")
    if not process == "":
        print("Implement ability to change project process")

def rename_project(name, new_name):
    # Not implemented yet - needs PATCH
    # https://www.visualstudio.com/en-us/docs/integrate/api/tfs/projects#update-a-team-project
    return False

