/*
Copyright 2019 Google LLC
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
https://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

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