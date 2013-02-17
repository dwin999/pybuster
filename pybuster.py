#!/usr/bin/env python
import Queue
import threading
import urllib2
import sys

target = sys.argv[1]

wordlist = ["admin", "test", "redmine", "robots.txt", "secret"]
	            
queue = Queue.Queue()
          
class getUrl(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            word = self.queue.get(timeout=2)
            request = urllib2.Request("http://" + target + "/" + word)
            request.get_method = lambda : 'HEAD'

            try:
                response = urllib2.urlopen(request)
            except urllib2.URLError, e:
                if e.code == 404:
                    pass
            else:       # 200
                print word + " - 200"

            self.queue.task_done()

def main():
    for i in range(2):      #Number of threads
        t = getUrl(queue)
        t.setDaemon(True)
        t.start()

    for word in wordlist:
        queue.put(word)

    queue.join()
main()
