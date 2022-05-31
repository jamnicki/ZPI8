"""epuck_mapping controller."""

from controller import Supervisor  # type: ignore

import requests
import os
import numpy as np

from utils import (
    initialize_devices, get_distance_sensors, get_motors, get_sensors_values,
    epuck_to_meters
)
from action import avoid_obstacles
from config import DATA_ENDPOINT


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


def run(robot, timestep):
    robot_name = robot.getName()
    robot_node = robot.getFromDef("epuck")
    rotation_field = robot_node.getField("rotation")
    if robot_node is None:
        print("DEF node 'epuck' not found!")

    arena_node = robot.getFromDef("arena")
    arena_x, arena_y = arena_node.getField("floorSize").getSFVec2f()
    assert arena_x == arena_y, "The arena must be a square!"
    arena_size = arena_x

    controller_name = os.path.basename(__file__).split(".")[0]

    MATRIX_SIZE = 100
    mid_index = MATRIX_SIZE // 2
    pixel_size = arena_size / MATRIX_SIZE

    # -1: not discovered, 0: no obstacle, 1: obstacle
    pixels_state = np.full((MATRIX_SIZE, MATRIX_SIZE), -1)
    # pixels_range = get_pixel_range(MATRIX_SIZE, arena_size, pixel_size)

    distance_sensors = get_distance_sensors(robot)
    left_motor, right_motor = get_motors(robot)

    initialize_devices(
        devices=distance_sensors.values(),
        motors=(left_motor, right_motor),
        timestep=timestep
    )

    i = 0
    while robot.step(timestep) != -1:
        i += 1
        if i % 3:
            continue
        distance_sensors_values = get_sensors_values(distance_sensors)
        robot_rotation = rotation_field.getSFRotation()
        robot_x, robot_y, _ = robot_node.getPosition()  # x, y, z

        # ####### update pixels state #######
        robot_pixels = set()
        robot_pixels.add(get_target_pixel(robot_x, robot_y, pixel_size, mid_index))

        changed_pixels = set()
        for pcoords in robot_pixels:
            changed_pixels.add(pcoords)
            pixels_state[pcoords[0]][pcoords[1]] = 0
        # ####################################

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
                sensor: epuck_to_meters(value)
                for sensor, value in distance_sensors_values.items()
            }
        })

        send_data(DATA_ENDPOINT.format(name=robot_name), data)

        avoid_obstacles(
            robot, timestep, left_motor, right_motor, distance_sensors_values
        )


def main():
    robot = Supervisor()
    timestep = int(robot.getBasicTimeStep())

    run(robot, timestep)


if __name__ == "__main__":
    main()
