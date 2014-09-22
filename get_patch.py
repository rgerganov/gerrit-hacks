import sys
import json
import httplib2
import textwrap
import collections

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

def retrieve_change(change_id):
    body = {'jsonrpc': '2.0', 'method': 'changeDetail', 'params': [{'id' : change_id}], 'id':1 }
    body = json.dumps(body)
    response, content = http.request('https://review.openstack.org/gerrit_ui/rpc/ChangeDetailService', 'POST', body, headers)
    data = json.loads(content)
    #return data['result']['patchSets']
    return data['result']

def retrieve_patchset(patchset_id):
    body = {'jsonrpc': '2.0', 'method': 'patchSetDetail', 'params': [patchset_id], 'id':1 }
    body = json.dumps(body)
    response, content = http.request('https://review.openstack.org/gerrit_ui/rpc/ChangeDetailService', 'POST', body, headers)
    data = json.loads(content)
    #patches = [patch for patch in data['result']['patches'] if patch['nbrComments'] > 0]
    #return patches
    return data['result']

def retrieve_diff(patchset_id, patch_key):
    args = {'context':10,'expandAllComments':False,'ignoreWhitespace':'N','intralineDifference':True,'lineLength':100,'manualReview':False,'retainHeader':False,'showLineEndings':True,'showTabs':True,'showWhitespaceErrors':True,'skipDeleted':False,'skipUncommented':False,'syntaxHighlighting':True,'tabSize':8}
    body = {'jsonrpc': '2.0', 'method': 'patchScript', 'params': [patch_key, None, patchset_id, args], 'id':1 }
    body = json.dumps(body)
    response, content = http.request('https://review.openstack.org/gerrit_ui/rpc/PatchDetailService', 'POST', body, headers)
    data = json.loads(content)
    #return data
    return data['result']

def get_accounts_map(accounts):
    result = {}
    for account in accounts:
        if account.has_key('fullName'):
            acc_id = account['id']['id']
            name = account['fullName']
            result[acc_id] = name
    return result

class Change(object):
    def __init__(self):
        self.patchsets = []

    def dump(self, indent=0):
        space = ' ' * indent
        print "%sChange: %d" % (space, self.id)

class PatchSet(object):
    def __init__(self):
        self.files = []

    def dump(self, indent=1):
        space = ' ' * indent
        print "%sPatchSet: %d" % (space, self.id)

class File(object):
    def __init__(self):
        # map a line number to its comments
        self.left_comments = collections.defaultdict(list)
        self.right_comments = collections.defaultdict(list)
        # TODO: map a line number to its source code
        # self.left_source = {}
        # self.right_source = {}

    def dump(self, indent=2):
        space1 = ' ' * indent
        space2 = space1 + ' '
        print "%sFile: %s" % (space1, self.name)
        for ln, comments in self.left_comments.iteritems():
            print "%sLine number: %d" % (space2, ln)
            for comment in comments:
                comment.dump(indent + 2)
        for ln, comments in self.right_comments.iteritems():
            print "%sLine number: %d" % (space2, ln)
            for comment in comments:
                comment.dump(indent + 2)

class Comment(object):
    def dump(self, indent=4):
        space = ' ' * indent
        prefix = '%s[%s] ' % (space, self.author)
        wrapper = textwrap.TextWrapper(initial_indent=prefix,
                                       width=80,
                                       subsequent_indent=' ' * len(prefix))
        print wrapper.fill(self.message)

def fetch(change_id):
    change = Change()
    raw_change = retrieve_change(change_id)
    change.id = change_id
    change.subject = raw_change['change']['subject']
    change.created_on = raw_change['change']['createdOn']
    change.dump()
    raw_patchsets = raw_change['patchSets']
    for raw_patchset in raw_patchsets:
        patchset_id = raw_patchset['id']
        patchset_detail = retrieve_patchset(patchset_id)
        raw_patches = patchset_detail['patches']
        raw_patches = [raw_patch for raw_patch in raw_patches if raw_patch['nbrComments'] > 0]
        if not raw_patches:
            continue
        patchset = PatchSet()
        patchset.id = patchset_id['patchSetId']
        for raw_patch in raw_patches:
            patch_key = raw_patch['key']
            raw_diff = retrieve_diff(patchset_id, patch_key)
            f = File()
            f.name = patch_key['fileName']
            accounts = get_accounts_map(raw_diff['comments']['accounts']['accounts'])
            left_comments = raw_diff['comments']['a']
            for comment in left_comments:
                cmt = Comment()
                cmt.message = comment['message']
                line_number = comment['lineNbr']
                author_id = comment['author']['id']
                cmt.author = accounts[author_id]
                f.left_comments[line_number].append(cmt)
            right_comments = raw_diff['comments']['b']
            for comment in right_comments:
                cmt = Comment()
                cmt.message = comment['message']
                line_number = comment['lineNbr']
                author_id = comment['author']['id']
                cmt.author = accounts[author_id]
                f.right_comments[line_number].append(cmt)
            f.dump()
            patchset.files.append(f)
        patchset.dump()
        change.patchsets.append(patchset)
    return change

#c = fetch(83207)
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: %s <patch#>' % sys.argv[0]
        sys.exit(1)
    fetch(int(sys.argv[1]))

