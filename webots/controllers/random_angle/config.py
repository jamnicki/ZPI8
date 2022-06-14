HOST = "localhost"
PORT = 8000

# e-puck0, e-puck1, e-puck2, ...
DATA_ENDPOINT = f"http://{HOST}:{PORT}" + "/robot/{name}"

# https://cyberbotics.com/doc/guide/epuck#e-puck-model

MAX_MOTOR_VELOCITY = 6
MAX_ROTATION_SPEED = 6.28  # rad/s
MOTOR_USAGE = 1

INITIAL_VELOCITY = MOTOR_USAGE * MAX_MOTOR_VELOCITY
DISTANCE_THRESHOLD = 500

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

MATRIX_SIZE = 100
TIME_STEP = 32
