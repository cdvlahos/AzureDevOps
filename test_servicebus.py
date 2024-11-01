#!/usr/bin/env python
from __future__ import division
from azure.servicebus import ServiceBusClient
from uamqp.constants import TransportType
import argparse
from argparse import RawTextHelpFormatter

import requests
#import html2text

import json
import os
import sys
from pprint import pprint


# return the json file containing the password info
def get_config_data(file):
    with open(file) as data_file:
        data = json.load(data_file)
    return data


def main(args):
    # get secret information for azure and vsts 
    secrets = get_config_data(os.path.abspath(os.path.join(os.getenv('HOME'), '.vsts.json')))

    # if user selected --trace it will print out to the screen all info and calls.
    debug = args.trace

    if debug:
        print("Azure bus namespace: " + secrets['namespace'])
        print("Azure bus key name: " + secrets['keyname'])

    # Create the service bus service connection
    with ServiceBusClient.from_connection_string(secrets['connstr']) as client:
    # max_wait_time specifies how long the receiver should wait with no incoming messages before stopping receipt.
    # Default is None; to receive forever.
        with client.get_queue_receiver("crn_calculations", max_wait_time=30) as receiver:
            for msg in receiver:  # ServiceBusReceiver instance is a generator.
                print(str(msg))

    


if __name__ == "__main__":
    des = '''
    This is designed to be an Automated script to handle events on a azure service bus
    currently this is only intended to handle events regarding CRN calculations for VSTS bugs

    No Actions required, setup requirement is to have ~/.vsts.json containing namespace, keyname and key
    Call script using: python crn_calculation.py
    add --trace to see what is called.
    '''
    # Initialize the parser and request account-ID to work with. By default will use all accounts.
    parser = argparse.ArgumentParser(description=des, formatter_class=RawTextHelpFormatter)
    parser.add_argument('--trace', dest='trace', help='Used to see calls', action='store_true')
    parser.set_defaults(trace=False)

    args = parser.parse_args()

    main(args)
