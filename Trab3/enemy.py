import pygame
import math
from abc import ABC, abstractmethod
from util import colored_sprite, EventHandler

class Enemy:
    def __init__(self, pos, player):
        self.pos = list(pos)
        self.player = player
        self.radius = 14
        self.max_hp = 3
        self.hp = self.max_hp
        self.speed = 1.3
        self.state = ApproachingState(self)

    def update(self, dt):
        self.state.update(dt)

    def draw(self, screen):
        self.state.draw(screen)

    def change_state(self, new_state):
        self.state.delete()
        self.state = new_state

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.destroy()
        else:
            self.change_state(StunnedState(self, duration=15))

    def destroy(self):
        EventHandler().notify("EnemyKilled", 100)
        EventHandler().notify("DestroyObj", self)

class EnemyState(ABC):
    def __init__(self, enemy):
        self.E = enemy

    def draw(self, screen):
        x, y = self.E.pos[0] - 14, self.E.pos[1] - 14
        sprite = colored_sprite((220, 50, 50), (28, 28))
        screen.blit(sprite, (x, y))
        
        ratio = max(0, self.E.hp / self.E.max_hp)
        pygame.draw.rect(screen, (255, 0, 0), (x, y - 8, 28, 4))
        pygame.draw.rect(screen, (0, 255, 0), (x, y - 8, int(28 * ratio), 4))

    def delete(self): pass

    @abstractmethod
    def update(self, dt): pass

class ApproachingState(EnemyState):
    def update(self, dt):
        px, py = self.E.player.pos
        ex, ey = self.E.pos
        dx, dy = px - ex, py - ey
        dist = math.hypot(dx, dy)

        if dist > 0:
            self.E.pos[0] += (dx / dist) * self.E.speed
            self.E.pos[1] += (dy / dist) * self.E.speed

        if dist < (self.E.radius + self.E.player.radius):
            self.E.change_state(AttackingState(self.E))

class StunnedState(EnemyState):
    def __init__(self, enemy, duration=15):
        super().__init__(enemy)
        self.duration = duration

    def draw(self, screen):
        x, y = self.E.pos[0] - 14, self.E.pos[1] - 14
        sprite = colored_sprite((255, 200, 0), (28, 28))
        screen.blit(sprite, (x, y))
        
        ratio = max(0, self.E.hp / self.E.max_hp)
        pygame.draw.rect(screen, (255, 0, 0), (x, y - 8, 28, 4))
        pygame.draw.rect(screen, (0, 255, 0), (x, y - 8, int(28 * ratio), 4))

    def update(self, dt):
        self.duration -= dt
        if self.duration <= 0:
            self.E.change_state(ApproachingState(self.E))

class AttackingState(EnemyState):
    def __init__(self, enemy):
        super().__init__(enemy)
        self.cooldown = 0

    def update(self, dt):
        self.E.player.take_damage(10)
        self.E.change_state(ApproachingState(self.E))