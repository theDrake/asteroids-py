#-------------------------------------------------------------------------------
#    Filename: config.py
#
#      Author: David C. Drake (https://davidcdrake.com)
#
# Description: Configuration file for a simple Asteroids game.
#-------------------------------------------------------------------------------

FRAMES_PER_SECOND = 60
BACKGROUND_COLOR = (0, 0, 0)
BACKGROUND_MUSIC = 'asteroids.mp3'

SHIP_POINTS = [(30, 15),
               (10, 20),
               (15, 25),
               (10, 30),
               (0, 25),
               (10, 20),
               (0, 15),
               (10, 10),
               (0, 5),
               (10, 0),
               (15, 5),
               (10, 10)]
SHIP_INITIAL_ROTATION = -90.0
SHIP_ACCELERATION_RATE = 0.3
SHIP_ROTATION_RATE = 8.0
SHIP_COLOR = (140, 140, 255)

ASTEROID_DENSITY = 0.005
ASTEROID_MIN_POINTS = 6
ASTEROID_MAX_POINTS = 12
ASTEROID_MIN_RADIUS = 20
ASTEROID_MAX_RADIUS = 80
ASTEROID_COLOR = (139, 69, 19)
ASTEROID_COLOR_DEVIATION = 20
ASTEROID_MIN_SPEED = 1.0
ASTEROID_MAX_SPEED = 4.0
ASTEROID_MIN_ROTATION_SPEED = 1.0
ASTEROID_MAX_ROTATION_SPEED = 6.0

BULLET_RADIUS = 3.0
BULLET_COLOR = (255, 255, 0)
BULLET_SPEED = 30.0

UPGRADE_RADIUS = 7.0
UPGRADE_REQ = 15 # number of asteroids to destroy to earn upgrade
MAX_UPGRADE_LEVEL = 7

STAR_DENSITY = 0.1
STAR_RADIUS = 2
STAR_TWINKLE_SPEED = 20

RESPAWN_DELAY = 60 # game cycles
VULNERABILITY_DELAY = 120 # game cycles

CIRCLE_POINT_COUNT = 8 # number of points to use for collision detection
