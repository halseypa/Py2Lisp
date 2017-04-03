'''
Created on Jul 27, 2015

@author: Phillip Halsey
'''

import socket
import time
from threading import *
import subprocess
import sys

host = "127.0.0.1"
port = 7004
header = []


class client(Thread):
    def __init__(self, host, port):
        
        

        self.msock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.msock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
        self.msock.setsockopt(socket.SOL_SOCKET, socket.TCP_NODELAY, 0)
    
        self.msock.bind((host, port))
        self.sock =  None
        self.LISP_READY = False
        self.MESSAGE_TO_SEND = None
        self.PREDICTION_RECEIVED = None
        
        Thread.__init__(self)
        
    
    def run(self):
        import urllib2
        self.msock.listen(5)
        
        while 1:
            #Block and wait for the next message
                
            clientsocket, address = self.msock.accept()
            self.sock = clientsocket
            
            self.LISP_READY = self.pyGetLispFlag()
            #print "Waiting..."
            
            time.sleep(.3)
            site = "http://127.0.0.1:8000/DataSender.py?columnfilterString=ML_Env_newtree"
            hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                   'Accept-Encoding': 'none',
                   'Accept-Language': 'en-US,en;q=0.8',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Connection': 'keep-alive'}
            req = urllib2.Request(site, headers=hdr)
            
            #grabs tree data from ML
            try:
                mlTree = urllib2.urlopen(req)
                mlTree = mlTree.read()
            except urllib2.HTTPError, e:
                mlTree = ""
            except urllib2.URLError, e:
                mlTree = ""
            
            d = mlTree
                        
            if(str(d) != ""):
                treeData = self.treeFormat(d)
                trialData = str(self.getTrialNum(d))
            else:
                treeData = "86"
                trialData = "0"
                
            print "treeData", treeData
            print "trial Number", trialData
            
            while self.MESSAGE_TO_SEND == None:
                time.sleep(.1) 
            
            self.PREDICTION_RECEIVED=None
            
            print >>sys.stderr, "message to send", self.MESSAGE_TO_SEND
            
            self.pySendLispData(self.MESSAGE_TO_SEND, treeData, trialData)
            if self.MESSAGE_TO_SEND == "":
                break
            
            #for debugging
            #mlTree_Verify = self.getLispMLTree()
            #print >>sys.stderr, "here's the trialNum", mlTree_Verify
            
            prediction = self.getLispPrediction()
            print >>sys.stderr, "lisp response", prediction

            self.MESSAGE_TO_SEND = None
            self.PREDICTION_RECEIVED =  prediction

        print "All finished eating data and very full."
    
    
    def pyGetLispFlag(self):
        data = int(self.sock.recv(1024))
        return data
    
    def pySendLispData(self,data, treeData, trialData):
        output = ""
        
        #alphabetize cue names and output names
        if data == "":
            output = ""
        else:
            for in_out_index in [0, 1]: #0 INPUT CUES, #1 OUTPUT DATA
                for c in sorted(data[in_out_index].keys()):
                    output = output  + str(data[in_out_index][c]) + " "
                #print "ordered cues/output values:", output
        print >>sys.stderr, "output: ", output
        treeData = str(treeData)
        trialData = str(trialData)
        
        self.sock.send(output + "\n")
        self.sock.send(treeData + "\n")
        self.sock.send(trialData + "\n")

             
    def getLispPrediction(self):
        prediction = str(self.sock.recv(1024))
        return prediction
    
    def getLispMLTree(self):
        #debug and verify
        tree = str(self.sock.recv(1024))
        return tree   
    
    def getTrialNum(self, data):
        import re

        lines = data
        mostRecentTrialLine = lines[len(lines)-1]
        mostRecentTrialLine = re.split(r'\t+', mostRecentTrialLine.rstrip('\n'))
        
        return mostRecentTrialLine[0]
        
        
    def treeFormat(self, treeData):
        import re

        lines = treeData
        mostRecentTrialLine = lines[len(lines)-1]
        mostRecentTrialLine = re.split(r'\t+', mostRecentTrialLine.rstrip('\n'))
        print "most recent", mostRecentTrialLine[1]
        
        #formatting to send to lisp
        #print "most recent tree first part", int(mostRecentTrialLine[0])
        #print "most recent tree second part", mostRecentTrialLine[1]
        if (str(mostRecentTrialLine[1]) =="{'cues': False}") or (str(mostRecentTrialLine[1]) =="{'cues': True}"):
            lispTree = mostRecentTrialLine[1].replace("'cues': ", "").replace("{", "").replace("}","").replace("'", "").replace("True", "1").replace("False", "0")
            print "lispTree for {cue: 1 or 0} case", lispTree
        else:
            lispTree = mostRecentTrialLine[1].replace("'cues': ", "").replace("Cue", "").replace("{", "").replace("}","").replace("'", "").replace("True", "1").replace("False", "0").replace(",", "")
            lispTree = lispTree[1:-1]
        
        return lispTree
    
    
    def respFormat(self, respData):
        import re

        lines = respData
        mostRecentTrialLine = lines[len(lines)-1])
        lispResp = re.split(r'\t+', mostRecentTrialLine.rstrip('\n'))
        
        return lispResp[1]
                    
                             
if __name__ == "__main__":
    # comment the following statement out to get guaranteed chaos;-)
    c=client(host, port)
    c.start()
    
    c.MESSAGE_TO_SEND = "0 0 1 0"
    
    while c.PREDICTION_RECEIVED == None:
            time.sleep(1)
    print "yeah: prediction", c.PREDICTION_RECEIVED
    
    c.MESSAGE_TO_SEND = "0 1 0 1"
    while c.PREDICTION_RECEIVED == None:
            time.sleep(1)
    print "yeah: prediction", c.PREDICTION_RECEIVED
        
    c.join()
    print "exiting"
