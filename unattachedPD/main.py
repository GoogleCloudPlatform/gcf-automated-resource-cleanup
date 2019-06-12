# for execution in Cloud Functions Python 3.7.1

# modify these variables for your environment:
project = 'automating-cost-optimization'
authorizedUsername = "postman"
authorizedPassword = "postman"

# imports
import datetime
import googleapiclient
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from datetime import datetime
import calendar
import time
import sys
from flask import request
from flask import Flask
from flask import escape
from basicauth import decode

# initialize global
compute = googleapiclient.discovery.build('compute', 'v1')
credentials = GoogleCredentials.get_application_default()

# define helper functions
def authorizeRequest (request):
    encoded_str = request.headers.get('Authorization')
    username, password = decode(encoded_str)
    #TODO update username and password
    if (username == authorizedUsername, password == authorizedPassword):
        return True
    return False

def waitForZoneOperation(operationResponse, project, zone):
    status = operationResponse["status"]
    name = operationResponse["name"]
    while (status != "DONE"):
        checkRequest = compute.zoneOperations().get(project=project, operation=name, zone=zone)
        checkResponse = checkRequest.execute()
        status = checkResponse["status"]
        time.sleep(3)

# main function
def deleteUnattachedPDs():
    # get list of disks and iterate through it:
    disksRequest = compute.disks().aggregatedList(project=project)
    while disksRequest is not None:
        diskResponse = disksRequest.execute()
        for name, disks_scoped_list in diskResponse['items'].items():
            if disks_scoped_list.get('warning') is None:
                # got disks
                for disk in disks_scoped_list['disks']: # iterate through disks
                    diskName = disk['name']
                    print (diskName)
                    
                    # handle never attached disk - delete it
                    try:
                        if disk['lastAttachTimestamp'] is None:
                            print ("none!")
                    except KeyError:
                        print ("disk was never attached")
                        deleteRequest = 

        disksRequest = compute.disks().aggregatedList_next(previous_request=disksRequest, previous_response=diskResponse)

deleteUnattachedPDs()
