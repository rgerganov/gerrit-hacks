import sys
import json
import httplib2
import textwrap
import collections

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
    return data['result']

def retrieve_patchset(patchset_id):
    body = {'jsonrpc': '2.0', 'method': 'patchSetDetail', 'params': [patchset_id], 'id':1 }
    body = json.dumps(body)
    response, content = http.request('https://review.openstack.org/gerrit_ui/rpc/ChangeDetailService', 'POST', body, headers)
    data = json.loads(content)
    return data['result']

def retrieve_diff(patchset_id, patch_key):
    args = {'context':10,'expandAllComments':False,'ignoreWhitespace':'N','intralineDifference':True,'lineLength':100,'manualReview':False,'retainHeader':False,'showLineEndings':True,'showTabs':True,'showWhitespaceErrors':True,'skipDeleted':False,'skipUncommented':False,'syntaxHighlighting':True,'tabSize':8}
    body = {'jsonrpc': '2.0', 'method': 'patchScript', 'params': [patch_key, None, patchset_id, args], 'id':1 }
    body = json.dumps(body)
    response, content = http.request('https://review.openstack.org/gerrit_ui/rpc/PatchDetailService', 'POST', body, headers)
    data = json.loads(content)
    return data['result']

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
        # map a line number to a list of comments
        self.left_comments = collections.defaultdict(list)
        self.right_comments = collections.defaultdict(list)
        self.left_source = []
        self.right_source = []

    def dump(self, indent=2):
        space1 = ' ' * indent
        space2 = space1 + ' '
        print "%sFile: %s" % (space1, self.name)
        od = collections.OrderedDict(sorted(self.left_comments.items()))
        for ln, comments in od.iteritems():
            print "%s%d: %s" % (space2, ln, self.left_source[ln-1])
            for comment in comments:
                comment.dump(indent + 2)
        od = collections.OrderedDict(sorted(self.right_comments.items()))
        for ln, comments in od.iteritems():
            print "%s%d: %s" % (space2, ln, self.right_source[ln-1])
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

def get_accounts_map(accounts):
    result = {}
    for account in accounts:
        if account.has_key('fullName'):
            acc_id = account['id']['id']
            name = account['fullName']
            result[acc_id] = name
    return result

def compute_right_source(left_source, edits, right_ranges):
    result = list(left_source)
    for edit in edits:
        x1, y1, x2, y2 = edit[0:4]
        result[x1:y1] = result[x2:y2]
    for range in right_ranges:
        base = range['base']
        lines = range['lines']
        result[base:base+len(lines)] = lines
    return result

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
        patchset.dump()
        for raw_patch in raw_patches:
            patch_key = raw_patch['key']
            raw_diff = retrieve_diff(patchset_id, patch_key)
            f = File()
            f.name = patch_key['fileName']
            accounts = get_accounts_map(raw_diff['comments']['accounts']['accounts'])
            left_ranges = raw_diff['a']['ranges']
            if left_ranges:
                f.left_source = left_ranges[0]['lines']
            edits = raw_diff['edits']
            right_ranges = raw_diff['b']['ranges']
            f.right_source = compute_right_source(f.left_source, edits, right_ranges)

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
        change.patchsets.append(patchset)
    return change

#c = fetch(83207)
#httplib2.debuglevel=1
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: %s <patch#>' % sys.argv[0]
        sys.exit(1)
    fetch(int(sys.argv[1]))

