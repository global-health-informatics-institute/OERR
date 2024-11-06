1. test connection
   ```bash
   curl http://127.0.0.1:5984
   ```
1. check dbs
   ```bash
   curl http://admin:sinthaMW@127.0.0.1:5984/_all_dbs | jq
   ```
1. db info
   ```bash
   curl http://admin:sinthaMW@127.0.0.1:5984/mss_results_new | jq
   ```

1. get docs of this database 
   ```bash
   curl http://admin:sinthaMW@127.0.0.1:5984/mss_results_new/_all_docs?include_docs=true  | jq
   ```

1. add a doc with id 1 and a field "ward":"MSS"
   ```bash
   curl -X PUT http://admin:sinthaMW@127.0.0.1:5984/mss_results_new/1 \
    -H "Content-Type: application/json" \
    -d '{"ward": "MSS"}'
   ```

1. add a doc with id 2 and a field "ward":"other"
   ```bash
   curl -X PUT http://admin:sinthaMW@127.0.0.1:5984/mss_results_new/11 \
    -H "Content-Type: application/json" \
    -d '{"ward": "other"}'
   ```

1. get _replication docs 
   ```bash
   curl http://admin:sinthaMW@127.0.0.1:5984/_replicator/_all_docs?include_docs=true | jq
   ```

1. drop replicator indtance
   ```bash
   curl -X DELETE http://admin:sinthaMW@127.0.0.1:5984/_replicator
   ```


1. get jiyar
   ```bash
   curl http://OERRuser:sinthaMW@127.0.0.1:5984/mss_results_new/jiyar | jq
   ```
1. Delete instance
   ```bash
   curl -X DELETE http://127.0.0.1:5984/mss_results_new -u admin:root
   ```
1. Create instance
   ```bash
   curl -X PUT http://127.0.0.1:5984/my_database -u admin:password
   ```
