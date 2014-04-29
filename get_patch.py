import json
import httplib2

#comment on new+old code:
#https://review.openstack.org/#/c/90970/1/nova/conductor/manager.py
#
#comments on a new file:
#https://review.openstack.org/#/c/84933/1/os_cloud_config/cmd/register_nodes.py

#https://review.openstack.org/gerrit_ui/rpc/ChangeDetailService
#{"jsonrpc":"2.0","method":"changeDetail","params":[{"id":84933}],"id":4}

#https://review.openstack.org/gerrit_ui/rpc/ChangeDetailService
#{"jsonrpc":"2.0","method":"patchSetDetail","params":[{"changeId":{"id":84933},"patchSetId":1}],"id":2}

#https://review.openstack.org/gerrit_ui/rpc/PatchDetailService
#{"jsonrpc":"2.0","method":"patchScript","params":[{"fileName":"os_cloud_config/cmd/register_nodes.py","patchSetId":{"changeId":{"id":84933},"patchSetId":1}},null,{"changeId":{"id":84933},"patchSetId":1},{"context":10,"expandAllComments":false,"ignoreWhitespace":"N","intralineDifference":true,"lineLength":100,"manualReview":false,"retainHeader":false,"showLineEndings":true,"showTabs":true,"showWhitespaceErrors":true,"skipDeleted":false,"skipUncommented":false,"syntaxHighlighting":true,"tabSize":8}],"id":3}


http = httplib2.Http(disable_ssl_certificate_validation=True)

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8',
}

body = {'jsonrpc': '2.0', 'method': 'changeDetail', 'params': [{'id' : 84933}], 'id':1 }
body = json.dumps(body)
response, content = http.request('https://review.openstack.org/gerrit_ui/rpc/ChangeDetailService', 'POST', body, headers)
data = json.loads(content)

cid = data['result']['patchSets'][0]['id']
print cid


body = {'jsonrpc': '2.0', 'method': 'patchSetDetail', 'params': [cid], 'id':1 }
body = json.dumps(body)
response, content = http.request('https://review.openstack.org/gerrit_ui/rpc/ChangeDetailService', 'POST', body, headers)
data = json.loads(content)

pid = data['result']['patches'][2]['key']
print pid
print 'nbrComments', data['result']['patches'][2]['nbrComments']

args = {'context':10,'expandAllComments':False,'ignoreWhitespace':'N','intralineDifference':True,'lineLength':100,'manualReview':False,'retainHeader':False,'showLineEndings':True,'showTabs':True,'showWhitespaceErrors':True,'skipDeleted':False,'skipUncommented':False,'syntaxHighlighting':True,'tabSize':8}

body = {'jsonrpc': '2.0', 'method': 'patchScript', 'params': [pid, None, cid, args], 'id':1 }
body = json.dumps(body)
print body
response, content = http.request('https://review.openstack.org/gerrit_ui/rpc/PatchDetailService', 'POST', body, headers)
print content

