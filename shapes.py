#-------------------------------------------------------------------------------
#    Filename: shapes.py
#
#      Author: David C. Drake (https://davidcdrake.com)
#
# Description: Contains shape-related classes for use in an Asteroids game,
#              including 'Shape' (abstract), 'Polygon', 'Circle', 'Ship',
#              'Asteroid', 'Bullet', 'Star', 'Upgrade', and 'Point'. Developed
#              using Python 2.7 and Pygame 1.9.
#-------------------------------------------------------------------------------

import math
import random
import pygame
from pygame import draw
from config import *

#-------------------------------------------------------------------------------
#       Class: Shape
#
# Description: Abstract class for handling shapes as Asteroids game objects.
#
#     Methods: __init__, game_logic (virtual), paint (virtual), get_points
#              (virtual), contains (virtual), move, boundary_check, rotate,
#              accelerate, intersects, set_random_color, set_random_rotation,
#              set_random_rotation_rate, set_random_acceleration
#-------------------------------------------------------------------------------
class Shape:
    def __init__(self, position, rotation, color):
        self.position = position
        self.rotation = rotation
        self.color = color
        self.dx = 0
        self.dy = 0
        self.active = True

    def game_logic(self, keys, new_keys):
        raise NotImplementedError()

    def paint(self):
        raise NotImplementedError()

    def get_points(self):
        raise NotImplementedError()

    def contains(self, point):
        raise NotImplementedError()

    def move(self):
        self.position = Point(self.position.x + self.dx,
                              self.position.y + self.dy)

    def boundary_check(self, screen_width, screen_height):
        if self.position.x >= screen_width:
            self.position = Point(0, self.position.y)
        elif self.position.x < 0:
            self.position = Point(screen_width - 1, self.position.y)
        if self.position.y >= screen_height:
            self.position = Point(self.position.x, 0)
        elif self.position.y < 0:
            self.position = Point(self.position.x, screen_height)

    def rotate(self, degrees):
        self.rotation += degrees
        if self.rotation < 0.0:
            self.rotation += 360.0
        elif self.rotation >= 360.0:
            self.rotation -= 360.0

    def accelerate(self, acceleration):
        self.dx = self.dx + acceleration * math.cos(math.radians(self.rotation))
        self.dy = self.dy + acceleration * math.sin(math.radians(self.rotation))

    def intersects(self, other_shape):
        for point in self.get_points():
            if other_shape.contains(point):
                return True
        for point in other_shape.get_points():
            if self.contains(point):
                return True
        return False

    def set_random_color(self):
        self.color = (random.randint(0, 255), random.randint(0, 255),
                      random.randint(0, 255))

    def set_random_rotation(self, min=0.0, max=359.99):
        self.rotation = random.uniform(min, max)

    def set_random_rotation_rate(self, min, max):
        self.rotation_rate = random.uniform(min, max)
        if random.randint(0, 1):
            self.rotation_rate *= -1.0

    def set_random_acceleration(self, min, max):
        self.acceleration = int(random.uniform(min, max))

#-------------------------------------------------------------------------------
#       Class: Polygon
#
# Description: Superclass for all polygonal Asteroids game objects.
#
#     Methods: __init__, paint, get_points, contains, _find_area, _find_center
#-------------------------------------------------------------------------------
class Polygon(Shape):
    def __init__(self, shape, position, rotation, color):
        Shape.__init__(self, position, rotation, color)
        self.cache_points = (None, None, None)

        # Find the shape's origin (its top-most, left-most pixel):
        (origin_x, origin_y) = (shape[0].x, shape[0].y)
        for p in shape:
            if p.x < origin_x:
                origin_x = p.x
            if p.y < origin_y:
                origin_y = p.y

        # Orient all points relative to the origin:
        shifted = []
        for p in shape:
            shifted.append(Point(p.x - origin_x, p.y - origin_y))

        # Now shift all points based on the center of gravity:
        self.shape = shifted
        self.center = self._find_center()
        self.shape = []
        for p in shifted:
            self.shape.append(Point(p.x - self.center.x, p.y - self.center.y))

    def paint(self, surface):
        if not self.active:
            return
        point_list = self.get_points()
        converted_point_list = []
        for point in point_list:
            converted_point_list.append(point.pair())
        draw.polygon(surface, self.color, converted_point_list)

    # Applies rotation and offset to the shape of the polygon.
    def get_points(self):
        (old_rotation, old_position, old_points) = self.cache_points
        if old_rotation == self.rotation and old_position == self.position:
            return old_points
        angle = math.radians(self.rotation)
        sin = math.sin(angle)
        cos = math.cos(angle)
        points = []
        for p in self.shape:
            x = p.x * cos - p.y * sin + self.position.x
            y = p.x * sin + p.y * cos + self.position.y
            points.append(Point(x, y))
        self.cache_points = (self.rotation, self.position, points)
        return points

    # Determines whether a given point is inside the polygon.
    def contains(self, point):
        points = self.get_points()
        crossing_number = 0
        for i in range(len(points)):
            j = (i + 1) % len(points)
            if (((points[i].x < point.x and point.x <= points[j].x) or
                 (points[j].x < point.x and point.x <= points[i].x)) and
                (point.y > points[i].y + (points[j].y - points[i].y) /
                 (points[j].x - points[i].x) * (point.x - points[i].x))):
                crossing_number += 1
        return crossing_number % 2 == 1

    def _find_area(self):
        shape = self.shape
        sum = 0.0
        for i in range(len(shape)):
            j = (i + 1) % len(self.shape)
            sum += shape[i].x * shape[j].y - shape[j].x * shape[i].y
        return abs(0.5 * sum)

    def _find_center(self):
        shape = self.shape
        (sum_x, sum_y) = (0.0, 0.0)
        for i in range(len(shape)):
            j = (i + 1) % len(self.shape)
            sum_x += ((shape[i].x + shape[j].x) *
                      (shape[i].x * shape[j].y - shape[j].x * shape[i].y))
            sum_y += ((shape[i].y + shape[j].y) *
                      (shape[i].x * shape[j].y - shape[j].x * shape[i].y))
        area = self._find_area()
        return Point(abs(sum_x / (6.0 * area)), abs(sum_y / (6.0 * area)))

#-------------------------------------------------------------------------------
#       Class: Ship
#
# Description: Manages a player-controlled ship.
#
#     Methods: __init__, game_logic, paint, upgrade, take_damage
#-------------------------------------------------------------------------------
class Ship(Polygon):
    def __init__(self, position, rotation, color):
        shape = []
        for point in SHIP_POINTS:
            shape.append(Point(point[0], point[1]))
        Polygon.__init__(self, shape, position, rotation, color)
        self.starting_point = position
        self.rotation_rate = SHIP_ROTATION_RATE
        self.acceleration_rate = SHIP_ACCELERATION_RATE
        self.asteroids_destroyed = 0
        self.upgrade_level = 0
        self.shielded = False
        self.invincibility_timer = 0
        self.respawn_timer = 0

    def game_logic(self, keys, new_keys):
        if not self.active:
            if self.respawn_timer > 0:
                self.respawn_timer -= 1
                if self.respawn_timer <= 0:
                    self.invincibility_timer = VULNERABILITY_DELAY
                    self.active = True
            return
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1
        if (pygame.K_UP in keys or pygame.K_w in keys or
            pygame.K_KP8 in keys):
            self.accelerate(self.acceleration_rate)
        if (pygame.K_DOWN in keys or pygame.K_s in keys or
            pygame.K_KP2 in keys):
            self.accelerate(self.acceleration_rate * -1)
        if (pygame.K_LEFT in keys or pygame.K_a in keys or
            pygame.K_KP4 in keys):
            self.rotate(self.rotation_rate * -1)
        if (pygame.K_RIGHT in keys or pygame.K_d in keys or
            pygame.K_KP6 in keys):
            self.rotate(self.rotation_rate)
        if self.shielded:
            self.set_random_color()
        self.move()

    def paint(self, surface):
        if self.invincibility_timer > 0 and self.invincibility_timer % 2:
            return
        Polygon.paint(self, surface)

    def upgrade(self):
        self.upgrade_level += 1
        if self.upgrade_level >= MAX_UPGRADE_LEVEL:
            self.upgrade_level == MAX_UPGRADE_LEVEL
            self.shielded = True

    def take_damage(self):
        if self.invincibility_timer > 0:
            return
        elif self.shielded:
            self.shielded = False
            self.color = SHIP_COLOR
            self.invincibility_timer = VULNERABILITY_DELAY
        else:
            self.active = False
            self.asteroids_destroyed = 0
            self.upgrade_level = 0
            self.position = self.starting_point
            self.rotation = SHIP_INITIAL_ROTATION
            self.dx = 0
            self.dy = 0
            self.respawn_timer = RESPAWN_DELAY

#-------------------------------------------------------------------------------
#       Class: Asteroid
#
# Description: Manages asteroid behavior.
#
#     Methods: __init__, game_logic, _set_random_points
#-------------------------------------------------------------------------------
class Asteroid(Polygon):
    def __init__(self, average_radius, spawn_point):
        self.average_radius = average_radius
        self._set_random_points(self.average_radius)
        self.set_random_rotation()
        self.set_random_rotation_rate(ASTEROID_MIN_ROTATION_SPEED,
                                      ASTEROID_MAX_ROTATION_SPEED)
        self.color = list(ASTEROID_COLOR)
        index = random.randint(0, 2)
        if random.randint(0, 1):
            self.color[index] += ASTEROID_COLOR_DEVIATION
            if self.color[index] > 255:
                self.color[index] -= 2 * ASTEROID_COLOR_DEVIATION
        else:
            self.color[index] -= ASTEROID_COLOR_DEVIATION
            if self.color[index] < 0:
                self.color[index] += 2 * ASTEROID_COLOR_DEVIATION
        self.color = tuple(self.color)
        Polygon.__init__(self, self.shape, spawn_point, self.rotation,
                         self.color)
        self.set_random_acceleration(ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED)
        self.accelerate(self.acceleration)

    def game_logic(self, keys, new_keys):
        self.move()

    def _set_random_points(self, average_radius):
        self.shape = []
        points = random.randint(ASTEROID_MIN_POINTS, ASTEROID_MAX_POINTS)
        radius_deviation = average_radius / 4
        for i in range(0, 360, 360 / points):
            radius = random.randint(average_radius - radius_deviation,
                                    average_radius + radius_deviation)
            radians = math.radians(i)
            self.shape.append(Point(math.cos(radians) * radius,
                                    math.sin(radians) * radius))

#-------------------------------------------------------------------------------
#       Class: Circle
#
# Description: Superclass for all circular Asteroids game objects.
#
#     Methods: __init__, paint, get_points, contains
#-------------------------------------------------------------------------------
class Circle(Shape):
    def __init__(self, position, radius, rotation, color):
        Shape.__init__(self, position, rotation, color)
        self.radius = radius

    def paint(self, surface):
        if self.active:
            draw.circle(surface, self.color, self.position.pair(),
                        int(self.radius))

    def get_points(self):
        points = []
        for i in range(0, 360, 360 / CIRCLE_POINT_COUNT):
            radians = math.radians(i)
            p = Point(math.cos(radians) * self.radius + self.position.x,
                      math.sin(radians) * self.radius + self.position.y)
            points.append(p)
        return points

    def contains(self, point):
        distance_x = self.position.x - point.x
        distance_y = self.position.y - point.y
        return ((distance_x * distance_x) + (distance_y * distance_y) <=
                (self.radius * self.radius))

#-------------------------------------------------------------------------------
#       Class: Bullet
#
# Description: Manages bullets from the player's ship.
#
#     Methods: __init__, game_logic
#-------------------------------------------------------------------------------
class Bullet(Circle):
    def __init__(self, position, rotation):
        Circle.__init__(self, position, BULLET_RADIUS, rotation, BULLET_COLOR)
        self.accelerate(BULLET_SPEED)

    def game_logic(self, keys, new_keys):
        self.position = Point(self.position.x + self.dx,
                              self.position.y + self.dy)

#-------------------------------------------------------------------------------
#       Class: Upgrade
#
# Description: Manages the visual appearance of upgrades (power-ups).
#
#     Methods: __init__, game_logic
#-------------------------------------------------------------------------------
class Upgrade(Circle):
    def __init__(self, position):
        Circle.__init__(self, position, UPGRADE_RADIUS, 0, (0, 0, 0))

    def game_logic(self):
        self.set_random_color()

#-------------------------------------------------------------------------------
#       Class: Star
#
# Description: Manages the appearance of distant stars.
#
#     Methods: __init__, twinkle
#-------------------------------------------------------------------------------
class Star(Circle):
    def __init__(self, spawn_point):
        self.position = spawn_point
        self.radius = STAR_RADIUS
        self.twinkle_rate = STAR_TWINKLE_SPEED
        self.rotation = 0.0
        b = random.randint(0, 255)
        self.color = (b, b, b)
        Circle.__init__(self, self.position, self.radius, self.rotation,
                        self.color)

    def twinkle(self):
        if ((self.color[0] + self.twinkle_rate > 255) or
            (self.color[0] + self.twinkle_rate < 0)):
            self.twinkle_rate *= -1
        b = self.color[0] + self.twinkle_rate
        self.color = (b, b, b)

#-------------------------------------------------------------------------------
#       Class: Point
#
# Description: A simple point class for handling x,y coordinates.
#
#     Methods: __init__, __str__, __repr__, __eq__, pair
#-------------------------------------------------------------------------------
class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __str__(self):
        return 'Point(%.1f, %.1f)' % (self.x, self.y)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def pair(self):
        return (int(round(self.x)), int(round(self.y)))
