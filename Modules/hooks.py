#!/usr/bin/env python
import requests
import Modules.variables as variables
import Modules.ado_details as tools
import os
import json
from pprint import pprint

# Get the PAT auth for request authentication
auth = tools.get_authentication()

def delete_old_hooks():
    try:
        config=os.path.abspath(os.path.join(os.getenv('HOME'), '.vsts.json'))
        with open(config, 'r') as f:
            configObj = json.load(f)

        for hook in get_subscriptions():
            if hook.action_description=="Topic codepush":
                url = '%s/%s?%s' % (variables.HOOKS_URL % "", hook.id, variables.API_VERSION)
                auth, HEADERS = tools.get_authentication()
                r = requests.delete(url, headers=HEADERS)
                r.raise_for_status()
                print('Deleted hook %s' % hook.id)

    except requests.exceptions.HTTPError:
        print('HTTP Code: %d\n%s' % (r.status_code, r.text))
        exit(1)
    except ValueError:
        print('Failed to parse resulting JSON')
        print('HTTP Code: %d\n%s' % (r.status_code, r.text))
        exit(1)

# Will find all hooks owned by "owner" and do a "fake" update
# to take ownership
# We should run this on each user that leaves the company to
# ensure we take ownership of their hooks
def takeown_hook(owner):
    try:
        config=os.path.abspath(os.path.join(os.getenv('HOME'), '.vsts.json'))
        with open(config, 'r') as f:
            configObj = json.load(f)

        for hook in get_subscriptions():
            if hook.modified_by.unique_name == owner:
                print("Found %s as owner of hook %s" % (owner, hook.id))
                # Set the request body
                # Print the values and attributes of the object

                attributes = ["created_by", "modified_by", "created_date", "modified_date", "_links"]
                data = {}
                for attribute, value in hook.__dict__.items():
                    if not attribute in attributes:
                        if attribute == "action_description":
                            data["actionDescription"] = value
                        elif attribute == 'consumer_action_id':
                            data["consumerActionId"] = value
                        elif attribute == 'consumer_id':
                            data["consumerId"] = value
                        elif attribute == 'consumer_inputs':
                            data["consumerInputs"] = value
                            if 'connectionString' in value:
                                data["consumerInputs"]["connectionString"] = configObj['{ORG_ID}']['servicebus_sender']
                        elif attribute == 'event_description':
                            data["eventDescription"] = value
                        elif attribute == 'event_type':
                            data["eventType"] = value
                        elif attribute == 'id':
                            data["id"] = value
                        elif attribute == 'probation_retries':
                            data["probationRetries"] = value
                        elif attribute == 'publisher_id':
                            data["publisherId"] = value
                        elif attribute == 'consumer_inputs':
                            data["consumerInputs"] = value
                        elif attribute == 'publisher_inputs':
                            data["publisherInputs"] = value
                        elif attribute == 'resource_version':
                            data["resourceVersion"] = value
                        elif attribute == 'status':
                            data["status"] = value
                        elif attribute == 'subscriber':
                            data["subscriber"] = value
                        elif attribute == 'url':
                            data["url"] = value

                print(data)
                url = '%s?%s' % (variables.HOOKS_URL % "", variables.API_VERSION)
                auth, HEADERS = tools.get_authentication()
                r = requests.put(url, json=data, headers=HEADERS)
                r.raise_for_status()
                print('Changed ownership of %s from %s' % (hook.id, hook.modified_by.unique_name))

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

def list_hooks(name):

    pid = tools.get_project_id_from_name(name)

    # Print the service hooks
    for hook in get_subscriptions():
        # Print the values and attributes of the object
        if hook.publisher_inputs.get('projectId') == pid:
            print()
            if hook.consumer_inputs:
                print("Consumer inputs: " + str(hook.consumer_inputs))
            if hook.event_description:
               print("event description: " + hook.event_description)
            if hook.publisher_inputs:
                print("publisher_inputs: " + str(hook.publisher_inputs))
            if hook.event_type:
                print("event type: " + hook.event_type)
            if hook.action_description:
                print("action description: " + hook.action_description)
            if hook.modified_by:
                print("Modifed By: " + hook.modified_by.unique_name)

def hook_exists(pid, subscriptions, newHook):

    gitType = ["git.push", "git.pullrequest.updated", "git.pullrequest.created"]
    actionDescription = ["Teamcity notification on code push", "Teamcity notification on PR created", "Teamcity notification on PR updated"]

    # Print the service hooks
    for hook in subscriptions:
        projectId = hook.publisher_inputs.get('projectId')
        if projectId == pid:
            # check for bug/issue service hooks
            if "workItemType" in newHook["publisherInputs"]:
                if hook.event_description == newHook["eventDescription"]:
                    return True

            # check for git hooks
            elif hook.action_description in actionDescription and hook.event_type == newHook["eventType"]:
                return True

    return False

def get_subscriptions():
    # Get the subscriptions that match the query
    subscriptions_client = tools.get_hookClient()
    subscriptions = subscriptions_client.list_subscriptions()
    return subscriptions

def create_hooks(name, subscriptions):
    create_git(name, subscriptions)
    create_crn(name)

def create_git(name, subscriptions):
    # FIXME: There is no code in here yet that will validate if the hook exists
    #        already.  Should try to find one, or it'll add subsequent ones!
    try:
        config=os.path.abspath(os.path.join(os.getenv('HOME'), '.vsts.json'))
        with open(config, 'r') as f:
            configObj = json.load(f)

        cwd = os.getcwd()
        with open(os.path.join(cwd, 'serviceHooks', 'git_hooks.json'), 'r') as f:
            gitData = json.load(f)

        print('Creating GIT hooks for project %s' % name)

        pid = tools.get_project_id_from_name(name)

        data = []
        for item in gitData:
            item['publisherInputs'] = {
                "projectId": pid
            }
            item['consumerInputs'] = {
                "url": "https://{URL_TO_VCPOLLING_LAMBDA}.com/push",
                "httpHeaders": configObj['{ORG_ID}']['httpHeaders']  # get httpHeaders from .vsts.json
            }
            data.append(item)

        for hook in data:
            exists = hook_exists(pid, subscriptions, hook)


            if exists:
                print("hook for %s already exists" % hook["eventType"])
                print()
            else:
                auth, HEADERS = tools.get_authentication()
                print("Creating %s hook for project %s" % (hook["eventType"], name))
                # Create VSTS hook
                url = '%s?%s' % (variables.HOOKS_URL % "", variables.API_VERSION)
                r = requests.post(url, headers=HEADERS, json=hook)
                r.raise_for_status()
                print('Git hooks successfully created')
                print()

    except requests.exceptions.HTTPError:
        print('HTTP Code: %d\n%s' % (r.status_code, r.text))
        exit(1)
    except ValueError:
        print('Failed to parse resulting JSON')
        print('HTTP Code: %d\n%s' % (r.status_code, r.text))
        exit(1)

def create_crn(name):
    # FIXME: There is no code in here yet that will validate if the hook exists
    #        already.  Should try to find one, or it'll add subsequent ones!
    try:
        config=os.path.abspath(os.path.join(os.getenv('HOME'), '.vsts.json'))
        with open(config, 'r') as f:
            configObj = json.load(f)

        cwd = os.getcwd()

        # get all the Bug and issue CRN hooks
        with open(os.path.join(cwd, 'serviceHooks', 'bug_hooks.json'), 'r') as bug, \
             open(os.path.join(cwd, 'serviceHooks', 'issue_hooks.json'), 'r') as issue:
            bugData = json.load(bug)
            issueData = json.load(issue)

        print('Creating CRN hooks for project %s' % name)

        # Create crn hooks for given project
        pid = tools.get_project_id_from_name(name)
        data = []
        for item in bugData:
            item['publisherInputs']["projectId"] = pid
            item['consumerInputs'] = {"queueName": "crn_calculations", "connectionString": configObj['crnkey']}
            data.append(item)

        if "external" not in name:
            for item in issueData:
                item['publisherInputs']["projectId"] = pid
                item['consumerInputs'] = {"queueName": "crn_calculations", "connectionString": configObj['crnkey']}
                data.append(item)

        for hook in data:
            exists = hook_exists(pid, get_subscriptions(), hook)

            if exists:
                print("hook for %s already exists" % hook["eventDescription"])
                print()
            else:
                print("Creating %s hook for project %s" % (hook["eventDescription"], name))
                # Create VSTS hook
                auth, HEADERS = tools.get_authentication()
                url = '%s?%s' % (variables.HOOKS_URL % "", variables.API_VERSION)
                r = requests.post(url, json=hook, headers=HEADERS)
                r.raise_for_status()
                print('%s hook successfully created in project %s' % (hook["eventDescription"], name))
                print()

    except requests.exceptions.HTTPError:
        print('HTTP Code: %d\n%s' % (r.status_code, r.text))
        exit(1)
    except ValueError:
        print('Failed to parse resulting JSON')
        print('HTTP Code: %d\n%s' % (r.status_code, r.text))
        exit(1)