import time
import numpy as np
import matplotlib.pyplot as plt
import math

from connection import connect, send_heartbeat, cmd, close_connection

TIME_DELAY = 0.5

CM_TO_GRID = 1
GRID_SIZE = (100, 100)

occupancy_grid = np.zeros(GRID_SIZE)
robot_position = [GRID_SIZE[0]//2, GRID_SIZE[1]//2]
heading = 0
yaw = 0.0


previous_time = time.time()
def calculate_yaw():
    global yaw, previous_time
    send_heartbeat() 
    motion = cmd(do="measure", what="motion")
    gz = motion[5]
    
    # Calculate time elapsed since the last reading
    current_time = time.time()
    delta_time = current_time - previous_time
    previous_time = current_time

    # Integrate gyroscope z-axis data to update yaw
    yaw += gz * delta_time
    yaw = yaw % 360

    print(f"Yaw: {yaw:.2f} degrees")
    return yaw


def update_position(robot_distance_travelled):
    global robot_position, heading
    heading += calculate_yaw()  # Update heading with IMU yaw data
    heading = heading % 360 

    # Update robot position based on distance moved
    x_movement = robot_distance_travelled * math.cos(math.radians(heading)) * CM_TO_GRID
    y_movement = robot_distance_travelled * math.sin(math.radians(heading)) * CM_TO_GRID

    # Update the robot's grid position
    robot_position[0] += int(x_movement)
    robot_position[1] += int(y_movement)

def update_map(ultrasound_distance, servo_angle):
    global occupancy_grid, heading, robot_position, GRID_SIZE

    absolute_angle = heading + servo_angle
    absolute_angle = absolute_angle % 360
    servo_angle_rad = math.radians(absolute_angle)
    distance_in_grid = ultrasound_distance * CM_TO_GRID

    x_offset = distance_in_grid * math.cos(servo_angle_rad)
    y_offset = distance_in_grid * math.sin(servo_angle_rad)

    target_x = int(robot_position[0] + x_offset)
    target_y = int(robot_position[1] + y_offset)

    # # Mark path cells as free (set to 1) until the target cell
    # num_steps = int(distance_in_grid)
    # for i in range(num_steps):
    #     free_x = int(robot_position[0] + (x_offset * i / num_steps))
    #     free_y = int(robot_position[1] + (y_offset * i / num_steps))
    #     if 0 <= free_x < GRID_SIZE[0] and 0 <= free_y < GRID_SIZE[1]:
    #         occupancy_grid[free_x, free_y] = 1

    # Mark the target cell as occupied if within grid bounds
    if 0 <= target_x < GRID_SIZE[0] and 0 <= target_y < GRID_SIZE[1]:
        occupancy_grid[target_x, target_y] = -1



"""main"""
servo_angle = 0
connect()
send_heartbeat() 

# for _ in range(10):
#     # dist = cmd(do="measure", what="distance")
#     # print(dist)
#     # motion = cmd(do="measure", what="motion")
#     # print(motion)
#     calculate_yaw()
#     send_heartbeat() 
#     time.sleep(TIME_DELAY)

try:
    plt.ion()
    fig, ax = plt.subplots()

    while servo_angle <= 180:
        cmd(do = "rotate", at = servo_angle)
        dist = cmd(do = "measure", what = "distance")
        print(servo_angle, dist)
        update_map(dist, 90 - servo_angle)

        ax.clear()
        ax.imshow(occupancy_grid, cmap="gray", origin="lower")
        ax.plot(robot_position[0], robot_position[1], "ro")
        plt.pause(TIME_DELAY)
        send_heartbeat() 
        servo_angle += 10
        time.sleep(TIME_DELAY)

finally:
    close_connection()
    plt.ioff()
    plt.show()

