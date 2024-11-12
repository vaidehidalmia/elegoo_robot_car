import numpy as np
import math
import time

class Robot:
    def __init__(self, initial_position=(0, 0), initial_velocity=(0, 0), cm_to_grid=1):
        self.position = np.array(initial_position, dtype=float)
        self.velocity = np.array(initial_velocity, dtype=float)
        self.yaw = 0.0  # Initial yaw angle in degrees
        self.previous_time = time.time()
        self.cm_to_grid = cm_to_grid 

    def update_motion(self):
        ax, ay, az, gx, gy, gz = cmd(do="measure", what="motion")
        
        # Calculate time elapsed since the last reading
        current_time = time.time()
        dt = current_time - self.previous_time
        self.previous_time = current_time
        
        # Update yaw angle using gyroscope z-axis data (gz) in degrees
        self.yaw += math.degrees(gz * dt)
        self.yaw = self.yaw % 360  # Keep yaw within 0-360 degrees
        print(f"Updated Yaw: {self.yaw:.1f} degrees")

        # Rotate the acceleration vector from the robot's frame to the global frame
        yaw_rad = math.radians(self.yaw)
        global_ax = ax * math.cos(yaw_rad) - ay * math.sin(yaw_rad)
        global_ay = ax * math.sin(yaw_rad) + ay * math.cos(yaw_rad)

        # Update velocity (v = u + at)
        self.velocity[0] += global_ax * dt
        self.velocity[1] += global_ay * dt

        # Update position (s = s0 + v * dt), converting to grid units if necessary
        self.position[0] += self.velocity[0] * dt * self.cm_to_grid
        self.position[1] += self.velocity[1] * dt * self.cm_to_grid

    def get_position(self):
        return tuple(map(int, self.position))  # Rounded position on the grid

    def get_yaw(self):
        return self.yaw