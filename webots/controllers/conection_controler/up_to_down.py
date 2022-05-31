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

CURRENT_TIME = 0

class robot_State(Enum):
    free_and_minus_180 = 0
    wall_and_minus_180 = 1
    free_and_0 = 2
    wall_and_0 = 3
    free_and_minus_90 = 4

class obstacle_State(Enum):
    left = 0
    right = 1

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
        # print("position x: {}, position y: {}, orientation: {}"\
        # .format(self.x_pos, self.y_pos, self.theta_deg))
        return self.x_pos, self.y_pos, self.theta_deg

    def set_velocity(self, velocity):
        if velocity > SPEED:
            velocity = SPEED
        self.left_motor.setVelocity(velocity)
        self.right_motor.setVelocity(velocity)

    def rotate(self, angle_deg):
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

def up_to_down(robot):
    own_robot = robot_controller(robot, world_dim_x = WORD_X , world_dim_y = WORD_Y) 
    robot_name = robot.getName()
    rotation_field = own_robot.node_robot.getField("rotation")

    prox_sensors = []
    for ind in range(8):
        sensor_name = 'ps' + str(ind)
        prox_sensors.append(robot.getDevice(sensor_name))
        prox_sensors[ind].enable(TIME_STEP)

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

    desired_angle_deg = -179
    obstacle_avoidence_duration = DURATION
    while robot.step(TIME_STEP) != -1:
    
        print('robot 1: ',own_robot.state)
        print('robot 1: ',own_robot.is_rotate)
        own_robot.update_robot_pose()

        own_robot.rotate(desired_angle_deg)
        if not own_robot.is_rotate:
            if own_robot.state == robot_State.free_and_minus_180 or own_robot.state == robot_State.free_and_0:
                own_robot.set_velocity(SPEED)

            if own_robot.state == robot_State.free_and_minus_90:
                if obstacle_avoidence_duration > 0:
                    own_robot.set_velocity(SPEED)
                    obstacle_avoidence_duration -= TIME_STEP/1000
                else:
                    if own_robot.obstacle_state == obstacle_State.left:
                        desired_angle_deg = 0 
                    if own_robot.obstacle_state == obstacle_State.right:
                        desired_angle_deg = -179

        if (prox_sensors[0].getValue() > 140) or (prox_sensors[7].getValue() > 140):
            print("WALL DETECTED")
            own_robot.update_robot_pose()
            if(abs(-179 - own_robot.theta_deg) < 1):
                own_robot.state = robot_State.wall_and_minus_180
                own_robot.obstacle_state = obstacle_State.left

            if(abs(0 - own_robot.theta_deg) < 1):
                own_robot.state = robot_State.wall_and_0
                own_robot.obstacle_state = obstacle_State.right

            if own_robot.state == robot_State.wall_and_minus_180 or own_robot.state == robot_State.wall_and_0:
                desired_angle_deg = -90

        else:
            if(abs(-179 - own_robot.theta_deg) < 1):
                own_robot.state = robot_State.free_and_minus_180
                obstacle_avoidence_duration = DURATION
            if(abs(0 - own_robot.theta_deg) < 1):
                own_robot.state = robot_State.free_and_0
                obstacle_avoidence_duration = DURATION
            if(abs(-90 - own_robot.theta_deg) < 1):
                own_robot.state = robot_State.free_and_minus_90
        x, y, theta = own_robot.update_robot_pose()
        if x < 0.1 and y < 0.1:
            break
    return False

WORD_X = 1.5
WORD_Y = 1.5
SPEED = 2
DURATION = 2
TIME_STEP = 32
HOST = "localhost"
PORT = 8000

# e-puck0, e-puck1, e-puck2, ...
DATA_ENDPOINT = f"http://{HOST}:{PORT}" + "/robot/{name}/distance-sensors"
