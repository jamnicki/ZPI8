"""epuck_mapping controller."""

from controller import Supervisor  # type: ignore

import requests

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


def run(robot, timestep):
    robot_name = robot.getName()
    robot_node = robot.getFromDef("epuck")
    rotation_field = robot_node.getField("rotation")
    if robot_node is None:
        print("DEF node 'epuck' not found!")

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
        robot_position = robot_node.getPosition()
        robot_rotation = rotation_field.getSFRotation()

        data = {
            "robot_name": robot_name,
            "robot_position": robot_position,
            "robot_rotation": robot_rotation[-1]
        }
        data.update({
            "distance_sensors": {
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
