"""zpi_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
from controller import DistanceSensor
from controller import Motion
from controller import Supervisor
import requests
import math
from enum import Enum

import os
import numpy as np


CURRENT_TIME = 0

class robot_State(Enum):
    free_and_90 = 0
    wall_and_90 = 1
    free_and_minus_90 = 2
    wall_and_minus_90 = 3
    free_and_0 = 4

class obstacle_State(Enum):
    up = 0
    down = 1

class robot_controller():
    def __init__(self, robot, world_dim_x, world_dim_y):
        self.x_pos = None
        self.y_pos = None
        self.theta_deg = None
        self.world_dim_x = world_dim_x 
        self.world_dim_y = world_dim_y
        self.node_robot = robot.getFromDef("epuck")
        
        self.left_motor = robot.getDevice('left wheel motor')
        self.right_motor = robot.getDevice('right wheel motor')
        
        self.left_motor.setPosition(float('inf'))
        self.left_motor.setVelocity(0.0)
        
        self.right_motor.setPosition(float('inf'))
        self.right_motor.setVelocity(0.0)

        self.is_rotate = 0
        self.state = None

        self.obstacle_state = None
        
    def update_robot_pose(self):
        robot_position = self.node_robot.getPosition()
        robot_rotation = self.node_robot.getOrientation()
        
        #Transform robot position to 0,0
        self.x_pos = robot_position[0] + self.world_dim_x/2
        self.y_pos = robot_position[1] + self.world_dim_y/2
        self.theta_deg =  math.copysign(1,robot_rotation[3])*math.acos(robot_rotation[0])*180/math.pi
        print("position x: {}, position y: {}, orientation: {}"\
        .format(self.x_pos, self.y_pos, self.theta_deg))
        return self.x_pos, self.y_pos, self.theta_deg
    # set equal velocity on both motors
    def set_velocity(self, velocity):
        if velocity > SPEED:
            velocity = SPEED
        self.left_motor.setVelocity(velocity)
        self.right_motor.setVelocity(velocity)

    # robot is not rotating to given angle but to given global orientation 
    def rotate(self, angle_deg):
        # stop motors
        self.set_velocity(0)
        self.update_robot_pose()
        angle_error = angle_deg - self.theta_deg
        
        if abs(angle_error) >= 1:
            self.is_rotate = 1
            velocity = math.copysign(1,angle_error) * 0.5 
            self.left_motor.setVelocity(-velocity)
            self.right_motor.setVelocity(velocity)
        else:
            pass
            self.is_rotate = 0

def epuck_to_meters(sensor_output: float) -> float:
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


def send_data(url, data):
    try:
        requests.post(url, json=data)
    except Exception as e:
        print(e)


def get_target_pixel(x, y, pixel_size, mid_index):
    if x > 0:
        column = mid_index + (abs(x) // pixel_size)
    elif x < 0:
        column = mid_index - (abs(x) // pixel_size)
    else:
        column = mid_index

    if y > 0:
        row = mid_index - (abs(y) // pixel_size)
    elif y < 0:
        row = mid_index + (abs(y) // pixel_size)
    else:
        row = mid_index

    return int(row), int(column)


def get_line_pixels(x0, y0, x1, y1):
    x0 += 0.5
    y0 += 0.5
    x1 += 0.5
    y1 += 0.5

    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    err = dx + dy  # error value e_xy
    line_pixels = []
    while True:
        # plot(x0, y0);
        line_pixels.append((int(x0 - 0.5), int(y0 - 0.5)))
        # line_pixels.append((x0, y0))
        if (x0 == x1 and y0 == y1):
            break
        e2 = 2*err
        if (e2 >= dy):  # e_xy+e_x > 0
            err += dy
            x0 += sx
        if (e2 <= dx):  # e_xy+e_y < 0
            err += dx
            y0 += sy

    return line_pixels


def circle_pixels(center_col, center_row, radius):
    pixels = set()
    for col in range(center_col - radius, center_col + radius):
        for row in range(center_row - radius, center_row + radius):
            if (col-center_col)**2 + (row-center_row)**2 <= radius**2:
                pixels.add((col, row))
    return pixels


def left_to_right(robot, controller_name):
    own_robot = robot_controller(robot, world_dim_x = WORD_X , world_dim_y = WORD_Y) 

    robot_name = robot.getName()
    rotation_field = own_robot.node_robot.getField("rotation")

    prox_sensors = []
    for ind in range(8):
        sensor_name = 'ps' + str(ind)
        prox_sensors.append(robot.getDevice(sensor_name))
        prox_sensors[ind].enable(TIME_STEP)

    # --------------- pixels init ---------------
    arena_node = robot.getFromDef("arena")
    arena_x, arena_y = arena_node.getField("floorSize").getSFVec2f()
    assert arena_x == arena_y, "The arena must be a square!"
    arena_size = arena_x

    MATRIX_SIZE = 100
    mid_index = MATRIX_SIZE // 2
    pixel_size = arena_size / MATRIX_SIZE
    robot_pixel_radius = int((ROBOT_DIAMETER / pixel_size) / 2)

    # -1: not discovered, 0: no obstacle, 1: obstacle
    pixels_state = np.full((MATRIX_SIZE, MATRIX_SIZE), -1)
    # --------------- pixels init ---------------

    prox_sensors = []
    for ind in range(8):
        sensor_name = 'ps' + str(ind)
        prox_sensors.append(robot.getDevice(sensor_name))
        prox_sensors[ind].enable(TIME_STEP)

    desired_angle_deg = 90
    obstacle_avoidence_duration = DURATION
    while robot.step(TIME_STEP) != -1:
        # --------------- update pixels state ---------------
        robot_x, robot_y, _ = own_robot.node_robot.getPosition()  # x, y, z
        robot_rotation = rotation_field.getSFRotation()

        robot_pixel = get_target_pixel(robot_x, robot_y, pixel_size, mid_index)
        robot_pixels = circle_pixels(*robot_pixel, robot_pixel_radius)

        lines_pixels = set()
        obstacle_pixels = set()
        for sensor, value in {
            f"ps{i}": sensor.getValue()
            for i, sensor in enumerate(prox_sensors)
        }.items():
            val = epuck_to_meters(value)
            deg = robot_rotation[-1]
            x_obstacle = robot_x + (val * np.cos(SENSORS_ORIENTATION[sensor] + deg))
            y_obstacle = robot_y + (val * np.sin(SENSORS_ORIENTATION[sensor] + deg))
            ob_px, ob_py = get_target_pixel(x_obstacle, y_obstacle, pixel_size, mid_index)

            if value > DISTANCE_THRESHOLD:
                obstacle_pixels.add((ob_px, ob_py))

            for line_pixel in get_line_pixels(*robot_pixel, ob_px, ob_py)[:-2]:
                lines_pixels.add(line_pixel)

        changed_pixels = set()

        for pcoords in robot_pixels:
            if not all([0 <= c < MATRIX_SIZE for c in pcoords]):
                continue
            changed_pixels.add(pcoords)
            if pixels_state[pcoords[0]][pcoords[1]] != 1:
                pixels_state[pcoords[0]][pcoords[1]] = 0

        for pcoords in lines_pixels:
            if not all([0 <= c < MATRIX_SIZE for c in pcoords]):
                continue
            changed_pixels.add(pcoords)
            if pixels_state[pcoords[0]][pcoords[1]] != 1:
                pixels_state[pcoords[0]][pcoords[1]] = 0

        for pcoords in obstacle_pixels:
            if not all([0 <= c < MATRIX_SIZE for c in pcoords]):
                continue
            changed_pixels.add(pcoords)
            pixels_state[pcoords[0]][pcoords[1]] = 1
        # --------------- update pixels state ---------------

        # --------------- send data ---------------
        data = {
            "name": controller_name,
            "mapSize": (arena_size, arena_size),
            "matrixSize": (MATRIX_SIZE, MATRIX_SIZE),
            "pixels": [
                {"pos": (i, j), "state": int(pixels_state[i][j])}
                for (i, j) in changed_pixels
            ],
            "pos": (robot_x, robot_y),
            "deg": robot_rotation[-1]
        }
        data.update({
            "sensors": {
                f"ps{i}": epuck_to_meters(sensor.getValue())
                for i, sensor in enumerate(prox_sensors)
            }
        })

        send_data(DATA_ENDPOINT.format(name=robot_name), data)
        # --------------- send data ---------------

        # print(own_robot.state)
        own_robot.update_robot_pose()

        own_robot.rotate(desired_angle_deg)
        if not own_robot.is_rotate:
            if own_robot.state == robot_State.free_and_90 or own_robot.state == robot_State.free_and_minus_90:
                own_robot.set_velocity(SPEED)

            if own_robot.state == robot_State.free_and_0:
                if obstacle_avoidence_duration > 0:
                    own_robot.set_velocity(SPEED)
                    obstacle_avoidence_duration -= TIME_STEP/1000
                else:
                    if own_robot.obstacle_state == obstacle_State.up:
                        desired_angle_deg = -90 
                    if own_robot.obstacle_state == obstacle_State.down:
                        desired_angle_deg = 90 

        if (prox_sensors[0].getValue() > 140) or (prox_sensors[7].getValue() > 140):
            # print("WALL DETECTED")
            own_robot.update_robot_pose()
            if(abs(90 - own_robot.theta_deg) < 1):
                own_robot.state = robot_State.wall_and_90
                own_robot.obstacle_state = obstacle_State.up

            if(abs(-90 - own_robot.theta_deg) < 1):
                own_robot.state = robot_State.wall_and_minus_90
                own_robot.obstacle_state = obstacle_State.down

            if own_robot.state == robot_State.wall_and_90 or own_robot.state == robot_State.wall_and_minus_90:
                desired_angle_deg = 0

        else:
            if(abs(90 - own_robot.theta_deg) < 1):
                own_robot.state = robot_State.free_and_90
                obstacle_avoidence_duration = DURATION
            if(abs(-90 - own_robot.theta_deg) < 1):
                own_robot.state = robot_State.free_and_minus_90
                obstacle_avoidence_duration = DURATION
            if(abs(0 - own_robot.theta_deg) < 1):
                own_robot.state = robot_State.free_and_0
        x, y, theta = own_robot.update_robot_pose()
        if x > WORD_X-0.1 and y > WORD_Y-0.1:
            break
    return False

WORD_X = 1.5
WORD_Y = 1.5
SPEED = 2
DURATION = 1
TIME_STEP = 32

HOST = "localhost"
PORT = 8000

# e-puck0, e-puck1, e-puck2, ...
DATA_ENDPOINT = f"http://{HOST}:{PORT}" + "/robot/{name}"

DISTANCE_THRESHOLD = 100
ROBOT_DIAMETER = 0.074  # m
SENSORS_ORIENTATION = {
    "ps0": 1.27,
    "ps1": 0.77,
    "ps2": 0.00,
    "ps3": 5.21,
    "ps4": 4.21,
    "ps5": 3.14159,
    "ps6": 2.37,
    "ps7": 1.87
}
