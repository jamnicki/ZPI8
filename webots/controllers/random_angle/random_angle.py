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
from config import (
    DATA_ENDPOINT, SENSORS_ORIENTATION, ROBOT_DIAMETER, DISTANCE_THRESHOLD,
    MATRIX_SIZE, TIME_STEP
)


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

    mid_index = MATRIX_SIZE // 2
    pixel_size = arena_size / MATRIX_SIZE
    robot_pixel_radius = int((ROBOT_DIAMETER / pixel_size) / 2)

    # -1: not discovered, 0: no obstacle, 1: obstacle
    pixels_state = np.full((MATRIX_SIZE, MATRIX_SIZE), -1)

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
        robot_pixel = get_target_pixel(robot_x, robot_y, pixel_size, mid_index)
        robot_pixels = circle_pixels(*robot_pixel, robot_pixel_radius)

        lines_pixels = set()
        obstacle_pixels = set()
        for sensor, value in distance_sensors_values.items():
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

        # send_data(DATA_ENDPOINT.format(name=robot_name), data)

        avoid_obstacles(
            robot, timestep, left_motor, right_motor, distance_sensors_values
        )


def main():
    robot = Supervisor()

    run(robot, TIME_STEP)


if __name__ == "__main__":
    main()
