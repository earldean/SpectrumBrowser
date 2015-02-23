from flask import jsonify
import random
import util
import Config
import time
import threading
import Accounts
import sys
import traceback
import AccountLock
import DbCollections
import DebugFlags
import json

from Defines import TWO_HOURS
from Defines import FIFTEEN_MINUTES
from Defines import SIXTY_DAYS
from Defines import EXPIRE_TIME
from Defines import USER_NAME


from Defines import SENSOR_ID
from Defines import SENSOR_KEY
from Defines import ENABLED
from Defines import SENSOR_STATUS

import SessionLock



def checkSessionId(sessionId):
 
    sessionFound = False
    if DebugFlags.disableSessionIdCheck :
        sessionFound = True
    else:
        SessionLock.acquire() 
        try :
            session = SessionLock.getSession(sessionId)
            if session <> None:
                sessionFound = True
                if sessionId.startswith("user"):
                    delta = TWO_HOURS
                else:
                    delta = FIFTEEN_MINUTES
                expireTime = time.time() + delta
                session[EXPIRE_TIME] = expireTime
                SessionLock.updateSession(session)
                util.debugPrint("updated session ID expireTime")
        except:
            util.debugPrint("Problem checking sessionKey " + sessionId)
        finally:
            SessionLock.release()  
    return sessionFound

# Place holder. We need to look up the database for whether or not this is a valid sensor key.
def authenticateSensor(sensorId, sensorKey):
    record = DbCollections.getSensors().find_one({SENSOR_ID:sensorId,SENSOR_KEY:sensorKey})
    if record != None and record[SENSOR_STATUS] == ENABLED : 
        return True
    else:
        return False
    
def logOut(sessionId):
    SessionLock.acquire() 
    logOutSuccessful = False
    try :
        util.debugPrint("Logging off " + sessionId)
        session =SessionLock.getSession(sessionId) 
        if session == None:
            util.debugPrint("When logging off could not find the following session key to delete:" + sessionId)
        else:
            SessionLock.removeSession(session["sessionId"])
            logOutSuccessful = True
    except:
        util.debugPrint("Problem logging off " + sessionId)
    finally:
        SessionLock.release() 
    return logOutSuccessful

def authenticatePeer(peerServerId, password):
    peerRecord = Config.findInboundPeer(peerServerId)
    if peerRecord == None:
        return False
    else:
        return password == peerRecord["key"]

def generateGuestToken():
    sessionId = generateSessionKey("user")
    addedSuccessfully = addSessionKey(sessionId, "guest")
    return sessionId

def generatePeerSessionKey():
    sessionId = generateSessionKey("peer")
    addSessionKey(sessionId, "peerUser")

def generateSessionKey(privilege):
    util.debugPrint("generateSessionKey ")
    try:
        sessionId = -1
        uniqueSessionId = False
        num = 0
        SessionLock.acquire()
        # try 5 times to get a unique session id
        while (not uniqueSessionId) and (num < 5):
            # JEK: I used time.time() as my random number so that if a user wants to create
            # DbCollections.getSessions() from 2 browsers on the same machine, the time should ensure uniqueness
            # especially since time goes down to msecs.
            # JEK I am thinking that we do not need to add remote_address to the sessionId to get uniqueness,
            # so I took out +request.remote_addr
            sessionId = privilege + "-" + str("{0:.6f}".format(time.time())).replace(".", "") + str(random.randint(1, 100000))
            util.debugPrint("SessionKey in loop = " + str(sessionId))            
            session = SessionLock.getSession(sessionId)
            if session == None:
                uniqueSessionId = True       
            else:
                num = num + 1
        if num == 5:
            util.debugPrint("Fix unique session key generation code. We tried 5 times to get a unique session key and then we gave up.") 
            sessionId = -1
    except:     
        util.debugPrint("Problem generating sessionKey " + str(sessionId))  
        sessionId = -1
    finally:
        SessionLock.release() 
    util.debugPrint("SessionKey = " + str(sessionId))      
    return sessionId   

def addSessionKey(sessionId, userName):
    util.debugPrint("addSessionKey")
    if sessionId <> -1:
        SessionLock.acquire()
        try :
            session = SessionLock.getSession(sessionId) 
            if session == None:
                #expiry time for Admin is 15 minutes.
                if sessionId.startswith("admin"):
                    delta = FIFTEEN_MINUTES
                else:
                    delta = TWO_HOURS
                newSession = {"sessionId":sessionId, USER_NAME:userName, "timeLogin":time.time(), EXPIRE_TIME:time.time() + delta}
                SessionLock.addSession(newSession)
                return True
            else:
                util.debugPrint("session key already exists, we should never reach since only should generate unique session keys")
                return False
        except:
            util.debugPrint("Problem adding sessionKey " + sessionId)
            return False
        finally:
            SessionLock.release()      
    else:
        return False
 
def IsAccountLocked(userName):
    AccountLocked = False
    if Config.isAuthenticationRequired():
        AccountLock.acquire()
        try :
            existingAccount = DbCollections.getAccounts().find_one({"emailAddress":userName})    
            if existingAccount <> None:               
                if existingAccount["AccountLocked"] == True:
                    AccountLocked = True
        except:
            util.debugPrint("Problem authenticating user " + userName )
        finally:
            AccountLock.release()   
    return AccountLocked
    
def authenticate(privilege, userName, password):
    print userName, password, Config.isAuthenticationRequired()
    authenicationSuccessful = False
    util.debugPrint("authenticate check database")
    if not Config.isAuthenticationRequired() and privilege == "user":
        authenicationSuccessful = True
    elif not Config.isConfigured() and privilege == "admin":
        if userName == Config.getDefaultAdminEmailAddress() and password == Config.getDefaultAdminPassword():
            authenicationSuccessful = True
        else:
            authenicationSuccessful = False
    else:
        AccountLock.acquire()
        try :
            util.debugPrint("finding existing account")
            existingAccount = DbCollections.getAccounts().find_one({"emailAddress":userName, "password":password, "privilege":privilege})
            if existingAccount == None and privilege == "user":
                existingAccount = DbCollections.getAccounts().find_one({"emailAddress":userName, "password":password})
                if existingAccount != None and existingAccount["privilege"] != "admin":
                    existingAccount = None
                    
            if existingAccount == None:
                util.debugPrint("did not find email and password ") 
                existingAccount = DbCollections.getAccounts().find_one({"emailAddress":userName})    
                if existingAccount != None :
                    util.debugPrint("account exists, but user entered wrong password or attempted admin log in")                    
                    numFailedLoggingAttempts = existingAccount["numFailedLoggingAttempts"] + 1
                    existingAccount["numFailedLoggingAttempts"] = numFailedLoggingAttempts
                    if numFailedLoggingAttempts == 5:                 
                        existingAccount["AccountLocked"] = True 
                    DbCollections.getAccounts().update({"_id":existingAccount["_id"]}, {"$set":existingAccount}, upsert=False)                           
            else:
                util.debugPrint("found email and password ") 
                if existingAccount["AccountLocked"] == False:
                    util.debugPrint("user passed login authentication.")           
                    existingAccount["numFailedLoggingAttempts"] = 0
                    existingAccount["AccountLocked"] = False 
                    # Place-holder. We need to access LDAP (or whatever) here.
                    DbCollections.getAccounts().update({"_id":existingAccount["_id"]}, {"$set":existingAccount}, upsert=False)
                    util.debugPrint("user login info updated.")
                    authenicationSuccessful = True
        except:
            util.debugPrint("Problem authenticating user " + userName + " password: " + password)
            print "Unexpected error:", sys.exc_info()[0]
            print sys.exc_info()
            traceback.print_exc()
        finally:
            AccountLock.release()    
    return authenicationSuccessful

def authenticateUser(privilege, userName, password):
    """
     Authenticate a user given a requested privilege, userName and password.
    """
    util.debugPrint("authenticateUser: " + userName + " privilege: " + privilege + " password " + password)
    if privilege == "admin" or privilege == "user":
        if IsAccountLocked(userName):
            return jsonify({"status":"ACCLOCKED", "sessionId":"0"})
        else:
            # Authenticate will will work whether passwords are required or not (authenticate = true if no pwd req'd)
            # Only one admin login allowed at a given time.
            if privilege == "admin" and SessionLock.getAdminSessionCount() != 0:
                return jsonify({"status":"NOSESSIONS","sessionId":"0"})
            if authenticate(privilege, userName, password) :
                sessionId = generateSessionKey(privilege)
                addedSuccessfully = addSessionKey(sessionId, userName)
                if addedSuccessfully:
                    return jsonify({"status":"OK", "sessionId":sessionId})
                else:
                    return jsonify({"status":"INVALSESSION", "sessionId":"0"})
            else:
                util.debugPrint("invalid user will be returned: ")
                return jsonify({"status":"INVALUSER", "sessionId":"0"})   
    else:
        # q = urlparse.parse_qs(query,keep_blank_values=True)
        # TODO deal with actual logins consult user database etc.
        return jsonify({"status":"NOK", "sessionId":"0"}), 401

# TODO -- this will be implemented after the admin stuff
# has been implemented.
def isUserRegistered(emailAddress):
    UserRegistered = False
    if Config.isAuthenticationRequired():
        AccountLock.acquire()
        try :
            existingAccount = DbCollections.getAccounts().find_one({"emailAddress":emailAddress})
            if existingAccount <> None:
                UserRegistered = True
        except:
            util.debugPrint("Problem checking if user is registered " + emailAddress)
        finally:
            AccountLock.release()    

    return UserRegistered




