#!/usr/bin/python
 
#This script simultaneously pings multiple hosts.  It then reports how many
#pings were lost and min/max/avg return trips times.
 
#The script takes the following input from the user:
# - name of this test run.  This name will be used in the name of the file
#       that the results are written to.
# - name of the input file (full path name) the format of which can be seen
#       below.
# - the number of pings to run in this test.
# The default ping interval is 200ms, change the pinginterval variable to
#       change it.
 
### Format of Input File ###
 
# (Don't include this first line):
# Format: <Category>,<Description>,<ip address or hostname>
#VIA-Layer2-link,Vlan2,10.126.101.27
#VIA-Layer2-link,Vlan416,10.201.33.243
#VIA-Layer2-link,Vlan417,10.201.40.38
 
import sys
import collections
import time
import datetime
 
from threading import Thread
import subprocess
from subprocess import Popen, PIPE, STDOUT
from Queue import Queue
 
#num_threads = 100
queue = Queue()
 
inputdict = {}
outputdict = {}
myresults = {}
 
#ips = ["10.201.94.5", "10.201.94.36", "10.201.94.101"]
#pinginterval = 1
pinginterval = .2
 
prompt = '>'
### Get Input ###
print "Enter name of this test (No spaces or special characters):"
nameoftest = raw_input(prompt)
print "Enter full path of the input file:"
inputfile = raw_input(prompt)
print "Enter the number of pings for this test:"
numofpings = raw_input(prompt)
############
 
### Derive name of the output file ###
starttime = datetime.datetime.now()
yr = getattr(starttime, 'year')
month = getattr(starttime, 'month')
day = getattr(starttime, 'day')
hour = getattr(starttime, 'hour')
minute =  getattr(starttime, 'minute')
sec =  getattr(starttime, 'second')
testoutput = "%s-%s-%s-%s-%s-%s" % (yr, month, day, hour, minute, sec)
#print testoutput
newoutfile = "%s.%s" % (nameoftest, testoutput)
 
print "Output will be written to ./%s" % newoutfile
########
 
### Parse the input file ###
def parseinput(inputfile):
        inputdict = {}
        for f in inputfile:
                g=f.rstrip()
                catanddescrandip=g.split(',')
                category = catanddescrandip[0]
                descr = catanddescrandip[1]
                destip = catanddescrandip[2]
                inputdict[destip] = [category,descr]
        return(inputdict)
 
fopeninputfile = open(inputfile, 'r')
inputdict = parseinput(fopeninputfile)
#num_threads = len (inputdict)
num_threads = 300
 
#wraps system ping command
def pinger(i, q):
    """Pings subnet"""
    while True:
        ip = q.get()
        print "Thread %s: Pinging %s" % (i, ip)
        cmd = 'ping -q -i %s -c %s %s' % (pinginterval, numofpings, ip)
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        output = p.stdout.read()
        #print output
        outputdict[ip] = output
        q.task_done()
#Spawn thread pool
for i in range(num_threads):
 
    worker = Thread(target=pinger, args=(i, queue))
    worker.setDaemon(True)
    worker.start()
#Place work in queue
#for ip in ips:
for ip in inputdict.keys():
    queue.put(ip)
#Wait until worker threads are done to exit   
queue.join()
 
endtime = datetime.datetime.now()
 
#print type(outputdict)
#outfile = "./%s" % nameoftest
foutfile = open(newoutfile, 'w')
#fopeninputfile = open(inputfile, 'r')
print "==============================================="
print >> foutfile, "RESULTS FOR %s:" %nameoftest
print >> foutfile, "   Test start time: %s" % starttime
print >> foutfile, "   Test end time: %s" % endtime
print >> foutfile, "   Ping interval for this test: %s seconds" % pinginterval
print >> foutfile, "   Number of Pings for this test: %s" % numofpings
print >> foutfile, "Category, Descript, DestIP, NumofDropped, NumSent, RTTInfo"
for ip, output in outputdict.iteritems():
        #print "output for ip %s" % ip
        #print output
        listoflines = output.splitlines()
        #print "here is list"
        #print listoflines
        transrecv = listoflines[3]
        rtt = listoflines[4]
        #print "%s had this many: %s" % (ip, transrecv)
        transrecvsplit = transrecv.split()
        transmitted = transrecvsplit[0]
        received = transrecvsplit[3]
        #print transmitted, received
        numtrans = int(transmitted)
        numrecv = int(received)
        numdropped = numtrans - numrecv
        #print ip, numdropped, rtt
        cat, descript = inputdict[ip]
        myresults[ip] = [cat,descript,numdropped,numtrans,numrecv,rtt]
        #print "%s  | %s  | %s   | %s" % (ip, numdropped, numtrans, rtt)
        print >> foutfile, "%s, %s, %s, %s, %s, %s" % (cat, descript, ip, numdropped, numtrans, rtt)
        if numdropped>0:
                print "%s, %s, %s, %s, %s, %s" % (cat, descript, ip, numdropped, numtrans, rtt)
 
#op = open(foutfile, 'r')
#op_contents = op.read()
#print op_contents
 
#if __name__ == '__main__':
#  main()
