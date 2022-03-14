import time
import random

from utils import calc_rotation_time, obstacle_detected
from config import INITIAL_VELOCITY, MAX_MOTOR_VELOCITY


def move_forward(left_motor, right_motor):
    left_motor.setVelocity(INITIAL_VELOCITY)
    right_motor.setVelocity(INITIAL_VELOCITY)


def stop(left_motor, right_motor):
    left_motor.setVelocity(0)
    right_motor.setVelocity(0)


def rotate_left(left_motor, right_motor):
    left_motor.setVelocity(-MAX_MOTOR_VELOCITY)
    right_motor.setVelocity(MAX_MOTOR_VELOCITY)


def rotate_right(left_motor, right_motor):
    left_motor.setVelocity(MAX_MOTOR_VELOCITY)
    right_motor.setVelocity(-MAX_MOTOR_VELOCITY)


def rotate_degress(robot, timestep, left_motor, right_motor, degress):
    t0 = time.time()
    rotate_duration = calc_rotation_time(degress)
    if degress > 0:
        rotate = rotate_right
    elif degress < 0:
        rotate = rotate_left

    rotate(left_motor, right_motor)
    while time.time() - t0 < rotate_duration:
        robot.step(timestep)

    stop(left_motor, right_motor)


def avoid_obstacles(
    robot, timestep, left_motor, right_motor, distance_sensors_values
):
    obstacle = obstacle_detected(distance_sensors_values)
    if obstacle["ps1"] and obstacle["ps6"]:
        rotate_degress(
            robot, timestep, left_motor, right_motor,
            degress=180
        )
    elif obstacle["ps0"] or obstacle["ps1"]:
        # rotate left
        rotate_degress(
            robot, timestep, left_motor, right_motor,
            degress=random.uniform(-20, -1)
        )
    elif obstacle["ps6"] or obstacle["ps7"]:
        # rotate right
        rotate_degress(
            robot, timestep, left_motor, right_motor,
            degress=random.uniform(1, 20)
        )
    else:
        move_forward(left_motor, right_motor)
