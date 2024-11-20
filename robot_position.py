import numpy as np
import math
import time

class Robot:
    def __init__(self, initial_position=(10, 10), initial_velocity=(0, 0), cm_to_grid=1):
        self.position = np.array(initial_position, dtype=float)
        self.velocity = np.array(initial_velocity, dtype=float)
        self.yaw = 0.0  # Initial yaw angle in degrees
        self.previous_time = time.time()
        self.cm_to_grid = cm_to_grid 

    def update_position(self, imu_data):
        ax, ay, az, gx, gy, gz = imu_data
        
        # Calculate time elapsed since the last reading
        current_time = time.time()
        dt = current_time - self.previous_time
        self.previous_time = current_time
        
        # Update yaw angle using gyroscope z-axis data (gz) in degrees
        self.yaw += gz * dt
        self.yaw = round(self.yaw % 360)  # Keep yaw within 0-360 degrees

        # Rotate the acceleration vector from the robot's frame to the global frame
        yaw_rad = math.radians(self.yaw)
        rotation_matrix = np.array([
            [np.cos(yaw_rad), -np.sin(yaw_rad)],
            [np.sin(yaw_rad), np.cos(yaw_rad)]
        ])
        
        local_acceleration = np.array([ax, ay])
        global_acceleration = rotation_matrix @ local_acceleration
        
        # Update velocity (v = u + at)
        self.velocity += global_acceleration * dt
        
        # Update position (s = s0 + v * dt), converting to grid units if necessary
        self.position += self.velocity * dt * self.cm_to_grid
        

    def get_position(self):
        return tuple(map(int, self.position))  # Rounded position on the grid

    def get_yaw(self):
        return self.yaw