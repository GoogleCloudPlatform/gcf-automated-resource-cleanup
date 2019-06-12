

// Imports the Google Cloud client library
const Compute = require('@google-cloud/compute');


console.log("function called!");

const deletePDs = async () => {
    const compute = new Compute();
    var disks;
    try {
        await compute.getDisks(disks);
        console.log("there are " + disks.length + " disks");
        } catch (getDisksError) {
            throw getDisksError;
        }
        
    for (let item of disks){
        
        console.log("getting metadata");
        // get metadata for each disk
        const metadata = item.getMetadata();
        console.log("disk " + metadata.name + " is " + metadata.status);
        console.log("disk " + metadata.name + " was last attached on " + metadata.lastAttachTimestamp);

        if (metadata.lastAttachTimestamp==undefined) {
            console.log("disk " + metadata.name + " was never attached - deleting");
            try {
                item.delete();
                } catch (deleteError) {
                    throw deleteError;
                }
        }

    }
    
}
deletePDs()
    .then(() => console.log("\nSuccess!"))
    .catch((e) => console.log("\nFailure: " + e))
    .finally(() => process.exit())

console.log("finsihed");
            
/* 
            // handle orphaned disk - 
            // calculate age
            // if older than (x) -  take a snapshot and delete

            // compute age by convering ISO 8601 timestamps to Date
            var sinceLastAttach = computeDiskAge(new Date(metadata.lastAttachTimestamp));

            //  handle old currently unattached disk
            if ((sinceLastAttach > -1) // specify your own preferred age of disk here
                && metadata.users==null){ // not in use currently
                    
                    // timestamp the snapshot name
                    var snapshotName = metadata.name + new Date().getTime();
                    console.log("creating snapshot named " + snapshotName);
                    // take a snapshot
                    item.createSnapshot(function(snapshotErr, snapOperation, snapResponse){
                        if (snapshotErr){
                            console.log("could not create snapshot: " + snapshotErr);
                        }
                        console.log("created snapshot: " + snapResponse);
                        // delete
                        console.log("deleting old disk " + metadata.name);
                        item.delete(function(deleteErr, deleteOperation, deleteResponse){
                            if (err){
                                console.log("could not delete disk: " + err);
                            }
                            console.log("deleted disk");
                        });
                    })
            }            
        })
    }
    
});
*/
function computeDiskAge (originDate){
    var currDate = new Date();
    var diskAge = Math.floor((currDate - originDate)/86400e3);
    return diskAge;
}