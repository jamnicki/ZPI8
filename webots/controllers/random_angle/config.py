HOST = "localhost"
PORT = 8000

# e-puck0, e-puck1, e-puck2, ...
DATA_ENDPOINT = f"http://{HOST}:{PORT}" + "/robot/{name}"

# https://cyberbotics.com/doc/guide/epuck#e-puck-model

MAX_MOTOR_VELOCITY = 4.2
MAX_ROTATION_SPEED = 6.28  # rad/s
MOTOR_USAGE = 0.8

INITIAL_VELOCITY = MOTOR_USAGE * MAX_MOTOR_VELOCITY
DISTANCE_THRESHOLD = 140

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
