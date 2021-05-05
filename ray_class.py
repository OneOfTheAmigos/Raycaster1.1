import pygame 
import math

class Ray:
    def __init__(self, startingx, startingy, angle):
        self.startingx = startingx
        self.startingy = startingy
        self.angle = angle
        self.length = 100
        self.endx = self.startingx + (self.length * math.cos(math.radians(self.angle)))
        self.endy = self.startingy + (self.length * math.sin(math.radians(self.angle)))
        self.collisionRect = pygame.Rect(self.endx, self.endy, 1, 1)
        self.distances = []
        self.color = (255, 255, 255)

    def Update(self, newstartingx, newstartingy, newangle):
        self.startingx = newstartingx
        self.startingy = newstartingy
        self.angle = newangle
        self.endx = self.startingx + (self.length * math.cos(math.radians(self.angle)))
        self.endy = self.startingy + (self.length * math.sin(math.radians(self.angle)))
        self.collisionRect = pygame.Rect(self.endx, self.endy, 1, 1)