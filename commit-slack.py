#!/usr/bin/python

# post-commit: Hook used for SVN post commits
#
# Scott Vitale
# svvitale@gmail.com

# This script is set to publish information after SVN commits to HipChat.
#
# Required files/Application/services:
#     * Subversion: http://subversion.tigris.org/
#     * Working repository
#     * HipChat account and room setup: https://www.hipchat.com/
#     * HipChat token created: https://www.hipchat.com/groups/api
#
import os
import sys
import subprocess
import argparse
import urllib
import urllib2
import re
import json

# Set hipchat info
#
TOKEN=""
DOMAIN=""
NAME="Subversion"
REPO_BASE_URL=''

# svnlook location
LOOK="svnlook"

##############################################################
##############################################################
############ Edit below at your own risk #####################
##############################################################
##############################################################

def sendToSlack(payload):
        url = "https://{0}/services/hooks/subversion?token={1}".format(DOMAIN,TOKEN)
        urllib2.urlopen(url, urllib.urlencode({ 'payload' : json.dumps(payload)}))

def runLook( *args ):
        # check_output will except if it fails so we don't spam the room with 'run svnlook help for help' messages
        return subprocess.check_output( ' '.join([LOOK] + list(args)), shell=True, stderr=subprocess.STDOUT)

def getCommitInfo( repo, revision ):
        log = runLook("log", repo, "-r", revision)
        author = runLook("author", repo, "-r", revision)
        files = runLook("changed", repo, "-r", revision)

        chatMsg = ("""
committed revision
%s
%s
""" % (log, files)).strip()

        # create request dictionary
        param = {
                'revision': revision,
                'url': REPO_BASE_URL + repo + '?=' + revision,
                'author': author,
                'log': chatMsg
        }

        return param

def main():
        parser = argparse.ArgumentParser(description='Post commit hook that sends Slack messages.')
        parser.add_argument('-r', '--revision', metavar='<svn rev>', required=True, help='SVN revision')
        parser.add_argument('-s', '--repository', metavar='<repository>', required=True, help='Repository to operate on')

        args = parser.parse_args()
        payload = getCommitInfo( args.repository, args.revision )

        sendToSlack(payload)
        # sendToSlack( 'Slack SVN Integration Test', '500', '', 'coolsky' )

if __name__ == "__main__":
        main()

