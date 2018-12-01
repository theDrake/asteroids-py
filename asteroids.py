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
import pygame
from pygame import mixer, mouse
import game
import shapes
from config import *

#-------------------------------------------------------------------------------
#       Class: AsteroidsGame
#
# Description: Manages a modified version of the classic Asteroids game.
#
#     Methods: __init__, game_logic, paint, spawn_asteroids
#-------------------------------------------------------------------------------
class AsteroidsGame(game.Game):
    #---------------------------------------------------------------------------
    #      Method: __init__
    #
    # Description: Creates game objects and starts background music.
    #
    #      Inputs: fps - Desired frames per second.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def __init__(self, fps=FRAMES_PER_SECOND):
        game.Game.__init__(self, fps)
        mouse.set_visible(False)

        # Create the ship and place it in the center of the screen:
        center = shapes.Point(self.width / 2, self.height / 2)
        self.ship = shapes.Ship(center, SHIP_INITIAL_ROTATION, SHIP_COLOR)

        # Create bullet and upgrade lists:
        self.bullets = []
        self.upgrades = []

        # Create asteroids and background stars:
        self.asteroids = []
        self.spawn_asteroids()
        self.stars = []
        while len(self.stars) < (self.width * STAR_DENSITY):
            self.stars.append(shapes.Star(self.get_random_point()))

        # Initialize mixer and start looping background music:
        mixer.init()
        mixer.music.load(BACKGROUND_MUSIC)
        mixer.music.play(-1)

    #---------------------------------------------------------------------------
    #      Method: game_logic
    #
    # Description: Determines game behavior based on keyboard input and object
    #              interactions.
    #
    #      Inputs: keys     - Keys that are currently pressed down.
    #              new_keys - Keys that have just begun to be pressed down.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def game_logic(self, keys, new_keys):
        # Ship:
        self.ship.game_logic(keys, new_keys)
        self.ship.boundary_check(self.width, self.height)

        # Bullets:
        if ((pygame.K_SPACE in new_keys or pygame.K_RETURN in new_keys or
             pygame.K_KP_ENTER in new_keys or pygame.K_LCTRL in new_keys or
             pygame.K_RCTRL in new_keys) and self.ship.active):
            if self.ship.upgrade_level != 1:
                self.bullets.append(shapes.Bullet(self.ship.get_points()[0],
                                                  self.ship.rotation))
            if self.ship.upgrade_level > 0:
                self.bullets.append(shapes.Bullet(self.ship.get_points()[3],
                                                  self.ship.rotation))
                self.bullets.append(shapes.Bullet(self.ship.get_points()[9],
                                                  self.ship.rotation))
            if self.ship.upgrade_level > 2:
                self.bullets.append(shapes.Bullet(self.ship.get_points()[3],
                                                  self.ship.rotation + 45))
                self.bullets.append(shapes.Bullet(self.ship.get_points()[9],
                                                  self.ship.rotation - 45))
            if self.ship.upgrade_level > 3:
                self.bullets.append(shapes.Bullet(self.ship.get_points()[3],
                                                  self.ship.rotation + 90))
                self.bullets.append(shapes.Bullet(self.ship.get_points()[9],
                                                  self.ship.rotation - 90))
            if self.ship.upgrade_level > 4:
                self.bullets.append(shapes.Bullet(self.ship.get_points()[4],
                                                  self.ship.rotation + 135))
                self.bullets.append(shapes.Bullet(self.ship.get_points()[8],
                                                  self.ship.rotation - 135))
            if self.ship.upgrade_level > 5:
                self.bullets.append(shapes.Bullet(self.ship.get_points()[6],
                                                  self.ship.rotation + 180))
        for b in self.bullets:
            b.game_logic(keys, new_keys)
            if (b.position.x > self.width or b.position.x < 0 or
                b.position.y > self.height or b.position.y < 0):
                self.bullets.remove(b)

        # Upgrades:
        for u in self.upgrades:
            u.game_logic()
            if self.ship.active and self.ship.intersects(u):
                self.ship.upgrade()
                self.upgrades.remove(u)

        # Asteroids:
        if self.asteroid_count > 0:
            for a in self.asteroids:
                if a.active:
                    a.game_logic(keys, new_keys)
                    a.boundary_check(self.width, self.height)
                    if self.ship.active and self.ship.intersects(a):
                        self.ship.take_damage()
                        self.destroy_asteroid(a)
                    else:
                        for b in self.bullets:
                            if b.intersects(a):
                                self.bullets.remove(b)
                                self.destroy_asteroid(a)
                                break
        elif self.asteroid_respawn_timer > 0:
            self.asteroid_respawn_timer -= 1
        else:
            self.spawn_asteroids()

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
        for u in self.upgrades:
            u.paint(surface)
        self.ship.paint(surface)
        for b in self.bullets:
            b.paint(surface)
        for a in self.asteroids:
            a.paint(surface)

    #---------------------------------------------------------------------------
    #      Method: spawn_asteroids
    #
    # Description: Creates a new set of large asteroids. Also makes player
    #              temporarily invincible to avoid unfair deaths.
    #
    #      Inputs: None.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def spawn_asteroids(self):
        self.asteroid_count = int(self.width * ASTEROID_DENSITY)
        while len(self.asteroids):
            self.asteroids.pop()
        self.ship.invincibility_timer = VULNERABILITY_DELAY
        while len(self.asteroids) < self.asteroid_count:
            self.asteroids.append(shapes.Asteroid(ASTEROID_MAX_RADIUS,
                                                  self.get_random_point()))
        self.asteroid_respawn_timer = 0

    #---------------------------------------------------------------------------
    #      Method: destroy_asteroid
    #
    # Description: Handles the destruction of a given asteroid and the resulting
    #              aftermath, including possibly creating two smaller asteroids
    #              in its place.
    #
    #      Inputs: asteroid - The asteroid to be destroyed.
    #
    #     Outputs: None.
    #---------------------------------------------------------------------------
    def destroy_asteroid(self, asteroid):
            asteroid.active = False
            self.ship.asteroids_destroyed += 1
            if self.ship.asteroids_destroyed % UPGRADE_REQ == 0:
                self.upgrades.append(shapes.Upgrade(asteroid.position))
            half_radius = asteroid.average_radius / 2
            self.asteroid_count -= 1
            if half_radius >= ASTEROID_MIN_RADIUS:
                self.asteroids.append(shapes.Asteroid(half_radius,
                                                      asteroid.position))
                self.asteroids.append(shapes.Asteroid(half_radius,
                                                      asteroid.position))
                self.asteroid_count += 2
            elif self.asteroid_count <= 0:
                self.asteroid_respawn_timer = RESPAWN_DELAY

    #---------------------------------------------------------------------------
    #      Method: get_random_point
    #
    # Description: Generates a random spawn point (for a star or asteroid).
    #
    #      Inputs: None.
    #
    #     Outputs: Tuple containing the random coordinates.
    #---------------------------------------------------------------------------
    def get_random_point(self):
        random_point = shapes.Point(int(random.uniform(0, self.width - 1)),
                                    int(random.uniform(0, self.height - 1)))
        return random_point

def main():
    game = AsteroidsGame()
    game.main_loop()

if __name__ == '__main__':
    main()
