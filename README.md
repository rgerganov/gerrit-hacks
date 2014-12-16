Motivation
==========
It is hard to follow the discussion for a review request in Gerrit when there are many patch sets with many inline comments.

Solution
========
This is a web app which displays all inline comments from all patch sets in a single page. It is currently hosted on Google App Engine and it accepts a change ID as part of the url, e.g. http://gerrit-mirror.appspot.com/127283. It is configured to work against the OpenStack Gerrit but this can be easily changed by modifying gerrit-mirror.py.

The frontend is using the same APIs that are used by the Gerrit UI, so it can be easily deployed on existing Gerrit server. The backend (gerrit-mirror.py) is just a simple proxy to the real Gerrit backend.
