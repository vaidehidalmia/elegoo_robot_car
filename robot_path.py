import time
import numpy as np
import matplotlib.pyplot as plt
import math

from connection import connect, send_heartbeat, cmd, close_connection
from robot_position import Robot

TIME_DELAY = 0.5
CM_TO_GRID = 1
GRID_SIZE = (100, 100)

occupancy_grid = np.zeros(GRID_SIZE)
car = Robot(initial_position=(10, 10), initial_velocity=(0, 0), cm_to_grid=1)

connect()
send_heartbeat() 

yaw = car.get_yaw()
while yaw < 180:
    print(yaw)
    cmd(do="move", where="left")
    send_heartbeat()
    imu_data = cmd(do="measure", what="motion")
    time.sleep(0.05)
    cmd(do="stop")
    car.update_position(imu_data)
    # print(car.get_position())
    yaw = car.get_yaw()
print(yaw)

close_connection()




