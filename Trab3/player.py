import pygame
import math
from abc import ABC, abstractmethod
from util import colored_sprite, EventHandler
from bullet import StraightBullet

class Player:
    def __init__(self, pos):
        self.pos = list(pos)
        self.speed = 2.5
        self.radius = 16
        self.max_hp = 100
        self.hp = self.max_hp
        self.lives = 3
        self.invincible_timer = 0
        
        # Instancia todas as armas para manter a munição salva
        self.weapons = [PistolState(self), ShotgunState(self), MachineGunState(self)]
        self.current_idx = 0
        self.state = self.weapons[self.current_idx]

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  self.pos[0] -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.pos[0] += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:    self.pos[1] -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  self.pos[1] += self.speed

        self.pos[0] = max(16, min(784, self.pos[0]))
        self.pos[1] = max(16, min(584, self.pos[1]))

        if self.invincible_timer > 0:
            self.invincible_timer -= dt

        # Recarregamento das armas
        is_reloading = keys[pygame.K_r]
        for w in self.weapons:
            if w == self.state and is_reloading:
                w.reload(dt, active=True)  # Recarga rápida (arma em mãos segurando R)
            else:
                w.reload(dt, active=False) # Recarga lenta (em segundo plano)

        self.state.update(dt)

    def draw(self, screen):
        if self.invincible_timer > 0 and int(self.invincible_timer * 10) % 2 == 0:
            return
        self.state.draw(screen)

    def action_1(self): self.state.action_1()
    
    def switch_weapon(self, idx):
        if 0 <= idx < len(self.weapons):
            self.current_idx = idx
            self.state = self.weapons[idx]

    def take_damage(self, amount):
        if self.invincible_timer <= 0:
            self.hp -= amount
            self.invincible_timer = 30
            if self.hp <= 0:
                self.lives -= 1
                EventHandler().notify("PlayerExplosion", self.pos)
                if self.lives > 0:
                    self.hp = self.max_hp
                    self.invincible_timer = 120
                else:
                    EventHandler().notify("DestroyObj", self)


class PlayerState(ABC):
    def __init__(self, player):
        self.P = player
        self.name = "Base"
        self.max_ammo = 10
        self.ammo = 10
        self.fire_rate = 15     # Limite do timer entre tiros
        self.cooldown = 0
        self.reload_time = 180  # Tempo total para recarregar (3 segs a 60fps)
        self.reload_progress = 0

    def draw(self, screen):
        sprite = colored_sprite((50, 150, 255), (32, 32))
        screen.blit(sprite, (self.P.pos[0] - 16, self.P.pos[1] - 16))

    def update(self, dt):
        if self.cooldown > 0:
            self.cooldown -= dt

    def reload(self, dt, active=False):
        if self.ammo < self.max_ammo:
            # Segurar R recarrega 3x mais rápido
            rate = 3 if active else 0.5 
            self.reload_progress += dt * rate
            if self.reload_progress >= self.reload_time:
                self.ammo = self.max_ammo
                self.reload_progress = 0

    def can_fire(self):
        return self.cooldown <= 0 and self.ammo > 0

    def get_angle_to_mouse(self):
        mx, my = pygame.mouse.get_pos()
        px, py = self.P.pos
        return math.degrees(math.atan2(my - py, mx - px))

    @abstractmethod
    def action_1(self): pass


class PistolState(PlayerState):
    def __init__(self, player):
        super().__init__(player)
        self.name = "Pistola"
        self.max_ammo = 12
        self.ammo = self.max_ammo
        self.fire_rate = 15

    def action_1(self):
        if self.can_fire():
            self.ammo -= 1
            self.cooldown = self.fire_rate
            angle = self.get_angle_to_mouse()
            b = StraightBullet(tuple(self.P.pos), angle, speed=10)
            EventHandler().notify("SpawnObj", b)


class ShotgunState(PlayerState):
    def __init__(self, player):
        super().__init__(player)
        self.name = "Shotgun"
        self.max_ammo = 6
        self.ammo = self.max_ammo
        self.fire_rate = 45 # Tiro mais lento

    def action_1(self):
        if self.can_fire():
            self.ammo -= 1
            self.cooldown = self.fire_rate
            base_angle = self.get_angle_to_mouse()
            for spread in [-15, 0, 15]:
                b = StraightBullet(tuple(self.P.pos), base_angle + spread, speed=8)
                EventHandler().notify("SpawnObj", b)


class MachineGunState(PlayerState):
    def __init__(self, player):
        super().__init__(player)
        self.name = "Metralhadora"
        self.max_ammo = 30
        self.ammo = self.max_ammo
        self.fire_rate = 6 # Tiro muito rápido
        self.burst_pending = 0

    def update(self, dt):
        super().update(dt)
        
        # Atirar automático segurando o botão
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if mouse_pressed and self.can_fire():
            self.shoot()
            self.burst_pending = 0 
        
        # Finaliza o burst de 3 caso tenha clicado e soltado rápido
        elif self.burst_pending > 0 and self.can_fire():
            self.shoot()
            self.burst_pending -= 1

    def action_1(self):
        # Apenas inicializa o burst no clique (se houver munição)
        if self.ammo > 0:
            self.burst_pending = 3

    def shoot(self):
        self.ammo -= 1
        self.cooldown = self.fire_rate
        angle = self.get_angle_to_mouse()
        b = StraightBullet(tuple(self.P.pos), angle, speed=12)
        EventHandler().notify("SpawnObj", b)