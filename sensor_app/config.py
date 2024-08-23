import socket
import logging


DEBUG = True
HOST_BACKEND = "127.0.0.1"
PORT_BACKEND = 32300
# нельзя использовать !? в названии
GROUP = "BATCHNAME"
MACHINE = socket.gethostname()
ALWAYS_RECONNECT = True
RECONNECT_DELAY = 5
LOGFILE = "sensor.log"
LOGLEVEL = logging.DEBUG
SENSOR_CATEGORIES = ["cpu", "net", "mem", "dsk", "gpu"]
