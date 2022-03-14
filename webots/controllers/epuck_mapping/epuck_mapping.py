"""epuck_mapping controller."""

from controller import Supervisor  # type: ignore

from utils import (
    initialize_devices, get_distance_sensors, get_motors, get_sensors_values
)
from action import avoid_obstacles
from config import DATA_ENDPOINT


def send_data(url, data):
    pass


def run(robot, timestep):
    robot_name = robot.getName()
    robot_node = robot.getFromDef("epuck")
    if robot_node is None:
        print("DEF node 'epuck' not found!")

    distance_sensors = get_distance_sensors(robot)
    left_motor, right_motor = get_motors(robot)

    initialize_devices(
        devices=distance_sensors.values(),
        motors=(left_motor, right_motor),
        timestep=timestep
    )

    while robot.step(timestep) != -1:
        distance_sensors_values = get_sensors_values(distance_sensors)
        robot_position = robot_node.getPosition()

        data = {
            "robot_name": robot_name,
            "robot_position": robot_position
        }
        data.update({
            "distance_sensors": distance_sensors_values
        })

        send_data(DATA_ENDPOINT, data)

        avoid_obstacles(
            robot, timestep, left_motor, right_motor, distance_sensors_values
        )


def main():
    robot = Supervisor()
    timestep = int(robot.getBasicTimeStep())

    run(robot, timestep)


if __name__ == "__main__":
    main()
