#Copyright 2019 Google LLC
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#https://www.apache.org/licenses/LICENSE-2.0
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

# for execution in Cloud Functions Python 3.7.1


# imports
import datetime
import dateutil.parser
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
import pytz

# initialize global
compute = googleapiclient.discovery.build('compute', 'v1')
credentials = GoogleCredentials.get_application_default()

# define helper functions
def waitForZoneOperation(operationResponse, project, zone):
    status = operationResponse["status"]
    name = operationResponse["name"]
    while (status != "DONE"):
        checkRequest = compute.zoneOperations().get(project=project, operation=name, zone=zone)
        checkResponse = checkRequest.execute()
        status = checkResponse["status"]
        time.sleep(3)

# main function
def delete_unattached_pds(request):
    assert request.args and 'project' in request.args, '"project" argument required.'
    project = request.args['project']
    dry_run = True

    if dry_run:
        print ('*** Running in dry_run mode. No disks will be harmed. ***')
    # get list of disks and iterate through it:
    print ("fetching list of disks under project: " + project)
    # TODO(brad): Add filter to reduce response size.
    disksRequest = compute.disks().aggregatedList(project=project)
    while disksRequest is not None:
        diskResponse = disksRequest.execute()
        for name, disks_scoped_list in diskResponse['items'].items():
            if disks_scoped_list.get('warning') is None:
                # got disks
                for disk in disks_scoped_list['disks']: # iterate through disks
                    diskName = disk['name']
                    diskZone = str((disk['zone'])).rsplit('/',1)[1]
                   
                    # handle never attached disk - delete it
                    # lastAttachedTimestamp is not present
                    if 'lastAttachTimestamp' not in disk:
                        print ("disk " + diskName + " was never attached")
                        if not dry_run:
                            deleteRequest = compute.disks().delete(project=project, zone=diskZone, disk=diskName)
                            deleteResponse = deleteRequest.execute()
                            waitForZoneOperation(deleteResponse, project, diskZone)
                            print ("disk " + diskName + " was deleted")
                        continue

                    # handle detached disk - snapshot and delete
                    # lastAttachTimestamp is present AND users is not present

                    if 'users' not in disk and 'lastDetachTimestamp' in disk:
                        detachTimestamp = dateutil.parser.parse(disk['lastDetachTimestamp'])
                        detachedFor = pytz.utc.localize(datetime.utcnow()) - detachTimestamp
                        
                        print ("disk " + diskName + " has no users and has been detached for " + str(detachedFor))
                        
                        # update this for your preferred age
                        if detachedFor.days > -1 and not dry_run:
                            # take a snapshot
                            snapShotName = diskName + str(int(time.time()))
                            print ("taking snapshot: " + snapShotName)
                            snapshotBody = {
                                "name": snapShotName
                            }
                            snapshotRequest = compute.disks().createSnapshot(project=project, zone=diskZone, disk=diskName, body=snapshotBody)
                            snapshotResponse = snapshotRequest.execute()
                            waitForZoneOperation(snapshotResponse, project, diskZone)
                            print ("snapshot completed")

                            # delete the disk
                            print ("deleting disk " + diskName)
                            deleteRequest = compute.disks().delete(project=project, zone=diskZone, disk=diskName)
                            deleteResponse = deleteRequest.execute()
                            waitForZoneOperation(deleteResponse, project, diskZone)
                            print ("disk " + diskName + " was deleted")
                            continue


        disksRequest = compute.disks().aggregatedList_next(previous_request=disksRequest, previous_response=diskResponse)
    return ("disk scan completed")
