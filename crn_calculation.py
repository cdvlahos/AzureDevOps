#!/usr/bin/env python
from __future__ import division
from azure.servicebus import ServiceBusClient
from azure.servicebus import TransportType
import argparse
from argparse import RawTextHelpFormatter

import requests

import json
import os
import sys
from pprint import pprint


# return the json file containing the password info
def get_config_data(file):
    with open(file) as data_file:
        data = json.load(data_file)
    return data

def get_dict(message):
    head, sep, tail = message.partition('{"id":')
    return sep + tail[:-1]

# after creating a new case in manuscript take the response which include the ID and attach it to the vsts task
# used for both tracking and updating.
def update_crn(crn, id, user, password, debug):
    try:
        url = 'https://{ORG_ID}.visualstudio.com/DefaultCollection/_apis/wit/workitems/' + str(id) + '?api-version=4.1-preview'

        data = [
            {
                "op": "add",
                "path": "/fields/LessonsDesktop.CRNTotal",
                "value": str(crn)
            }
        ]

        response = requests.patch(url, json=data, auth=(user, password), headers={'Content-type': 'application/json-patch+json'})

        if debug:
            print("URL and response to adding CRN total to bug:")
            print(url)
            print(response.reason)
    except:
        print("Bug deleted")


def calculate_crn(CRNExposure,CRNRepro, Severity, debug):
    if CRNExposure == "1":
        crn_exp = 2
    elif CRNExposure == "2":
        crn_exp = 1
    elif CRNExposure == "3":
        crn_exp = 0.5
    else:
        crn_exp = 0.1

    if CRNRepro == "1":
        crn_rep = 2
    elif CRNRepro == "2":
        crn_rep = 1
    elif CRNRepro == "3":
        crn_rep = 0.5
    else:
        crn_rep = 0.1

    if Severity == "1":
        crn_sev = 50
    elif Severity == "2":
        crn_sev = 20
    elif Severity == "3":
        crn_sev = 5
    else:
        crn_sev = 1

    print("CRN is " + str(round(crn_exp * crn_rep * crn_sev, 2)))
    return round(crn_exp * crn_rep * crn_sev, 2)

def get_crn(msg, debug):

    CRNExposure = msg['fields']['LessonsDesktop.CRNExposure'][:1]
    CRNRepro = msg['fields']['LessonsDesktop.CRNRepro'][:1]
    Severity = msg['fields'].get('Microsoft.VSTS.Common.Severity', '1')[:1]
    ID = msg['id']

    if debug:
        print("CRNExposure is " + CRNExposure)
        print("CRNRepro is " + CRNRepro)
        print("Severity is " + Severity)

    CRN = calculate_crn(CRNExposure, CRNRepro, Severity, debug)
    return CRN, ID

def update_tar(tar, id, debug):
    try:
        url = 'https://{ORG_ID}.visualstudio.com/DefaultCollection/_apis/wit/workitems/' + str(id) + '?api-version=4.1-preview'

        data = [
            {
                "op": "add",
                "path": "/fields/Custom.ActivityRanktotal",
                "value": str(tar)
            }
        ]

        response = requests.patch(url, json=data, headers={'Content-type': 'application/json-patch+json'})

        if debug:
            print("URL and response to adding tags to vsts bug:")
            print(url)
            print(response)
    except:
        print("Bug deleted")

def calculate_tar(cost_reduction, create_new_tech, establish_m, fills_a_strat, probability, production_imp, project_complex, required_to_sup, requirement_for, technical_capab, time_critical, truly_novel):
    strategic_criteria = (establish_m + fills_a_strat + truly_novel)/3
    business_criteria  = (requirement_for + production_imp + cost_reduction)/3
    technical_criteria = (create_new_tech + required_to_sup + technical_capab)/3
    risk_criteria      = (time_critical + probability + project_complex)/3

    return round(strategic_criteria + business_criteria + technical_criteria + risk_criteria, 2)

def get_tar(msg, debug):
    # get the values from the message for the fields to calculate the TAR
    cost_reduction  = msg['fields']['Custom.Costreductionpotentialoramount']
    create_new_tech = msg['fields']['Custom.Createsnewtechnologyplatform']
    establish_m     = msg['fields']['Custom.Establishesamarketleadershippositionorcleardifferentiation']
    fills_a_strat   = msg['fields']['Custom.Fillsastrategicgapinproductoffering']
    probability     = msg['fields']['Custom.Probabilityofsuccesfullyimplementingthisproject']
    production_imp  = msg['fields']['Custom.Productimpactonmarketshare']
    project_complex = msg['fields']['Custom.ProjectComplexity']
    required_to_sup = msg['fields']['Custom.Requiredtosupportenableotherproducts']
    requirement_for = msg['fields']['Custom.Requirementforkeyaccountoropp']
    technical_capab = msg['fields']['Custom.Technicalcapabilityinhouse']
    time_critical   = msg['fields']['Custom.Timecritical']
    truly_novel     = msg['fields']['Custom.TrulynovelresearchinSMARTscoreoradjacenttechnologyspaces']

    ID = msg['id']

    if debug:
        print("Cost reduction potential or amount is " + str(cost_reduction))
        print("Creates new technology platform is " + str(create_new_tech))
        print("Establishes a market leadership position or clear differentiation is " + str(establish_m))
        print("Fills a strategic gap in product offering is " + str(fills_a_strat))
        print("Probability of succesfully implementing this project is " + str(probability))
        print("Product impact on market share is " + str(production_imp))
        print("Project Complexity is " + str(project_complex))
        print("Required to support enable other products is " + str(required_to_sup))
        print("Requirement for key account or opp is " + str(requirement_for))
        print("Technical capability inhouse is " + str(technical_capab))
        print("Time critical is " + str(time_critical))
        print("Truly novel research in score or adjacent technology spaces is " + str(truly_novel))

    TAR = calculate_tar(cost_reduction, create_new_tech, establish_m, fills_a_strat, probability, production_imp, project_complex, required_to_sup, requirement_for, technical_capab, time_critical, truly_novel)

    return TAR, ID

def main(args):

    # if user selected --trace it will print out to the screen all info and calls.
    debug = args.trace

    # get secret information for azure and vsts, trying env vars first
    connstr = os.getenv('CRN_CONNSTR', None)
    ado_username = os.getenv('CRN_ADO_USERNAME', None)
    ado_password = os.getenv('CRN_ADO_PASSWORD', None)
    if connstr is None:
        secrets = get_config_data(os.path.abspath(os.path.join(os.getenv('HOME'), '.vsts.json')))
        connstr = secrets.get('connstr')

    if (connstr is None):
        print("ERROR: Missing json connstr parameter or CRN_CONNSTR environment variable")
        exit(1)

    # Create the service bus service connection
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=connstr, logging_enable=True, transport_type=TransportType.AmqpOverWebsocket)
    with servicebus_client:
        queue_receiver = servicebus_client.get_queue_receiver(queue_name="crn_calculations")

        with queue_receiver:
            messages = queue_receiver.receive_messages(max_wait_time=5)
            while messages:
                for message in messages:
                    decoded_message = b''.join(message.body).decode('utf-8', 'ignore')
                    bug_info = json.loads(get_dict(decoded_message))
                    #bug_info = json.loads(get_dict(str(message)))

                    is_new = bug_info['resource'].get('revision', 'is_new')

                    if "is_new" in is_new:
                        msg = bug_info['resource']
                    else:
                        msg = bug_info['resource']['revision']

                    if debug:
                        print("\nContent of message on the bus")
                        pprint(msg)


                    if "Core_Research" in msg['fields'].get('System.AreaPath'):
                        TAR, ID = get_tar(msg, debug)

                        if debug:
                            pprint('TAR = ' + str(TAR))
                            pprint('ID = ' + str(ID))

                        update_tar(TAR, ID, debug)
                    elif "WebDev" in msg['fields'].get('System.AreaPath'):
                        print("WebDev Broke this so not doing anything")
                    else:
                        crn,ID = get_crn(msg, debug)

                        if debug:
                            pprint('CRN = ' + str(crn))
                            pprint('ID = ' + str(ID))

                        update_crn(crn, ID, ado_username, ado_password, debug)
                    queue_receiver.complete_message(message)
                messages = queue_receiver.receive_messages(max_wait_time=5)


if __name__ == "__main__":
    des = '''
    This is designed to be an Automated script to handle events on a azure service bus
    currently this is only intended to handle events regarding CRN calculations for VSTS bugs

    No Actions required, setup requirement is to have ~/.vsts.json containing connstr (Connection string)
    Call script using: python crn_calculation.py
    add --trace to see what is called.
    '''
    # Initialize the parser and request account-ID to work with. By default will use all accounts.
    parser = argparse.ArgumentParser(description=des, formatter_class=RawTextHelpFormatter)
    parser.add_argument('--trace', dest='trace', help='Used to see calls', action='store_true')
    parser.set_defaults(trace=False)

    args = parser.parse_args()

    main(args)
