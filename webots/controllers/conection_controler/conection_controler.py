"""conection_controler controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor

from controller import Supervisor
from up_to_down import up_to_down
from left_to_right import left_to_right
import math
from enum import Enum


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

def run_robot(robot):
    own_robot = robot_controller(robot, world_dim_x = WORD_X , world_dim_y = WORD_Y) 
    controller = left_to_right(robot)
    while robot.step(TIME_STEP) != -1:
        x, y, theta = own_robot.update_robot_pose()

        if x < 0.1 and y < 0.1:
            controller = left_to_right(robot)
            controller

        if x > WORD_X-0.1 and y > WORD_Y-0.1:
            controller = up_to_down(robot)
            controller

        print(controller)
    
if __name__ == "__main__":
    WORD_X = 1.5
    WORD_Y = 1.5
    SPEED = 2
    DURATION = 0.3
    TIME_STEP = 32

    my_robot = Supervisor()
    run_robot(my_robot)
