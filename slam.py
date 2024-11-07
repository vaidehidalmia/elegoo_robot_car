import socket
import json
import time
import re
import sys

# Configuration Constants
IP_ADDRESS = "192.168.4.1"
PORT = 100
RECV_BUFFER_SIZE = 2048
HEARTBEAT_MSG = "{Heartbeat}"
RETRIES = 3
TIME_DELAY = 0.5

connection = None
cmd_no = 0

def initialize_socket():
    """Initializes a new socket connection."""
    return socket.socket()

def connect():
    """Attempts to establish a connection to the server."""
    global connection
    connection = initialize_socket()
    try:
        print(f"Connecting to {IP_ADDRESS}:{PORT}")
        connection.connect((IP_ADDRESS, PORT))
        print("Connected!")
    except Exception as e:
        print("Connection failed:", e)

def check_for_heartbeat():
    """Checks for incoming heartbeat messages from the server."""
    try:
        data = connection.recv(RECV_BUFFER_SIZE).decode()
        print("Received:", data)
    except Exception as e:
        print("Error receiving heartbeat:", e)    

def send_heartbeat():
    """Sends a heartbeat message to keep the connection alive."""
    try:
        connection.send(HEARTBEAT_MSG.encode())
    except Exception as e:
        print("Failed to send heartbeat:", e)

def send_cmd(msg, retries=RETRIES):
    """Sends a command to the server and retries if needed."""
    global connection
    msg_json = json.dumps(msg)
    attempts = 0
    res = None

    while attempts < retries:
        try:
            connection.send(msg_json.encode())  
            res = connection.recv(RECV_BUFFER_SIZE).decode()
            if "Heartbeat" in res:
                res = connection.recv(RECV_BUFFER_SIZE).decode()
            if "_" in res:
                break  # Exit on valid response
        except (socket.error, BrokenPipeError):
            attempts += 1
            print(f"Error sending command: {sys.exc_info()[0]}")
            print("Retrying command due to BrokenPipeError...")
            time.sleep(TIME_DELAY)
            connect()
        else:
            break

    if attempts == retries:
        print(f"Failed to send command after {retries} attempts.")
        print("Error:", sys.exc_info()[0])

    return parse_response(res)

def parse_response(response):
    """Parses the response to extract a meaningful result."""
    if response and "Heartbeat" not in response:
        match = re.search("_(.*)}", response)
        if match:
            result = match.group(1)
            if result == "ok" or result == "true":
                return 1
            elif result == "false":
                return 0
            elif "," in result:
                result = result.split(",")
                return [int(i) for i in result]
            else:
                return int(result)
    return None

def cmd(do, what="", where="", at=""):
    """Constructs and sends a command to the server based on parameters."""
    global cmd_no
    cmd_no += 1
    msg = {"H": str(cmd_no)}

    if do == "move":
        msg.update({"N": 3, "D2": 100})
        if where == "forward":
            msg["D1"] = 3
        elif where == "back":
            msg["D1"] = 4
        elif where == "left":
            msg["D1"] = 1
        elif where == "right":
            msg["D1"] = 2
    elif do == "stop":
        msg.update({"N": 1, "D1": 0, "D2": 0, "D3": 1})
    elif do == "rotate":
        msg.update({"N": 5, "D1": 1, "D2": at})
    elif do == "measure":
        if what == "distance":
            msg.update({"N": 21, "D1": 2})
        elif what == "motion":
            msg["N"] = 6
    elif do == "check":
        msg["N"] = 23
   
    return send_cmd(msg)


connect()
while 1:
    send_heartbeat() 
    dist = cmd(do = "measure", what = "distance")
    motion = cmd(do = "measure", what = "motion")
    print(dist)
    print(motion)
    time.sleep(TIME_DELAY)
connection.close()