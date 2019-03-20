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

activeSystems = client.system.listActiveSystems(key)
inactiveSystems = client.system.listInactiveSystems(key)

# Email headers
sender = Mailer(SMTPRELAY)
message0 = Message(From=FROMADDRESS,
                  To=EMAIL3)
message1 = Message(From=FROMADDRESS,
                  To=EMAIL3)

# String to hold all systems requiring upgrades
upgradeHeader = "<u><h3>Upgrades Pending</h3></u>"
upgradeStr = ""
# Loop thru failed and print each
for active in activeSystems:
    for attr, value in active.items():
        if attr == 'id':
            idVal = value
        if attr == 'name':
            nameVal = value
        if attr == 'last_checkin':
            lcVal = value
        upgrades = client.system.listLatestUpgradablePackages(key, idVal)
        ctr = sum(map(len, upgrades))
        total = round(ctr / 11)
    if total > 0:
        #print("Name: ", nameVal, "\nID: ", idVal, "\nLast Checkin: ", lcVal, "\nUpdates: ", total)
        #print('')
        cont = "<b>Name:</b> " + nameVal + "<br><b>ID:</b> " + str(idVal) + "<br><b>Last Checkin:</b> " + str(lcVal) + "<br><b>Updates:</b> " + str(total) + "<br><br>"
        upgradeStr += cont

# If upgrades pending, send email
if upgradeStr != "":
    message0.Subject = "Spacewalk - Systems Requiring Updates"
    message0.Html = upgradeHeader + upgradeStr
    sender.send(message0)

# String to hold all systems requiring upgrades
inactiveHeader = "<u><h3>Inactive Systems</h3></u>"
inactiveStr = ""
countInactive = sum(map(len, inactiveSystems))
if round(countInactive) > 0:
    for inactive in inactiveSystems:
        for attr, value in inactive.items():
            if attr == 'id':
                idVal = value
            if attr == 'name':
                nameVal = value
            if attr == 'last_checkin':
                lcVal = value
        #print("Name: ", nameVal, "\nID: ", str(idVal), "\nLast Checkin: ", str(lcVal))
        inactiveContent = "<b>Name:</b> " + nameVal + "<br><b>ID:</b> " + str(idVal) + "<br><b>Last Checkin:</b> " + str(lcVal) + "<br><br>"
        inactiveStr += inactiveContent

# If inactive systems found, send email
if inactiveStr != "":
    message1.Subject = "Spacewalk - Inactive Systems"
    message1.Html = inactiveHeader + inactiveStr
    sender.send(message1)

client.auth.logout(key)
