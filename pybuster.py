#!/usr/bin/env python
#
# pybuster copyright (C) 2013 rbsec, CrumblyMongoose
# Licensed under GPLv3, see LICENSE for details
#

import Queue
import threading
import urllib2
import sys
import argparse

# Usage: pybuster.py <domain name> <wordlist>

class queue_manager(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def get_dir(self, word):
        if word.find('.') == -1:
            url = target + "/" + word + "/"
        else:
            url = target + "/" + word

        request = urllib2.Request(url)
        request.get_method = lambda : 'HEAD'

        try:
            if args.verbose == True:
                print 'trying ' + url
            response = urllib2.urlopen(request)
        except urllib2.URLError, e:
            if e.code == 404:
                pass
        else:       # 200
            print word + " - 200"

    def run(self):
        while True:
            word = self.queue.get(timeout=2)
            self.get_dir(word)
            self.queue.task_done()


def argParser():
    global args
    
    parser = argparse.ArgumentParser('pybuster.py')
    parser.add_argument('-d', '--domain', help='target domain', dest='domain', required=True)
    parser.add_argument('-w', '--wordlist', help='wordlist to use', dest='wordlist', required=True)
    parser.add_argument('-t', '--threads', help='number of threads', dest='threads', required=False, type=int, default=2)
    parser.add_argument('-v', '--verbose', action="store_true", default=False, help='verbose mode', dest='verbose', required=False)
    args = parser.parse_args()

def setVars():
    global target
    global domain
    global wordlist
    global queue
    
    # Open wordlist, removes carriage returns
    wordlist = open(args.wordlist).read().splitlines()
    domain = args.domain
    queue = Queue.Queue()   # Initialise the queue
    
    
    if not "http" in domain.lower():    # Assume http if not specified
        target = "http://" + domain.lower()
    else:
        target = domain.lower()
        
        
def main():
    argParser()
    setVars()
    
    if args.threads > 20 or args.threads < 1:
        args.threads = 2
    for i in range(args.threads):      # Number of threads
        t = queue_manager(queue)
        t.setDaemon(True)
        t.start()

    for word in wordlist:
        queue.put(word)

    queue.join()
main()
