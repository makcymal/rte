import socket
import logging
import json


DEBUG = True
HOST_BACKEND = "127.0.0.1"
PORT_BACKEND = 32300
ALWAYS_RECONNECT = True
RECONNECT_DELAY = 5
LOGFILE = "sensor.log"
LOGLEVEL = logging.DEBUG
SENSOR_CATEGORIES = ["cpu", "net", "ram", "nvm", "gpu", "tmp"]

with open("credentials.json", "r") as creds_file:
    creds = json.load(creds_file)
    
GROUP = creds["group"]
if creds["machine"] == "":
    MACHINE = socket.gethostname()
    creds["machine"] = MACHINE
    with open("credentials.json", "w") as creds_file:
        json.dump(creds, creds_file)
