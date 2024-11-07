import socket
import numpy as np

connection = socket.socket()
cmd_no = 0

def connect():
    global connection
    ip = "192.168.4.1"
    port = 100
    connection.close()  
    connection = socket.socket()  
    try:
        print('Connecting {0}:{1}'.format(ip, port))
        connection.connect((ip, port))
        print("Connected!")
    except Exception as e:
        print("Connection failed:", e)

def check_for_heartbeat():
    global connection
    try:
        data = connection.recv(2048).decode()
        print("Received: ", data)
    except Exception as e:
        print("Error: ", e)
    

def send_heartbeat():
    global connection
    heartbeat_msg = "{Heartbeat}"
    connection.send(heartbeat_msg.encode())




connect()
send_heartbeat()
check_for_heartbeat()
connection.close()