import socket


DEBUG = True
HOST_BACKEND = "127.0.0.1"
PORT_BACKEND = 32300
# нельзя использовать !? в названии
BATCH = "gvr:knl"
LABEL = socket.gethostname()
ALWAYS_RECONNECT = True
RECONNECT_DELAY = 5
