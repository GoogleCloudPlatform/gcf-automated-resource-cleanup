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

exports.unused_ip_function = (req, res) => {
    
    console.log("function called!");
    
    // use compute API to get all addresses 
    const compute = new Compute();
    compute.getAddresses(function(err, addresses){ // gets all addresses across regions
        if(err){
            console.log("there was an error: " + err);
        }
        if (addresses == null) {
            console.log("no addresses found");
            return;
        }
        console.log("there are " + addresses.length + " addresses");
        
        // iterate through addresses
        for (let item of addresses){

            // get metadata for each address
            item.getMetadata(function(err, metadata, apiResponse) {
                
                // if the address is not used:
                if (metadata.status=='RESERVED'){
                   
                    // compute age by convering ISO 8601 timestamps to Date
                    var creationDate = new Date(metadata.creationTimestamp);
                    var currDate = new Date();
                    var addressAge = Math.floor((currDate - creationDate)/86400e3);;
                    
                    // delete address
                    item.delete(function(err, operation, apiResponse2){
                        if (err) {
                            console.log("could not delete address: " + err);
                        }
                    })
                }
            })
        }
        // return number of addresses evaluated
        res.send("there are " + addresses.length + " total addresses");
    });  
}