#!/usr/bin/python2

#-------------------------------------------------------------------------------
#    Filename: asteroids.py
#
#      Author: David C. Drake (https://davidcdrake.com)
#
# Description: Contains an 'AsteroidsGame' class for managing a modified version
#              of the classic game Asteroids and a 'main' function for running
#              it. Developed using Python 2.7 and Pygame 1.9.
#-------------------------------------------------------------------------------

import random
from game import Game
from shapes import *
from config import *

#-------------------------------------------------------------------------------
#       Class: AsteroidsGame
#
# Description: Manages a modified version of the classic Asteroids game.
#
#     Methods: __init__, gameLogic, paint, initializeAsteroids
#-------------------------------------------------------------------------------
class AsteroidsGame(Game):
    #---------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Creates all game objects (a ship, bullets, an upgrade icon,
    #              asteroids, and stars) and starts playing background music.
    #
    #      Inputs: title        - Text to display along the top of the window.
    #              screenWidth  - Width of the screen, in pixels.
    #              screenHeight - Height of the screen, in pixels.
    #              fps          - Frames per second.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def __init__(self, title, screenWidth, screenHeight, fps):
        Game.__init__(self, title, screenWidth, screenHeight, fps)

        # Create the ship and place it in the center of the screen:
        center = Point(screenWidth / 2, screenHeight / 2)
        self.ship = Ship(center, SHIP_INITIAL_ROTATION, SHIP_COLOR)

        # Create bullets and an upgrade object:
        self.bullets = []
        for i in range(BULLET_COUNT + 1):
            self.bullets.append(Bullet(center, BULLET_RADIUS, 0, BULLET_COLOR))
        self.upgrade = Upgrade(center, UPGRADE_RADIUS, 0, (0, 0, 0))

        # Create asteroids and background stars:
        self.initializeAsteroids()
        self.stars = []
        for i in range(STAR_COUNT + 1):
            self.stars.append(Star())

        # Initialize mixer and start playing music:
        pygame.mixer.init()
        pygame.mixer.music.load(BACKGROUND_MUSIC)
        pygame.mixer.music.play(-1)

    #---------------------------------------------------------------------------
    #      Method: gameLogic
    #
    # Description: Determines game behavior based on keyboard input and object
    #              interactions.
    #
    #      Inputs: keys    - Keys that are currently pressed down.
    #              newkeys - Keys that have just begun to be pressed down.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def gameLogic(self, keys, newkeys):
        # Ship:
        self.ship.gameLogic(keys, newkeys)

        # Bullets:
        if pygame.K_SPACE in newkeys and self.ship.isActive():
            if self.ship.upgradeLevel != 1:
                self.bullets[0].fire(self.ship.getPoints()[0],
                                     self.ship.getRotation())
            if self.ship.upgradeLevel > 0:
                self.bullets[1].fire(self.ship.getPoints()[3],
                                     self.ship.getRotation())
                self.bullets[2].fire(self.ship.getPoints()[9],
                                     self.ship.getRotation())
            if self.ship.upgradeLevel > 2:
                self.bullets[3].fire(self.ship.getPoints()[3],
                                     self.ship.getRotation() + 45)
                self.bullets[4].fire(self.ship.getPoints()[9],
                                     self.ship.getRotation() - 45)
            if self.ship.upgradeLevel > 3:
                self.bullets[5].fire(self.ship.getPoints()[3],
                                     self.ship.getRotation() + 90)
                self.bullets[6].fire(self.ship.getPoints()[9],
                                     self.ship.getRotation() - 90)
            if self.ship.upgradeLevel > 4:
                self.bullets[7].fire(self.ship.getPoints()[4],
                                     self.ship.getRotation() + 135)
                self.bullets[8].fire(self.ship.getPoints()[8],
                                     self.ship.getRotation() - 135)
            if self.ship.upgradeLevel > 5:
                self.bullets[9].fire(self.ship.getPoints()[6],
                                     self.ship.getRotation() + 180)
        for b in self.bullets:
            b.gameLogic(keys, newkeys)

        # Upgrade icon:
        if self.upgrade.isActive():
            self.upgrade.gameLogic()
            if self.ship.isActive() and self.ship.intersects(self.upgrade):
                self.ship.upgrade()
                self.upgrade.deactivate()

        # Asteroids:
        if self.asteroidCount > 0:
            for a in self.asteroids:
                a.gameLogic(keys, newkeys)
                # Check for collisions with bullets:
                for b in self.bullets:
                    if a.isActive() and b.isActive() and b.intersects(a):
                        b.deactivate()
                        a.deactivate()
                        self.asteroidCount -= 1
                        self.ship.asteroidsDestroyed += 1
                        if self.ship.asteroidsDestroyed == UPGRADE_REQUIREMENT \
                           and not self.upgrade.isActive():
                            self.upgrade.setPosition(a.position)
                            self.upgrade.activate()
                # Check for collisions with the ship:
                if a.isActive() and self.ship.isActive() and \
                   self.ship.intersects(a):
                    self.ship.takeDamage()
            # If all asteroids have been destroyed, a respawn timer is set:
            if self.asteroidCount <= 0:
                self.asteroidRespawnTimer = RESPAWN_DELAY
        elif self.asteroidRespawnTimer > 0:
            self.asteroidRespawnTimer -= 1
        else:
            # Spawn a new set of asteroids:
            self.initializeAsteroids()

        # Stars:
        for s in self.stars:
            s.twinkle()

    #---------------------------------------------------------------------------
    #      Method: paint
    #
    # Description: Draws the background color and all active objects onto the
    #              screen.
    #
    #      Inputs: surface - The surface onto which images will be drawn.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def paint(self, surface):
        surface.fill(BACKGROUND_COLOR)
        for s in self.stars:
            s.paint(surface)
        self.upgrade.paint(surface)
        self.ship.paint(surface)
        for b in self.bullets:
            b.paint(surface)
        for a in self.asteroids:
            a.paint(surface)

    #---------------------------------------------------------------------------
    #      Method: initializeAsteroids
    #
    # Description: Creates a new set of asteroid objects.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def initializeAsteroids(self):
        self.asteroids = []
        for i in range(ASTEROID_COUNT + 1):
            self.asteroids.append(Asteroid())
        self.asteroidCount = len(self.asteroids)

def main():
    game = AsteroidsGame(TITLE, SCREEN_WIDTH, SCREEN_HEIGHT, FRAMES_PER_SECOND)
    game.mainLoop()

if __name__ == '__main__':
    main()
