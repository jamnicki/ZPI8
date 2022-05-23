"""zpi_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Supervisor


import requests
import math
from enum import Enum


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

        # Transform robot position to 0,0
        self.x_pos = robot_position[0] + self.world_dim_x/2
        self.y_pos = robot_position[1] + self.world_dim_y/2
        self.theta_deg = math.copysign(1, robot_rotation[3]) \
            * math.acos(robot_rotation[0]) * 180 / math.pi
        # print("position x: {}, position y: {}, orientation: {}"\
        # .format(self.x_pos, self.y_pos, self.theta_deg))

    # set equal velocity on both motors
    def set_velocity(self, velocity):
        if velocity > MAX_SPEED:
            velocity = MAX_SPEED
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
            velocity = math.copysign(1, angle_error) * 0.5
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


def run_robot(robot):
    own_robot = robot_controller(robot, world_dim_x=2, world_dim_y=2)
    robot_name = robot.getName()
    rotation_field = own_robot.node_robot.getField("rotation")

    prox_sensors = []
    for ind in range(8):
        sensor_name = 'ps' + str(ind)
        prox_sensors.append(robot.getDevice(sensor_name))
        prox_sensors[ind].enable(TIME_STEP)

    desired_angle_deg = 90
    obstacle_avoidence_duration = 2
    while robot.step(TIME_STEP) != -1:
        data = {
                "robot_name": robot_name,
                "robot_position": own_robot.node_robot.getPosition(),
                "robot_rotation": rotation_field.getSFRotation()[-1]
                # "robot_rotation": own_robot.theta_deg
            }
        data.update({
            "distance_sensors": {
                f"ps{i}": epuck_to_meters(sensor.getValue())
                for i, sensor in enumerate(prox_sensors)
            }
        })
        send_data(DATA_ENDPOINT.format(name=robot_name), data)

        # print(own_robot.state)
        own_robot.update_robot_pose()

        own_robot.rotate(desired_angle_deg)
        if not own_robot.is_rotate:
            if own_robot.state in (robot_State.free_and_90, robot_State.free_and_minus_90):  # noqa: E501
                own_robot.set_velocity(2)

            if own_robot.state == robot_State.free_and_0:
                if obstacle_avoidence_duration > 0:
                    own_robot.set_velocity(2)
                    obstacle_avoidence_duration -= TIME_STEP/1000
                else:
                    if own_robot.obstacle_state == obstacle_State.up:
                        desired_angle_deg = -90
                    if own_robot.obstacle_state == obstacle_State.down:
                        desired_angle_deg = 90

        if (prox_sensors[0].getValue() > 140) and (prox_sensors[7].getValue() > 140):  # noqa: E501
            print("WALL DETECTED")
            own_robot.update_robot_pose()
            if(abs(90 - own_robot.theta_deg) < 1):
                own_robot.state = robot_State.wall_and_90
                own_robot.obstacle_state = obstacle_State.up

            if(abs(-90 - own_robot.theta_deg) < 1):
                own_robot.state = robot_State.wall_and_minus_90
                own_robot.obstacle_state = obstacle_State.down

            if own_robot.state in (robot_State.wall_and_90, robot_State.wall_and_minus_90):   # noqa: E501
                desired_angle_deg = 0

        else:
            if(abs(90 - own_robot.theta_deg) < 1):
                own_robot.state = robot_State.free_and_90
                obstacle_avoidence_duration = 2
            if(abs(-90 - own_robot.theta_deg) < 1):
                own_robot.state = robot_State.free_and_minus_90
                obstacle_avoidence_duration = 2
            if(abs(0 - own_robot.theta_deg) < 1):
                own_robot.state = robot_State.free_and_0


if __name__ == "__main__":
    MAX_SPEED = 6.28
    TIME_STEP = 32

    HOST = "localhost"
    PORT = 8000

    # e-puck0, e-puck1, e-puck2, ...
    DATA_ENDPOINT = f"http://{HOST}:{PORT}" + "/robot/{name}/distance-sensors"

    my_robot = Supervisor()
    run_robot(my_robot)
