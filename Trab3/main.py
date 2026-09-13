import pygame
import random
import math
from player import Player
from enemy import Enemy
from bullet import Bullet
from util import EventHandler, circle_collistiion

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Twin-Stick Survivor - FSM & Events")
clock = pygame.time.Clock()

player = Player((WIDTH // 2, HEIGHT // 2))
objects = [player]
score = 0

def add_obj(obj):
    if obj not in objects: objects.append(obj)

def remove_obj(obj):
    if obj in objects: objects.remove(obj)

def add_score(pts):
    global score
    score += pts

def handle_explosion(pos):
    for obj in objects[:]:
        if isinstance(obj, Enemy):
            dist = math.hypot(obj.pos[0] - pos[0], obj.pos[1] - pos[1])
            if dist < 200:
                obj.take_damage(999)

EventHandler().subscribe("SpawnObj", add_obj)
EventHandler().subscribe("DestroyObj", remove_obj)
EventHandler().subscribe("EnemyKilled", add_score)
EventHandler().subscribe("PlayerExplosion", handle_explosion)

SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 1200)

def spawn_enemy():
    lado = random.choice(['top', 'bottom', 'left', 'right'])
    if lado == 'top':    pos = (random.randint(0, WIDTH), 0)
    elif lado == 'bottom': pos = (random.randint(0, WIDTH), HEIGHT)
    elif lado == 'left':   pos = (0, random.randint(0, HEIGHT))
    else:                  pos = (WIDTH, random.randint(0, HEIGHT))
    
    enemy = Enemy(pos, player)
    EventHandler().notify("SpawnObj", enemy)

def handle_input(player):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == SPAWN_EVENT:
            spawn_enemy()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                player.action_1()
        elif event.type == pygame.KEYDOWN:
            # Troca manual de armas
            if event.key == pygame.K_1: player.switch_weapon(0)
            elif event.key == pygame.K_2: player.switch_weapon(1)
            elif event.key == pygame.K_3: player.switch_weapon(2)

running = True
font = pygame.font.SysFont(None, 28)

while running:
    handle_input(player)

    for obj in objects[:]:
        obj.update(1)

    bullets = [o for o in objects if isinstance(o, Bullet)]
    enemies = [o for o in objects if isinstance(o, Enemy)]

    for b in bullets:
        for e in enemies:
            if circle_collistiion(b.pos, b.radius, e.pos, e.radius):
                e.take_damage(1)
                b.destroy()
                break

    screen.fill((30, 30, 30))

    for obj in objects:
        obj.draw(screen)

    if player in objects:
        # Lógica de Cores da Arma Baseada na Munição
        w = player.state
        if w.ammo == 0:
            cor_arma = (150, 150, 150) # Cinza (Vazia)
        elif w.ammo > w.max_ammo * 0.5:
            cor_arma = (100, 255, 100) # Verde (> 50%)
        elif w.ammo > w.max_ammo * 0.2:
            cor_arma = (255, 255, 100) # Amarelo (> 20%)
        else:
            cor_arma = (255, 100, 100) # Vermelho (Quase vazia)

        txt_info = font.render(f"Vidas: {player.lives} | Arma [1,2,3]: {w.name} [{w.ammo}/{w.max_ammo}]", True, cor_arma)
        txt_score = font.render(f"Score: {score}", True, (255, 255, 0))
        
        bar_w = 300
        hp_ratio = max(0, player.hp / player.max_hp)
        pygame.draw.rect(screen, (150, 0, 0), (WIDTH//2 - bar_w//2, 15, bar_w, 20))
        pygame.draw.rect(screen, (0, 200, 0), (WIDTH//2 - bar_w//2, 15, int(bar_w * hp_ratio), 20))
        
        screen.blit(txt_info, (10, 15))
        screen.blit(txt_score, (WIDTH - 120, 15))
    else:
        game_over_txt = font.render("GAME OVER", True, (255, 50, 50))
        screen.blit(game_over_txt, (WIDTH//2 - 60, HEIGHT//2))

    pygame.display.flip()
    clock.tick(60)