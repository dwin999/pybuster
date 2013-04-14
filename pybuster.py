#!/usr/bin/env python
#
# pybuster copyright (C) 2013 rbsec, CrumblyMongoose
# Licensed under GPLv3, see LICENSE for details
#

import argparse
import os
import sys
import threading
import platform

try:    # Ugly hack because Python3 decided to rename Queue to queue
    import Queue
except ImportError:
    import queue as Queue

try:    # Another Python3 rename
    import urllib2
except ImportError:
    import urllib.request as urllib2

# Usage: pybuster.py <domain name> <wordlist>

class scanner(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def get_dir(self, word):
        if word.find('.') == -1:
            url = target + word + "/"
        else:
            url = target + word

        request = urllib2.Request(url)
        request.get_method = lambda : 'HEAD'

        try:
            response = urllib2.urlopen(request)
        except urllib2.URLError as e:
            if e.code == 404:
                pass
            else:
                print(word + " - " + col.red + str(e.code) + col.end)
        except ConnectionResetError:
            out.fatal("Could not connect to server")
            sys.exit(1)

        else:       # 200
            if word.find('.') == -1:        # Folder found
                print(word + "/ - " + col.green + str(response.getcode()) + col.end)
                if args.recursive:
                    out.verbose("Adding folder " + word + " to scan")
                    add_folder(word)
            else:       # File found
                print(word + " - " + col.green + str(response.getcode()) + col.end)

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
        print(col.blue + "[*] " + col.end + message)

    def good(self, message):
        print(col.green + "[+] " + col.end + message)

    def verbose(self, message):
        if args.verbose:
            print(col.brown + "[v] " + col.end + message)

    def warn(self, message):
        print(col.red + "[-] " + col.end + message)

    def fatal(self, message):
        print(col.red + "FATAL: " + message + col.end)


class col:
    if sys.stdout.isatty() and platform.system() != "Windows":
        green = '\033[32m'
        blue = '\033[94m'
        red = '\033[31m'
        brown = '\033[33m'
        end = '\033[0m'
    else:# Disabling col for windows and pipes
        green = ""
        blue = ""
        red = ""
        brown = ""
        end = ""


def arg_parser():
    global args
    
    parser = argparse.ArgumentParser('pybuster.py')
    parser.add_argument('-d', '--domain', help='target domain', dest='domain', required=True)
    parser.add_argument('-w', '--wordlist', help='wordlist to use', dest='wordlist', required=False)
    parser.add_argument('-t', '--threads', help='number of threads', dest='threads', required=False, type=int, default=2)
    parser.add_argument('-r', '--no-recursive', action="store_false", default=True, help='disable recursive scanning', dest='recursive', required=False)
    parser.add_argument('-v', '--verbose', action="store_true", default=False, help='verbose mode', dest='verbose', required=False)
    args = parser.parse_args()

def set_vars():
    global target
    global domain
    global wordlist
    global queue
    global out
    
    out = output()
    # Open wordlist, removes carriage returns
    if not args.wordlist:   # Try to use default wordlist if non specified
        args.wordlist = os.path.dirname(os.path.realpath(__file__)) + "/wordlist.txt"
    try:
        wordlist = set(open(args.wordlist).read().splitlines())
    except:
        out.fatal("Could not open wordlist " + args.wordlist)
        sys.exit(1)
    domain = args.domain
    queue = Queue.Queue()   # Initialise the queue
    
    if not "http" in domain.lower():    # Assume http if not specified
        target = "http://" + domain.lower()
    else:
        target = domain.lower()
        
def add_folder(folder):
    for word in wordlist:
        queue.put(folder + "/" + word)
        
if __name__ == "__main__":
    arg_parser()
    set_vars()
    
    if args.threads > 20 or args.threads < 1:
        args.threads = 2
    for i in range(args.threads):      # Number of threads
        t = scanner(queue)
        t.setDaemon(True)
        t.start()

    add_folder("")  # Scan / on the site

    try:
        for i in range(args.threads):
            t.join(1024)       # Timeout needed or threads ignore exceptions..
    except KeyboardInterrupt:
        out.fatal("Quitting...")
