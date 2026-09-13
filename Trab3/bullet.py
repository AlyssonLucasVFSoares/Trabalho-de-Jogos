import pygame
import math
from abc import ABC, abstractmethod
from util import colored_sprite, EventHandler

def rotate(pos, angle, axis=(0,0)):
    angle = math.radians(angle)
    x, y = pos
    ax, ay = axis
    x -= ax
    y -= ay
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    rx = x * cos_a - y * sin_a
    ry = x * sin_a + y * cos_a
    return rx + ax, ry + ay

class Bullet(ABC):
    def __init__(self, pos, angle=0, radius=6, life_time=120):
        self.pos = pos
        self.origin = pygame.Vector2(pos)
        self.life_time = life_time
        self.angle = angle
        self.elapsed = 0
        self.radius = radius
        self.sprite = colored_sprite((255, 255, 0), (self.radius*2, self.radius*2))

    def update(self, dt):
        self.elapsed += dt
        if self.life_time and self.elapsed >= self.life_time:
            self.destroy()       
        self.pos = rotate(self.move(), self.angle) + self.origin

    def draw(self, screen):
        screen.blit(self.sprite, (self.pos[0] - self.radius, self.pos[1] - self.radius))

    @abstractmethod
    def move(self):
        pass

    def destroy(self):
        EventHandler().notify("DestroyObj", self)

class StraightBullet(Bullet):
    def __init__(self, pos, angle, speed=8, life_time=90):
        super().__init__(pos, angle=angle, radius=5, life_time=life_time)
        self.speed = speed

    def move(self):
        return pygame.Vector2(self.elapsed * self.speed, 0)