#------------------------------------------------------------------------------
#    Filename: shapes.py
#
#      Author: David C. Drake (http://davidcdrake.com)
#
# Description: Contains shape-related classes for use in an Asteroids game,
#              including 'Shape' (abstract), 'Polygon', 'Circle', 'Ship',
#              'Asteroid', 'Bullet', 'Star', 'Upgrade', and 'Point'. Developed
#              using Python 2.7 and PyGame 1.9.
#------------------------------------------------------------------------------

import math
import pygame
import random
from config import *

class Shape:
    def __init__(self, position, rotation, color):
        self.position = position
        self.rotation = rotation
        self.color = color
        self.dx = 0
        self.dy = 0
        self.activate()

    def paint(self):
        raise NotImplementedError()

    def gameLogic(self, keys, newkeys):
        raise NotImplementedError()

    def contains(self, point):
        raise NotImplementedError()

    def getPoints(self):
        raise NotImplementedError()

    def move(self):
        self.position = Point(self.position.x + self.dx,
                              self.position.y + self.dy)
        if self.position.x >= SCREEN_WIDTH:
            self.position = Point(0, self.position.y)
        elif self.position.x < 0:
            self.position = Point(SCREEN_WIDTH - 1, self.position.y)
        if self.position.y >= SCREEN_HEIGHT:
            self.position = Point(self.position.x, 0)
        elif self.position.y < 0:
            self.position = Point(self.position.x, SCREEN_HEIGHT)

    def rotate(self, degrees):
        self.rotation += degrees
        if self.rotation < 0.0:
            self.rotation += 360.0
        elif self.rotation >= 360.0:
            self.rotation -= 360.0

    def getRotation(self):
        return self.rotation

    def accelerate(self, acceleration):
        self.dx = self.dx + acceleration * \
                    math.cos(math.radians(self.rotation))
        self.dy = self.dy + acceleration * \
                    math.sin(math.radians(self.rotation))

    def intersects(self, otherShape):
        for point in self.getPoints():
            if otherShape.contains(point):
                return True
        for point in otherShape.getPoints():
            if self.contains(point):
                return True
        return False

    def isActive(self):
        return self.active

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def setRandomPosition(self):
        self.position = Point(int(random.uniform(0, SCREEN_WIDTH - 1)),
                              int(random.uniform(0, SCREEN_HEIGHT - 1)))

    def setRandomRotation(self, min=0.0, max=359.99):
        self.rotation = random.uniform(min, max)

    def setRandomRotationRate(self, min, max):
        self.rotationRate = random.uniform(min, max)
        if random.randint(0, 1):
            self.rotationRate *= -1.0

    def setRandomAcceleration(self, min, max):
        self.acceleration = int(random.uniform(min, max))

    def setPosition(self, point):
        self.position = point

    def setRandomColor(self):
        self.color = (random.randint(0, 255),
                      random.randint(0, 255),
                      random.randint(0, 255))

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
        self.center = self._findCenter()
        self.shape = []
        for p in shifted:
            self.shape.append(Point(p.x - self.center.x, p.y - self.center.y))

    # Applies rotation and offset to the shape of the polygon.
    def getPoints(self):
        (oldrotation, oldposition, oldpoints) = self.cache_points
        if oldrotation == self.rotation and oldposition == self.position:
            return oldpoints
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
        points = self.getPoints()
        crossingNumber = 0
        for i in range(len(points)):
            j = (i + 1) % len(points)
            if (((points[i].x < point.x and point.x <= points[j].x) or
                 (points[j].x < point.x and point.x <= points[i].x)) and
                (point.y > points[i].y + (points[j].y - points[i].y) /
                 (points[j].x - points[i].x) * (point.x - points[i].x))):
                crossingNumber += 1
        return crossingNumber % 2 == 1

    def _findArea(self):
        shape = self.shape
        sum = 0.0
        for i in range(len(shape)):
            j = (i + 1) % len(self.shape)
            sum += shape[i].x * shape[j].y - shape[j].x * shape[i].y
        return abs(0.5 * sum)

    def _findCenter(self):
        shape = self.shape
        (sum_x, sum_y) = (0.0, 0.0)
        for i in range(len(shape)):
            j = (i + 1) % len(self.shape)
            sum_x += (shape[i].x + shape[j].x) * \
                     (shape[i].x * shape[j].y - shape[j].x * shape[i].y)
            sum_y += (shape[i].y + shape[j].y) * \
                     (shape[i].x * shape[j].y - shape[j].x * shape[i].y)
        area = self._findArea()
        return Point(abs(sum_x / (6.0 * area)), abs(sum_y / (6.0 * area)))

    def paint(self, surface):
        if not self.isActive():
            return
        pointList = self.getPoints()
        convertedPointList = []
        for point in pointList:
            convertedPointList.append(point.pair())
        pygame.draw.polygon(surface, self.color, convertedPointList)

class Ship(Polygon):
    def __init__(self, position, rotation, color):
        shape = []
        for point in SHIP_POINTS:
            shape.append(Point(point[0], point[1]))
        Polygon.__init__(self, shape, position, rotation, color)
        self.rotationRate       = SHIP_ROTATION_RATE
        self.accelerationRate   = SHIP_ACCELERATION_RATE
        self.asteroidsDestroyed = 0
        self.upgradeLevel       = 0
        self.shielded           = False
        self.invincibilityTimer = 0
        self.respawnTimer       = 0

    def gameLogic(self, keys, newkeys):
        if not self.isActive():
            if self.respawnTimer > 0:
                self.respawnTimer -= 1
                if self.respawnTimer <= 0:
                    self.invincibilityTimer = VULNERABILITY_DELAY
                    self.activate()
            return
        if self.invincibilityTimer > 0:
            self.invincibilityTimer -= 1
        if pygame.K_RIGHT in keys:
            self.rotate(self.rotationRate)
        if pygame.K_LEFT in keys:
            self.rotate(self.rotationRate * -1)
        if pygame.K_UP in keys:
            self.accelerate(self.accelerationRate)
        if pygame.K_DOWN in keys:
            self.accelerate(self.accelerationRate * -1)
        if self.shielded:
            self.setRandomColor()
        self.move()

    def takeDamage(self):
        if self.invincibilityTimer > 0:
            return
        elif self.shielded:
            self.shielded = False
            self.color = SHIP_COLOR
            self.invincibilityTimer = VULNERABILITY_DELAY
        else:
            self.deactivate()
            self.asteroidsDestroyed = 0
            self.upgradeLevel = 0
            self.position = Point(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            self.rotation = SHIP_INITIAL_ROTATION
            self.dx = 0
            self.dy = 0
            self.respawnTimer = RESPAWN_DELAY

    def upgrade(self):
        self.upgradeLevel += 1
        if self.upgradeLevel >= MAX_UPGRADE_LEVEL:
            self.upgradeLevel == MAX_UPGRADE_LEVEL
            self.shielded = True
        self.asteroidsDestroyed = 0

    def paint(self, surface):
        if self.invincibilityTimer > 0 and self.invincibilityTimer % 2:
            return
        Polygon.paint(self, surface)

class Asteroid(Polygon):
    def __init__(self):
        self.setRandomPoints()
        self.setRandomPosition()
        self.setRandomRotation()
        self.setRandomRotationRate(ASTEROID_MIN_ROTATION_SPEED,
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
        Polygon.__init__(self,
                         self.shape,
                         self.position,
                         self.rotation,
                         self.color)
        self.setRandomAcceleration(ASTEROID_MIN_SPEED,
                                   ASTEROID_MAX_SPEED)
        self.accelerate(self.acceleration)

    def setRandomPoints(self):
        self.shape = []
        points = random.randint(ASTEROID_MIN_POINTS, ASTEROID_MAX_POINTS)
        for i in range(0, 360, 360 / points):
            radius = random.randint(int(ASTEROID_MIN_RADIUS),
                                    int(ASTEROID_MAX_RADIUS))
            radians = math.radians(i)
            self.shape.append(Point(math.cos(radians) * radius,
                                    math.sin(radians) * radius))

    def gameLogic(self, keys, newkeys):
        if not self.isActive():
            return
        self.rotate(self.rotationRate)
        self.move()

class Circle(Shape):
    def __init__(self, position, radius, rotation, color):
        Shape.__init__(self, position, rotation, color)
        self.radius = radius

    def paint(self, surface):
        if self.isActive():
            pygame.draw.circle(surface,
                               self.color,
                               self.position.pair(),
                               int(self.radius))

    def getPoints(self):
        points = []
        for i in range(0, 360, 360 / CIRCLE_POINT_COUNT):
            radians = math.radians(i)
            p = Point(math.cos(radians) * self.radius + self.position.x,
                      math.sin(radians) * self.radius + self.position.y)
            points.append(p)
        return points

    def contains(self, point):
        distanceX = self.position.x - point.x
        distanceY = self.position.y - point.y
        return (distanceX * distanceX) + (distanceY * distanceY) <= \
               (self.radius * self.radius)

class Bullet(Circle):
    def __init__(self, position, radius, rotation, color):
        Circle.__init__(self, position, radius, rotation, color)
        self.acceleration = BULLET_SPEED
        self.deactivate()

    def gameLogic(self, keys, newkeys):
        if not self.isActive():
            return
        self.move()

    def move(self):
        self.position = Point(self.position.x + self.dx,
                              self.position.y + self.dy)
        if self.position.x >= SCREEN_WIDTH or self.position.x < 0 or \
           self.position.y >= SCREEN_HEIGHT or self.position.y < 0:
            self.deactivate()

    def fire(self, position, rotation):
        self.activate()
        self.position = position
        self.rotation = rotation
        self.dx = 0
        self.dy = 0
        self.accelerate(self.acceleration)

class Upgrade(Circle):
    def __init__(self, position, radius, rotation, color):
        Circle.__init__(self, position, radius, rotation, color)
        self.deactivate()

    def gameLogic(self):
        self.setRandomColor()

class Star(Circle):
    def __init__(self):
        self.setRandomPosition()
        self.setRandomBrightness()
        self.radius      = STAR_RADIUS
        self.twinkleRate = STAR_TWINKLE_SPEED
        self.rotation    = 0.0
        Circle.__init__(self,
                        self.position,
                        self.radius,
                        self.rotation,
                        self.color)

    def setRandomBrightness(self):
        b = random.randint(0, 255)
        self.color = (b, b, b)

    def twinkle(self):
        if (self.color[0] + self.twinkleRate > 255) or \
           (self.color[0] + self.twinkleRate < 0):
            self.twinkleRate *= -1
        b = self.color[0] + self.twinkleRate
        self.color = (b, b, b)

class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def pair(self):
        return (int(round(self.x)), int(round(self.y)))

    def __str__(self):
        return 'Point(%.1f, %.1f)' % (self.x, self.y)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
