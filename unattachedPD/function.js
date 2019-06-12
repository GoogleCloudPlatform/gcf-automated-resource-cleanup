/**
 * HTTP Cloud Function.
 *
 * @param {Object} req Cloud Function request context.
 *                     More info: https://expressjs.com/en/api.html#req
 * @param {Object} res Cloud Function response context.
 *                     More info: https://expressjs.com/en/api.html#res
 */

// Imports the Google Cloud client library
const Compute = require('@google-cloud/compute');

exports.deleteUnattachedPD = (req, res) => {
    console.log("function called!");
    const compute = new Compute();
    
    // gets all disks across regions
    compute.getDisks(function(err, disks){ 
        if(err){
            console.log("there was an error: " + err);
        }
        console.log("there are " + disks.length + " disks");
        for (let item of disks){
            
            // get metadata for each disk
            item.getMetadata(function(err, metadata, apiResponse) {
                console.log("disk " + metadata.name + " is " + metadata.status);
                console.log("disk " + metadata.name + " was last attached on " + metadata.lastAttachTimestamp);

                // handle never attached disk - delete
                if (metadata.lastAttachTimestamp==undefined) {
                    item.delete(function(err, oepration, apiResponse2){
                        if (err){
                            console.log("could not delete disk: " + err);
                        }
                    });
                }

                // handle orphaned disk - 
                // calculate age
                // if older than (x) -  take a snapshot and delete

                // compute age by convering ISO 8601 timestamps to Date
                var sinceLastAttach = computeDiskAge(new Date(metadata.lastAttachTimestamp));
 
                //  handle old currently unattached disk
                if ((sinceLastAttach > -1) // specify your own preferred age of disk here
                    && metadata.users==null){ // not in use currently
                        
                        // timestamp the snapshot name
                        var snapshotName = metadata.name + new Date().getTime;
                        console.log("creating snapshot named " + snapshotName);
                        // take a snapshot
                        item.createSnapshot(function(err, operation, snapResponse){
                            if (err){
                                console.log("could not create snapshot: " + err);
                            }
                            console.log("created snapshot: " + snapResponse);
                        })

                        // delete
                        console.log("deleting old disk " + metadata.name);
                        item.delete(function(err, oepration, apiResponse2){
                            if (err){
                                console.log("could not delete disk: " + err);
                            }
                            console.log("deleted disk");
                        });
                }            
            })
        }
        res.send("there are " + disks.length + " total disks");
    });
}

function computeDiskAge (originDate){
    var currDate = new Date();
    var diskAge = Math.floor((currDate - originDate)/86400e3);
    return diskAge;
}