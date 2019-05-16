# for execution in Cloud Functions Python 3.7.1

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
project = 'automating-cost-optimization'
zone = ''
vm = ''
snapShotId = ''
newDiskId = ''

# define helper functions
# TODO create a function to wait for operation to complete

def authorizeRequest (request):
    encoded_str = request.headers.get('Authorization')
    username, password = decode(encoded_str)
    #TODO update username and password
    if (username == "postman", password == "postman"):
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
def resizePD(request):
    
    # Authorize incoming request 
    if (authorizeRequest(request)==False):
        print ("Unauthorized request")
        return ("Unauthorized request")
    print ("authorized request")

    # process incoming body 
    request_json = request.get_json(force=True)
    id = request_json['incident']['resource_id']

    # get aggregated VM list and get our VM
    listRequest = compute.instances().aggregatedList(project=project, filter='id={}'.format(id))
    while listRequest is not None:
        listResponse = listRequest.execute()
        for name, instances_scoped_list in listResponse['items'].items():
            if instances_scoped_list.get('warning') is None:
                # there are instances
                for instance in instances_scoped_list['instances']: # iterate through all instances in zone
                    if instance['id'] == id: # should be only one match
                        instanceName = instance['name']
                        print ("instance name is" + instanceName) # instance name
                        vm = instanceName
                        zone = name.rsplit('/',1)[1] # zone name
                        print ("zone is " + zone)
                        # return 'Instance name is: {}\n'.format(instanceName)
        listRequest = compute.instances().aggregatedList_next(previous_request=listRequest, previous_response=listResponse)
    
    # generate timestamped values
    d = datetime.utcnow()
    unixtime = calendar.timegm(d.utctimetuple())
    newSnapshotName = vm + str(unixtime)
    newDiskName = newSnapshotName
    
    # get the VM in question
    vmGetRequest = compute.instances().get(project=project, zone=zone, instance=vm)
    vmGetResponse = vmGetRequest.execute()
    instance = vmGetResponse["name"]
 
    # get first disk - assuming it's the boot disk
    currentBootDiskSource = vmGetResponse["disks"][0]["source"]
    diskDeviceName = vmGetResponse["disks"][0]["deviceName"]
    currentBootDisk = currentBootDiskSource.rsplit('/', 1)[-1]
    
    # fetch the disk
    print("fetching disk")
    diskGetRequest = compute.disks().get(project=project, zone=zone, disk=currentBootDisk)
    diskGetResponse = diskGetRequest.execute()
    print("got disk: " + diskGetResponse["name"])
    originalDiskSize = diskGetResponse["sizeGb"]
    print ("original disk size is: " + str(originalDiskSize))

    # create the snapshot
    print('taking snapshot ' + newSnapshotName)
    snapshot_body = {
        "name" : newSnapshotName
    }
    snapResponse = (compute.disks().createSnapshot(project=project, zone=zone, disk=currentBootDisk, body=snapshot_body)).execute()
    print('took snapshot: ' + newSnapshotName)
    print('operation status is: ' + str(snapResponse["status"]))
    waitForZoneOperation(snapResponse, project, zone)
    snapShotId = snapResponse["id"]
    print("snapshot completed. snapshot: " + snapShotId)

    # create new disk from snapshot
    print("creating new disk from snapshot")
    # set size for new disk
    newDiskSize = int(float(originalDiskSize) - 1) # reduce disk by 1
    disk_body = {
        "name" : newDiskName,
        "sizeGb" : newDiskSize,
        "sourceSnapshotId" : snapShotId
    }
    diskCreateResponse = (compute.disks().insert(project=project, zone=zone, body=disk_body)).execute() 
    print("started disk creation")
    waitForZoneOperation(diskCreateResponse, project, zone)
    newDiskId = diskCreateResponse["targetLink"]
    print("disk creation complete: " + newDiskId)

    # stop VM if it's running
    # check if the machine is running first
    print("getting VM status")
    vmStatus = vmGetResponse["status"]
    if (vmStatus == 'RUNNING'): # if machine is running, stop it
        print("stopping vm")
        stopResponse = (compute.instances().stop(project=project, zone=zone, instance=vm)).execute()
        waitForZoneOperation(stopResponse, project, zone)
        print("stopped VM")
    else:
        print("vm is already stopped") # if not running, we're done
    
    return ("PD resized!")


