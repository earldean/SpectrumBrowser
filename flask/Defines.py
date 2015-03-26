'''
Created on Feb 2, 2015

@author: local
'''

SENSOR_ID = "SensorID"
SENSOR_KEY="SensorKey"
SENSOR_ADMIN_EMAIL = "sensorAdminEmail"
SENSOR_STATUS = "sensorStatus"
LOCAL_DB_INSERTION_TIME = "_localDbInsertionTime"
DATA_RETENTION_DURATION_MONTHS = "dataRetentionDurationMonths"
SENSOR_THRESHOLDS = "thresholds"
SENSOR_STREAMING_PARAMS = "streaming"
STREAMING_SAMPLING_INTERVAL_SECONDS = "streamingSamplingIntervalSeconds"
STREAMING_SECONDS_PER_FRAME = "streamingSecondsPerFrame"
STREAMING_CAPTURE_SAMPLE_SIZE_SECONDS = "streamingCaptureSampleSizeSeconds"
STREAMING_FILTER = "streamingFilter"
IS_STREAMING_CAPTURE_ENABLED = "enableStreamingCapture"
LAST_MESSAGE_TYPE = "lastMessageType"
LAST_MESSAGE_DATE = "lastMessageDate"
ENABLED = "ENABLED"
DISABLED = "DISABLED"
LAT = "Lat"
LON = "Lon"
ALT = "Alt"
FFT_POWER = "FFT-Power"
SWEPT_FREQUENCY = "Swept-frequency"

#configuration

UNKNOWN = "UNKNOWN"
API_KEY= "API_KEY"
HOST_NAME = "HOST_NAME"
PUBLIC_PORT= "PUBLIC_PORT"
PROTOCOL= "PROTOCOL"
IS_AUTHENTICATION_REQUIRED = "IS_AUTHENTICATION_REQUIRED"
MY_SERVER_ID = "MY_SERVER_ID" 
MY_SERVER_KEY = "MY_SERVER_KEY" 
SMTP_PORT = "SMTP_PORT"
SMTP_SERVER = "SMTP_SERVER"
SMTP_EMAIL_ADDRESS = "SMTP_EMAIL_ADDRESS"
STREAMING_SERVER_PORT = "STREAMING_SERVER_PORT"
SOFT_STATE_REFRESH_INTERVAL = "SOFT_STATE_REFRESH_INTERVAL"
USE_LDAP = "USE_LDAP"
ACCOUNT_NUM_FAILED_LOGIN_ATTEMPTS = "ACCOUNT_NUM_FAILED_LOGIN_ATTEMPTS"
CHANGE_PASSWORD_INTERVAL_DAYS = "CHANGE_PASSWORD_INTERVAL_DAYS"
ACCOUNT_REQUEST_TIMEOUT_HOURS ="ACCOUNT_REQUEST_TIMEOUT_HOURS"
ACCOUNT_USER_ACKNOW_HOURS="ACCOUNT_USER_ACKNOW_HOURS"
USER_SESSION_TIMEOUT_MINUTES= "USER_SESSION_TIMEOUT_MINUTES"
ADMIN_SESSION_TIMEOUT_MINUTES = "ADMIN_SESSION_TIMEOUT_MINUTES"
CERT = "CERT"
ADMIN = "admin"
USER = "user"

#accounts
ACCOUNT_EMAIL_ADDRESS = "emailAddress"
ACCOUNT_FIRST_NAME = "firstName"
ACCOUNT_LAST_NAME = "lastName"
ACCOUNT_PASSWORD = "password"
ACCOUNT_PRIVILEGE = "privilege"
ACCOUNT_CREATION_TIME = "timeAccountCreated"
ACCOUNT_PASSWORD_EXPIRE_TIME = "timePasswordExpires"
ACCOUNT_NUM_FAILED_LOGINS = "numFailedLoginAttempts"
ACCOUNT_LOCKED = "accountLocked"
TEMP_ACCOUNT_TOKEN = "token"

#accounts, change password:
ACCOUNT_OLD_PASSWORD = "oldPassword"
ACCOUNT_NEW_PASSWORD = "newPassword"

#Message Types

SYS = "Sys"
LOC = "Loc"
DATA = "Data"
CAL = "Cal"
DATA_TYPE = "DataType"
DATA_KEY="_dataKey"
TYPE = "Type"
NOISE_FLOOR = "wnI"
SYS_TO_DETECT="Sys2Detect"
THRESHOLD_DBM_PER_HZ = "thresholdDbmPerHz"
THRESHOLD_MIN_FREQ_HZ = "minFreqHz"
THRESHOLD_MAX_FREQ_HZ = "maxFreqHz"
THRESHOLD_SYS_TO_DETECT = "systemToDetect"
BINARY_INT8 = "Binary - int8"
BINARY_INT16 = "Binary - int16"
BINARY_FLOAT32= "Binary - float32"
ASCII = "ASCII"


# Streaming filter types
MAX_HOLD = "MAX_HOLD"

TIME_ZONE_KEY = "TimeZone"

TWO_HOURS = 2 * 60 * 60
FIFTEEN_MINUTES = 15*60
SECONDS_PER_HOUR = 60*60
HOURS_PER_DAY = 24
MINUTES_PER_DAY = HOURS_PER_DAY * 60
SECONDS_PER_DAY = MINUTES_PER_DAY * 60
MILISECONDS_PER_DAY = SECONDS_PER_DAY * 1000
UNDER_CUTOFF_COLOR = '#D6D6DB'
OVER_CUTOFF_COLOR = '#000000'

EXPIRE_TIME = "expireTime"
ERROR_MESSAGE = "ErrorMessage"
USER_ACCOUNTS = "userAccounts"
STATUS = "status"
STATUS_MESSAGE = "statusMessage"

USER_NAME = "userName"
SESSIONS = "sessions"
SESSION_ID = "sessionId"
SESSION_LOGIN_TIME = "timeLogin"
REMOTE_ADDRESS = "remoteAddress"
