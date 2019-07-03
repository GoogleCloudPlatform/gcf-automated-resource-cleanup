# for execution in Cloud Functions Python 3.7.1

# modify these variables for your environment:
project = 'automating-cost-optimization'

# imports
import googleapiclient
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from google.cloud import storage
import sys
from flask import request
from flask import Flask
from flask import escape


# initialize global
compute = googleapiclient.discovery.build('compute', 'v1')
credentials = GoogleCredentials.get_application_default()

# main function
def migrate_storage(request):
    # process incoming request to get the bucket to be migrated:
    request_json = request.get_json(force=True)
    # bucket names are globally unique
    bucket_name = request_json['incident']['resource_name']

    # create storage client
    storage_client = storage.Client(project)

    # get bucket
    bucket = storage_client.get_bucket(bucket_name)

    # update storage class
    bucket.storage_class = "NEARLINE"
    bucket.patch()


