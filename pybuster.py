#!/usr/bin/env python
#
# pybuster copyright (C) 2013 rbsec, CrumblyMongoose
# Licensed under GPLv3, see LICENSE for details
#

import Queue
import threading
import urllib2
import sys

# Usage: pybuster.py <domain name> <wordlist>

domain = sys.argv[1]
global target

# opens given wordlist, reads and removes carriage returns
wordlist = open(sys.argv[2]).read().splitlines()

queue = Queue.Queue()
          
class queue_manager(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def get_dir(self, word):
        global target

        if word.find('.') == -1:
            url = target + "/" + word + "/"
        else:
            url = target + "/" + word

        request = urllib2.Request(url)
        request.get_method = lambda : 'HEAD'

        try:
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


def main():
    global target

    for i in range(2):      #Number of threads
        t = queue_manager(queue)
        t.setDaemon(True)
        t.start()

    for word in wordlist:
        queue.put(word)

    if not "http" in domain.lower():
        target = "http://" + domain.lower()
    else:
        target = domain.lower()

    queue.join()
main()
