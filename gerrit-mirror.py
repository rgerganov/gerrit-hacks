import urllib2
import webapp2

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8',
}

class ChangeDetailService(webapp2.RequestHandler):
    def post(self):
        req = urllib2.Request('https://review.openstack.org/gerrit_ui/rpc/ChangeDetailService', self.request.body, headers)
        response = urllib2.urlopen(req)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.response.write(response.read())

class PatchDetailService(webapp2.RequestHandler):
    def post(self):
        req = urllib2.Request('https://review.openstack.org/gerrit_ui/rpc/PatchDetailService', self.request.body, headers)
        response = urllib2.urlopen(req)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.response.write(response.read())

application = webapp2.WSGIApplication([
    ('/gerrit_ui/rpc/ChangeDetailService', ChangeDetailService),
    ('/gerrit_ui/rpc/PatchDetailService', PatchDetailService),
], debug=True)
