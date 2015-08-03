'''
Created on Jan 26, 2015

@author: mranga
'''
import Accounts
import DbCollections
import msgutils
import SessionLock
import pymongo
import authentication
import argparse
import os
import signal
import util
from DataStreamSharedState import MemCache

from Sensor import Sensor
from Defines import SENSOR_ID
from Defines import SENSOR_KEY
from Defines import SENSOR_STATUS
from Defines import ENABLED
from Defines import DISABLED
from Defines import STATUS
from Defines import OK
from Defines import NOK
from Defines import ERROR_MESSAGE
from Defines import IS_STREAMING_ENABLED



def getAllSensors():
    sensors = []
    for sensor in DbCollections.getSensors().find() :
        sensorObj = Sensor(sensor)
        sensors.append(sensorObj.getSensor())
    return sensors

def getAllSensorIds():
    sensorIds = []
    for sensor in DbCollections.getSensors().find() :
        sensorIds.append(sensor[SENSOR_ID])

def checkSensorConfig(sensorConfig):
    if not SENSOR_ID in sensorConfig \
    or not SENSOR_KEY in sensorConfig \
    or not "sensorAdminEmail" in sensorConfig \
    or not "dataRetentionDurationMonths" in sensorConfig :
        return False, {STATUS:"NOK", "StatusMessage":"Missing required information"}
    else:
        return True, {STATUS:"OK"}

def addSensor(sensorConfig):
    status, msg = checkSensorConfig(sensorConfig)
    if not status:
        msg["sensors"] = getAllSensors()
        return msg
    sensorId = sensorConfig[SENSOR_ID]
    sensor = DbCollections.getSensors().find_one({SENSOR_ID:sensorId})
    if sensor != None:
        return {STATUS:"NOK", "StatusMessage":"Sensor already exists", "sensors":getAllSensors()}
    else:
        sensorConfig[SENSOR_STATUS] = ENABLED
        DbCollections.getSensors().insert(sensorConfig)
        sensors = getAllSensors()
        dataPosts = DbCollections.getDataMessages(sensorId)
        dataPosts.ensure_index([('t', pymongo.ASCENDING), ("seqNo", pymongo.ASCENDING)])
        return {STATUS:"OK", "sensors":sensors}
        
def getSystemMessage(sensorId):
    query = {SENSOR_ID:sensorId}
    record = DbCollections.getSensors().find_one(query)
    if record == None:
        return {STATUS:"NOK", "StatusMessage":"Sensor not found"}
    else:
        systemMessage = record["systemMessage"]
        if systemMessage == None:
            return {STATUS:"NOK", "StatusMessage":"System Message not found"}
        
def addDefaultOccupancyCalculationParameters(sensorId, jsonData):
    sensorRecord = DbCollections.getSensors().find_one({SENSOR_ID:sensorId})
    if sensorRecord == None:
        return {STATUS:"NOK", "StatusMessage":"Sensor Not Found"}
    sensorRecord["defaultOccupancyCalculationParameters"] = jsonData
    recordId = sensorRecord["_id"]
    del sensorRecord["_id"]
    DbCollections.getSensors().update({"_id":recordId}, sensorRecord, upsert=False)
    return {STATUS:"OK"}

def removeAllSensors():
    DbCollections.getSensors().drop()


def removeSensor(sensorId):
    SessionLock.acquire()
    try:
        userSessionCount = SessionLock.getUserSessionCount()
        if userSessionCount != 0 :
            return {STATUS:"NOK", "ErrorMessage":"Active user session detected"}
        sensor = DbCollections.getSensors().find_one({SENSOR_ID:sensorId})
        if sensor == None:
            return {STATUS:"NOK", "StatusMessage":"Sensor Not Found", "sensors":getAllSensors()}
        else:
            DbCollections.getSensors().remove(sensor)
            sensors = getAllSensors()
            return {STATUS:"OK", "sensors":sensors}
    finally:
        SessionLock.release()
    
def getSensors():
    sensors = getAllSensors()
    return {STATUS:"OK", "sensors":sensors}

def printSensors():
    import json
    sensors = getAllSensors()
    for sensor in sensors:
        print json.dumps(sensor, indent=4)

def getSensor(sensorId):
    sensor = DbCollections.getSensors().find_one({SENSOR_ID:sensorId})
    if sensor == None:
        return None
    else:
        return Sensor(sensor).getSensor()
    
def getSensorObj(sensorId):
    sensor = DbCollections.getSensors().find_one({SENSOR_ID:sensorId})
    if sensor == None:
        return None
    else:
        return Sensor(sensor)
    
def getSensorConfig(sensorId):
    util.debugPrint("SensorDb:getSensorConfig: " + sensorId)
    sensor = DbCollections.getSensors().find_one({SENSOR_ID:sensorId})
    if sensor == None:
        return {STATUS:NOK, ERROR_MESSAGE:"Sensor not found " + sensorId}
    else:
        del sensor[SENSOR_KEY]
        del sensor["_id"]
        return {STATUS:OK, "sensorConfig":sensor}
        


        
def purgeSensor(sensorId):
    SessionLock.acquire()
    try :
        userSessionCount = SessionLock.getUserSessionCount()
        if userSessionCount != 0 :
            return {STATUS:"NOK", "ErrorMessage":"Active user session detected"}
        restartSensor(sensorId)
        DbCollections.getSensors().remove({SENSOR_ID:sensorId})
        systemMessages = DbCollections.getSystemMessages().find({SENSOR_ID:sensorId})
        # The system message can contain cal data.
        for systemMessage in systemMessages:
            msgutils.removeData(systemMessage)
        DbCollections.getSystemMessages().remove({SENSOR_ID:sensorId})
        dataMessages = DbCollections.getDataMessages(sensorId).find({SENSOR_ID:sensorId})
        # remove data associated with data messages.
        for dataMessage in dataMessages:
            msgutils.removeData(dataMessage)   
        DbCollections.getDataMessages(sensorId).remove({SENSOR_ID:sensorId})
        DbCollections.dropDataMessages(sensorId)
        # Location messages contain no associated data.
        DbCollections.getLocationMessages().remove({SENSOR_ID:sensorId})
        sensors = getAllSensors()
        return {STATUS:"OK", "sensors":sensors}
    finally:
        SessionLock.release()

def toggleSensorStatus(sensorId):
    sensor = DbCollections.getSensors().find_one({SENSOR_ID:sensorId})
    currentStatus = sensor[SENSOR_STATUS]
    if currentStatus == DISABLED:
        newStatus = ENABLED
    else:
        newStatus = DISABLED
        restartSensor(sensorId)
    DbCollections.getSensors().update({"_id":sensor["_id"]}, {"$set":{SENSOR_STATUS:newStatus}}, upsert=False)
    sensors = getAllSensors()
    return {STATUS:"OK", "sensors":sensors}

def postError(sensorId, errorStatus):
    sensor = DbCollections.getSensors().find_one({SENSOR_ID:sensorId})
    if not "SensorKey" in errorStatus:
        return {STATUS:"NOK", "ErrorMessage":"Authentication failure - sensor key not provided"}
    if sensor == None:
        return {STATUS:"NOK", "ErrorMessage":"Sensor not found"}
    if not authentication.authenticateSensor(sensorId, errorStatus[SENSOR_KEY]):
        return {STATUS:"NOK", "ErrorMessage":"Authentication failure"}
    DbCollections.getSensors().update({"_id":sensor["_id"]}, {"$set":{"SensorError":errorStatus["ErrorMessage"]}}, upsert=False)
    return {STATUS:OK}

def restartSensor(sensorId):
    memCache = MemCache()
    pid = memCache.getStreamingServerPid(sensorId)
    if pid != -1:
        try:
            util.debugPrint("restartSensor : sensorId " + sensorId + " pid " + str(pid) + " sending sigint")
            os.kill(pid, signal.SIGINT)
        except:
            util.errorPrint("restartSensor: Pid " + str(pid) + " not found")
    else:
        util.debugPrint("restartSensor: pid not found")
 
def updateSensor(sensorConfigData):
    status, msg = checkSensorConfig(sensorConfigData)
    if not status:
        msg["sensors"] = getAllSensors()
        return msg
    sensorId = sensorConfigData[SENSOR_ID]
    DbCollections.getSensors().remove({SENSOR_ID:sensorId})
    DbCollections.getSensors().insert(sensorConfigData)
    sensors = getAllSensors()
    if sensorConfigData[IS_STREAMING_ENABLED]:
        restartSensor(sensorId)
    return {STATUS:"OK", "sensors":sensors}

    
def startSensorDbScanner():
    tempSensors = DbCollections.getTempSensorsCollection()
    Accounts.removeExpiredRows(tempSensors)
    
def add_sensors(filename):   
    with open(filename, 'r') as f:
        data = f.read()
    sensors = eval(data)
    for sensor in sensors:
        addSensor(sensor)

# Note this is for manual deletion of all sensors for testing starting from scratch.
def deleteAllSensors():
    DbCollections.getSensors().remove({})

 # Self initialization scaffolding code.
if __name__ == "__main__":
   
    parser = argparse.ArgumentParser(description='Process command line args')
    parser.add_argument('action', default="init", help="init (default)")
    parser.add_argument('-f', help='sensors file')
    args = parser.parse_args()
    action = args.action
    if args.action == "init" or args.action == None:
        sensorsFile = args.f
        if sensorsFile == None:
            parser.error("Please specify sensors file")
        deleteAllSensors() 
        add_sensors(sensorsFile)
    else:
        parser.error("Unknown option " + args.action)
    
    

    
        
        
