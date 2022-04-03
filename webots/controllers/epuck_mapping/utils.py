from math import radians

from config import INITIAL_VELOCITY, DISTANCE_THRESHOLD, MAX_ROTATION_SPEED


def enable_devices(devices, timestep):
    for device in devices:
        device.enable(timestep)


def initialize_devices(devices, motors, timestep):
    enable_devices(devices, timestep)
    # Disable motor PID control mode.
    for motor in motors:
        motor.setPosition(float('inf'))
        motor.setVelocity(INITIAL_VELOCITY)


def get_distance_sensors(robot):
    return {f"ps{i}": robot.getDevice(f"ps{i}") for i in range(8)}


def get_motors(robot):
    return (
        robot.getDevice("left wheel motor"),
        robot.getDevice("right wheel motor")
    )


def get_sensors_values(sensors):
    return {
        name: device.getValue()
        for name, device in sensors.items()
    }


def obstacle_detected(distance_sensors_values):
    return {
        sensor_name: value > DISTANCE_THRESHOLD
        for sensor_name, value in distance_sensors_values.items()
    }


def calc_rotation_time(degress):
    return abs(radians(degress)) / MAX_ROTATION_SPEED


def epuck_to_meters(sensor_output: int) -> float: 
    """
    Convert epuck robot sensor output value to meters 
    
    param::sensor_output:: sensor output value
    return:: distance in meters 
    
    """
    
    if sensor_output >= 3474:
        return -(sensor_output-4095)/124200
    elif sensor_output < 34:
        return 0.07
    else:
        return 19.84698335/(sensor_output + 281.80449003)
