import time
from connection import connect, send_heartbeat, cmd, close_connection

TIME_DELAY = 0.3
NUM_CALIBRATION_READINGS = 5

def calculate_offsets():
    """Calibrates the IMU data by calculating the offset for each of the values"""
    # Initialize sums for accelerometer and gyroscope data
    ax_sum, ay_sum, az_sum = 0, 0, 0
    gx_sum, gy_sum, gz_sum = 0, 0, 0
    
    # Collect multiple readings to calculate average offset
    for _ in range(NUM_CALIBRATION_READINGS):
        motion = cmd(do="measure", what="motion")
        ax_sum += motion[0]
        ay_sum += motion[1]
        az_sum += motion[2]
        gx_sum += motion[3]
        gy_sum += motion[4]
        gz_sum += motion[5]

        send_heartbeat()
        time.sleep(TIME_DELAY)
    
    # Calculate average offsets
    ax_offset = ax_sum / NUM_CALIBRATION_READINGS
    ay_offset = ay_sum / NUM_CALIBRATION_READINGS
    az_offset = az_sum / NUM_CALIBRATION_READINGS
    gx_offset = gx_sum / NUM_CALIBRATION_READINGS
    gy_offset = gy_sum / NUM_CALIBRATION_READINGS
    gz_offset = gz_sum / NUM_CALIBRATION_READINGS
    
    return [ax_offset, ay_offset, az_offset, gx_offset, gy_offset, gz_offset]

connect()
send_heartbeat()
offsets = calculate_offsets()
print(offsets)
close_connection()