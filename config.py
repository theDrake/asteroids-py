#!/usr/bin/env python

#-------------------------------------------------------------------------------
#    Filename: config.py
#
#      Author: David C. Drake (www.davidcdrake.com)
#
# Description: Configuration file for an Asteroids game. Developed using Python
#              2.7.2.
#-------------------------------------------------------------------------------

TITLE             = 'Asteroids!'
SCREEN_WIDTH      = 800
SCREEN_HEIGHT     = 600
FRAMES_PER_SECOND = 30
BACKGROUND_COLOR  = (0, 0, 0)
BACKGROUND_MUSIC  = 'star_wars_asteroid_field.mp3'

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
SHIP_INITIAL_DIRECTION = -90.0
SHIP_ACCELERATION_RATE = 0.5
SHIP_ROTATION_RATE     = 10.0
SHIP_COLOR             = (140, 140, 255)

ASTEROID_COUNT              = 15
ASTEROID_MIN_POINTS         = 6
ASTEROID_MAX_POINTS         = 12
ASTEROID_MIN_RADIUS         = 10.0
ASTEROID_MAX_RADIUS         = 40.0
ASTEROID_COLOR              = (139, 69, 19)
ASTEROID_COLOR_DEVIATION    = 20
ASTEROID_MIN_SPEED          = 1.0
ASTEROID_MAX_SPEED          = 4.0
ASTEROID_MIN_ROTATION_SPEED = 1.0
ASTEROID_MAX_ROTATION_SPEED = 6.0

BULLET_COUNT  = 10
BULLET_RADIUS = 3.0
BULLET_COLOR  = (255, 255, 0)
BULLET_SPEED  = 30.0

UPGRADE_RADIUS      = 6.0
UPGRADE_REQUIREMENT = 5   # Number of asteroids to destroy to earn upgrade.
MAX_UPGRADE_LEVEL   = 7

STAR_COUNT         = 200
STAR_RADIUS        = 2.0
STAR_TWINKLE_SPEED = 20

RESPAWN_DELAY       = 50 # Game cycles.
VULNERABILITY_DELAY = 50 # Game cycles.

CIRCLE_POINT_COUNT = 8 # Number of points to use for circle collision detection.
