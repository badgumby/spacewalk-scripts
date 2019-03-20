#!/usr/bin/python3.7
from xmlrpc import client
import json
from mailer import Mailer
from mailer import Message
from myconfig import *

# Examples (real variables are stored in myconfig.py in same directory)
#SATELLITE_URL = "http://spacewalk/rpc/api"
#SATELLITE_LOGIN = "admin"
#SATELLITE_PASSWORD = "password"
#SMTPRELAY = "relay.company.com"
#FROMADDRESS = "server@company.com"
#EMAIL1 = "person1@company.com"
#EMAIL2 = "person2@company.com"
#EMAIL3 = "person3@company.com"

client = client.Server(SATELLITE_URL, verbose=0)
key = client.auth.login(SATELLITE_LOGIN, SATELLITE_PASSWORD)

failed = client.schedule.listFailedActions(key)
completed = client.schedule.listCompletedActions(key)

# Email headers
sender = Mailer(SMTPRELAY)
message0 = Message(From=FROMADDRESS,
                  To=EMAIL1)
message1 = Message(From=FROMADDRESS,
                  To=EMAIL2)

# String to hold all failed system entries
failedHeader = "<u><h3>Failed Actions</h3></u>"
failedStr = ""
# Loop thru failed and print each
for fail in failed:
    print('')
    for attr, value in fail.items():
        #print(attr, value)
        if attr == 'id':
            idVal = value
            print(idVal)
            failedSystems = client.schedule.listFailedSystems(key, idVal)
            for failedSystem in failedSystems:
                for attr, value in failedSystem.items():
                    if attr == 'server_name':
                        server_name = value
                    if attr == 'message':
                        messageAttr = value
                    if attr == 'timestamp':
                        ts = str(value)
                print("Server: ", server_name, "\nMessage: ", messageAttr)
                fullDump = json.dumps(failedSystem, default=str)
                failure = "<b>Server:</b> " + server_name + "<br><b>Message:</b> " + messageAttr + "<br><b>Timestamp:</b> " + ts + "<br><b>Verbose:</b> " + fullDump + "<br><br>"
                failedStr += failure

# If failed actions found, send email
if failedStr != "":
    message0.Subject = "Spacewalk Failed Actions"
    message0.Html = failedStr
    sender.send(message0)

# String to hold all archive actions
archivedHeader = "<u><h3>Archived Actions</h3></u>"
archivedStr = ""
# Loop thru complete and print each
for complete in completed:
    if "Show differences between profiled" in (complete['name']):
        for attr, value in complete.items():
            if attr == 'id':
                idVal = value
                print(idVal)
                archive = client.schedule.archiveActions(key, idVal)
                print(archive)
                archivedStr += idVal + "<br>"

# If completed actions were archived, send email
if archivedStr != "":
    message1.Subject = "Spacewalk Archived Actions"
    message1.Html = archivedHeader + archivedStr
    sender.send(message1)

client.auth.logout(key)
