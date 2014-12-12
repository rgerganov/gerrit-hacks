#!/bin/bash

curl -v \
    --header 'Content-Type: application/json; charset=UTF-8' \
    --header 'Accept: application/json' \
    --data '{"jsonrpc": "2.0", "method": "changeDetail", "params": [{"id" : 83207}], "id":1 }' \
    http://localhost:8080/gerrit_ui/rpc/ChangeDetailService

curl -k -v \
    --header 'Content-Type: application/json; charset=UTF-8' \
    --header 'Accept: application/json' \
    --data '{"jsonrpc": "2.0", "method": "changeDetail", "params": [{"id" : 83207}], "id":1 }' \
    https://review.openstack.org/gerrit_ui/rpc/ChangeDetailService
