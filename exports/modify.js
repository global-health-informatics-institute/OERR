var fs = require("fs");
var { exec } = require("child_process");

console.log("\n *START transformation* \n");

function transformation(fileName, dbUrl) {
    var content = fs.readFileSync(fileName, 'utf8');
    var json = JSON.parse(content);
    var docs = json.rows;
    var newDocs = [];

    docs.forEach(function(doc) {
        var innerdoc = doc.doc;
        delete innerdoc._rev;
        newDocs.push(innerdoc);
    });

    var newJson = { docs: newDocs };
    var newContent = JSON.stringify(newJson, null, 2); // Adding indentation for readability

    fs.writeFile(fileName, newContent, 'utf8', function(err) {
        if (err) throw err;
        console.log(fileName + ' transformation complete');

        // Trigger curl command after transformation is complete
        var curlCommand = `curl -d @${fileName} -H "Content-Type: application/json" -H "Referer: http://localhost" -X POST ${dbUrl}/_bulk_docs`;
        exec(curlCommand, (err, stdout, stderr) => {
            if (err) {
                console.error(`Error executing curl for ${fileName}: ${err}`);
                return;
            }
            console.log(`Curl command for ${fileName} executed successfully`);
            console.log('stdout:', stdout);
            console.error('stderr:', stderr);
        });
    });

    console.log("\n *DONE transformation!* \n");    
}

// Call transformation function with the appropriate database URLs
transformation("archived_records.json", "http://admin:root@127.0.0.1:5984/oerr_archived_records");
transformation("couch_db.json", "http://admin:root@127.0.0.1:5984/oerr");
transformation("lab_test_panels.json", "http://admin:root@127.0.0.1:5984/oerr_lab_test_panels");
transformation("lab_test_type.json", "http://admin:root@127.0.0.1:5984/oerr_lab_test_type");
transformation("patients.json", "http://admin:root@127.0.0.1:5984/oerr_patients");
transformation("records.json", "http://admin:root@127.0.0.1:5984/oerr_records");
transformation("users.json", "http://admin:root@127.0.0.1:5984/oerr_users");
