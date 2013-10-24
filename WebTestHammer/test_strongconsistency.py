#!/usr/bin/python
import gevent
from gevent import monkey
import httplib2
from json import loads, dumps
import re
import random
#import threading

monkey.patch_all(dns=False)

#threadLock = threading.Lock()
#successCount = 0;
#failedCount = 0;

class TestAction(object):
    __cookieRe = re.compile('sessionid=(\w+);.*XSRF-TOKEN=(\w+);')
    __checkAuthRe = re.compile('\)\]\}\',\n\{\"userid\": \"[-\w]+\"\}')
    def __init__(self, id):
        self.id = id
    def run(self):   
        sleeptime = self.id * 1
        gevent.sleep(sleeptime)      
        print "start %d %f" % (self.id, sleeptime)
        h = httplib2.Http()
        
        postData = '{"username":"ericd@esna.com","password":"zmkmalbb751018","isRemeberMe":false}'      
        headersData = {"Accept": "application/json, text/plain, */*",
                       "Content-Type": "application/json;charset=UTF-8"}
        rep = None 
        data = None
        try:
            rep, data = h.request('http://socialenterprise-test-2.appspot.com/api/1.0/client/userV2/signin' + "/%s"%(self.id), 
                              'POST', 
                              body=postData, 
                              headers=headersData)
        except:
            pass
        
        sessionid = None
        csrftoken = None
        failedreason = ""
        if(rep != None and data != None and data ==  ")]}',\n{}"):            
            matchObj = self.__cookieRe.match(rep["set-cookie"])
            
            if matchObj:
                sessionid = matchObj.group(1)
                csrftoken = matchObj.group(2)
        else:
            failedreason =  "failed at signin"
        #h2 = httplib2.Http()
        if(sessionid and csrftoken):
            headersData = {"Accept": "application/json, text/plain, */*",
                           "Cookie": "sessionid=%s; XSRF-TOKEN=%s"%(sessionid, csrftoken),
                           "X-XSRF-TOKEN": csrftoken}
            try:
                rep = None
                data = None
                rep, data = h.request('http://socialenterprise-test-2.appspot.com/api/1.0/client/user/checkAuth' + "/%s"%(self.id) , 
                              'GET',
                              headers=headersData)
            except:
                print "Check auth happen exception"
                pass           
            
        if(rep != None and data != None and self.__checkAuthRe.match(data)):
            try:
                rep = None
                data = None
                headersData = {"Accept": "application/json, text/plain, */*",
                           "Cookie": "sessionid=%s; XSRF-TOKEN=%s"%(sessionid, csrftoken),
                           "X-XSRF-TOKEN": csrftoken,
                           "Content-Type": "application/json;charset=UTF-8"}
                postData = '{"username":"ericd@esna.com","password":""}' 
                rep, data = h.request('http://socialenterprise-test-2.appspot.com/api/1.0/client/userV2/logout' + "/%s"%(self.id), 
                              'POST',
                              body=postData,
                              headers=headersData)
            except:
                pass
        elif(len(failedreason) == 0):
            failedreason = "failed at checkAuth %s " % (sessionid)
            if(data != None):
                failedreason += "  " + data
                    
        if(rep != None and data != None and data ==  ")]}',\n{}"): 
            #Success
            print "end %d successfully" % (self.id)
            #threadLock.acquire()
            #successCount += 1
            #threadLock.release()
            return
        elif(len(failedreason) == 0):
            failedreason = "failed at logout %s " % (sessionid)
            
        print "end %d failed-------------------%s--------------" % (self.id, failedreason)
        #threadLock.acquire()
        #failedCount += 1
        #threadLock.release()
        return
    
if __name__=="__main__":    
    jobs = [TestAction(i) for i in range(10)]
    startjobs = [gevent.spawn(ajob.run) for ajob in jobs]
    print "------>>"
    gevent.joinall(startjobs)    
    print "------<<"
    #print "------<< success=%d failed=%d"%(successCount, failedCount)
    