#!/usr/bin/env python

# The way this works:
#  In MS Team Services, for each project group, we define a service hook to
#  send a message into an Azure ServiceBus "Topic".  Essentially a queue, but
#  can have > 1 listener subscribed.  We need this so we can notify both
#  TeamCity and AmpCity.
#  This script will listen to the subscription passed into argv[1]
#  pull out the remoteURLs from the JSON blob and send that to TeamCity

# Some useful URLs:
#  https://github.com/Azure/azure-sdk-for-python
#  https://docs.microsoft.com/en-us/azure/service-bus-messaging/service-bus-python-how-to-use-topics-subscriptions

import os
import sys
import json
import re
import requests

from azure.servicebus import ServiceBusClient, ServiceBusMessage, ServiceBusSubQueue
from uamqp.constants import TransportType

# Set up default parameters
tc_url = 'http://localhost:8111'
rest_url_prefix = '/httpAuth/app/rest/vcs-root-instances/commitHookNotification?locator=type:jetbrains.git,property:(matchType:contains,name:url,value:'
rest_url_suffix = ')'


# Load up the configuration file with org secrets stored in ~/.vsts.json

with open(os.path.abspath(os.path.join(os.getenv('HOME'), '.vsts.json')), 'r') as f:
    config = json.load(f)
# Secret keys for contacting the subscription
subscription = None

repo_regex = re.compile("(_git.*)")

# Create the service bus service connection
client = ServiceBusClient.from_connection_string(config['{ORG_ID}']['servicebus_listener'],
        transport_type=TransportType.AmqpOverWebsocket)


# max_wait_time specifies how long the receiver should wait with no incoming messages before stopping receipt.
# Default is None; to receive forever.
dlq_receiver = client.get_subscription_receiver(topic_name=config['{ORG_ID}']['servicebus_topic'],
        subscription_name="ampcity", sub_queue=ServiceBusSubQueue.DEAD_LETTER)
with dlq_receiver:
    received_msgs = dlq_receiver.receive_messages(max_wait_time=5)
    while received_msgs:
        for msg in received_msgs:
            dlq_receiver.complete_message(msg)
        print("Removed 10 messages from dead letter")
        received_msgs = dlq_receiver.receive_messages(max_wait_time=5)
    print("no more messages")

dlq_receiver = client.get_queue_receiver(queue_name="bug_update", sub_queue=ServiceBusSubQueue.DEAD_LETTER)
with dlq_receiver:
    received_msgs = dlq_receiver.receive_messages(max_wait_time=5)
    while received_msgs:
        for msg in received_msgs:
            dlq_receiver.complete_message(msg)
        print("Removed 10 messages from dead letter")
        received_msgs = dlq_receiver.receive_messages(max_wait_time=5)
    print("no more messages")

dlq_receiver = client.get_queue_receiver(queue_name="crn_calculations", sub_queue=ServiceBusSubQueue.DEAD_LETTER)
with dlq_receiver:
    received_msgs = dlq_receiver.receive_messages(max_wait_time=5)
    while received_msgs:
        for msg in received_msgs:
            dlq_receiver.complete_message(msg)
        print("Removed 10 messages from dead letter")
        received_msgs = dlq_receiver.receive_messages(max_wait_time=5)
    print("no more messages")

dlq_receiver = client.get_queue_receiver(queue_name="dso_updates", sub_queue=ServiceBusSubQueue.DEAD_LETTER)
with dlq_receiver:
    received_msgs = dlq_receiver.receive_messages(max_wait_time=5)
    while received_msgs:
        for msg in received_msgs:
            dlq_receiver.complete_message(msg)
        print("Removed 10 messages from dead letter")
        received_msgs = dlq_receiver.receive_messages(max_wait_time=5)
    print("no more messages")

