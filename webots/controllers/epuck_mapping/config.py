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
