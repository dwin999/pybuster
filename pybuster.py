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

class scanner(threading.Thread):
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
                out.status("trying " + url)
            response = urllib2.urlopen(request)
        except urllib2.URLError, e:
            if e.code == 404:
                pass
        else:       # 200
            out.good(word + " - 200")

    def run(self):
        while True:
            try:
                word = self.queue.get(timeout=1)
            except:
                return
            self.get_dir(word)
            self.queue.task_done()


class output:
    def status(self, message):
        print col.blue + "[*] " + col.end + message

    def good(self, message):
        print col.green + "[+] " + col.end + message

    def warn(self, message):
        print col.red + "[-] " + col.end + message

    def fatal(self, message):
        print col.red + "FATAL: " + col.end + message


class col:
    if sys.stdout.isatty():
        green = '\033[32m'
        blue = '\033[94m'
        red = '\033[31m'
        end = '\033[0m'
    else:
        green = ""
        blue = ""
        red = ""
        end = ""


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
    global out
    
    # Open wordlist, removes carriage returns
    wordlist = open(args.wordlist).read().splitlines()
    domain = args.domain
    queue = Queue.Queue()   # Initialise the queue
    out = output()
    
    
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
        t = scanner(queue)
        t.setDaemon(True)
        t.start()

    for word in wordlist:
        queue.put(word)

    try:
        for i in range(args.threads):
            t.join(1024)       # Timeout needed or threads ignore exceptions..
    except KeyboardInterrupt:
        out.fatal("Quitting...")
main()
