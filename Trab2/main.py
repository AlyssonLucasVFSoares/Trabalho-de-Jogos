import pygame
from grid import Grid
from skynet import JogoDaVelhaAI

pygame.init()
pygame.font.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))  
font = pygame.font.Font(None, 36)

# Sprites
sprite_x = pygame.Surface((80, 80))
sprite_x.fill((0, 0, 0))
sprite_x.set_colorkey((0, 0, 0)) 
pygame.draw.line(sprite_x, (255, 50, 50), (10, 10), (70, 70), 10)
pygame.draw.line(sprite_x, (255, 50, 50), (70, 10), (10, 70), 10)

sprite_o = pygame.Surface((80, 80))
sprite_o.fill((0, 0, 0))
sprite_o.set_colorkey((0, 0, 0))
pygame.draw.circle(sprite_o, (50, 150, 255), (40, 40), 35, 10)

grid = Grid(x=250, y=150, sprites=[sprite_x, sprite_o], rows=3, cols=3, cell_size=100)
ai = JogoDaVelhaAI(player_id=2)

estado_jogo = "MENU" # Pode ser "MENU" ou "JOGANDO"
modo_jogo = "PVP"    # Pode ser "PVP" ou "PVE"

while True: 
    # Turno da IA
    if estado_jogo == "JOGANDO" and modo_jogo == "PVE" and grid.turn == 2 and not grid.game_over:
        pygame.time.wait(1000) # Pequena pausa para parecer que a IA está pensando
        jogada = ai.jogar(grid)
        if jogada:
            grid.try_play(jogada[0], jogada[1])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        if estado_jogo == "MENU":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    modo_jogo = "PVP"
                    grid.reset_match()
                    estado_jogo = "JOGANDO"
                elif event.key == pygame.K_2:
                    modo_jogo = "PVE"
                    grid.reset_match()
                    estado_jogo = "JOGANDO"

        elif estado_jogo == "JOGANDO":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]: 
                    if grid.game_over:
                        grid.reset_match()
                    elif grid.turn == 1 or modo_jogo == "PVP":
                        mx, my = pygame.mouse.get_pos()
                        for r in range(grid.rows):
                            for c in range(grid.cols):
                                if grid.cells[r][c].rect.collidepoint(mx, my):
                                    grid.try_play(r, c)
                                    grid.cursor_r, grid.cursor_c = r, c
                                    grid.update_focus()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    estado_jogo = "MENU"
                elif grid.game_over and event.key == pygame.K_r:
                    grid.reset_match()
                elif grid.turn == 1 or modo_jogo == "PVP":
                    if event.key in [pygame.K_UP, pygame.K_w]: grid.move_cursor(-1, 0)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]: grid.move_cursor(1, 0)
                    elif event.key in [pygame.K_LEFT, pygame.K_a]: grid.move_cursor(0, -1)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]: grid.move_cursor(0, 1)
                    elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        grid.try_play(grid.cursor_r, grid.cursor_c)

    grid.update(1)
    screen.fill((30, 30, 30))

    if estado_jogo == "MENU":
        txt_titulo = font.render("JOGO DA VELHA 2.0", True, (255, 255, 255))
        txt_pvp = font.render("[1] Jogar contra um Amigo", True, (100, 255, 100))
        txt_pve = font.render("[2] Jogar contra o Skynet", True, (100, 100, 255))
        screen.blit(txt_titulo, (270, 200))
        screen.blit(txt_pvp, (240, 300))
        screen.blit(txt_pve, (240, 350))
    else:
        txt_p1_score = font.render(f"Vitórias X: {grid.score_p1}", True, (255, 50, 50))
        txt_p2_score = font.render(f"Vitórias O: {grid.score_p2}", True, (50, 150, 255))
        screen.blit(txt_p1_score, (150, 20))
        screen.blit(txt_p2_score, (500, 20))

        grid.draw(screen)

        if grid.game_over:
            cor = (255, 50, 50) if grid.winner == 1 else (50, 150, 255)
            txt_fim = font.render(f"FIM DE JOGO: Jogador {grid.winner} VENCEU!", True, cor)
            txt_opcoes = font.render("[R] Revanche | [ESC] Menu", True, (100, 255, 100))
            screen.blit(txt_fim, (180, 90))
            screen.blit(txt_opcoes, (220, 500))
        else:
            cor = (255, 50, 50) if grid.turn == 1 else (50, 150, 255)
            nome_jogador = "IA (O)" if modo_jogo == "PVE" and grid.turn == 2 else f"Jogador {grid.turn}"
            txt_turno = font.render(f"Turno: {nome_jogador}", True, cor)
            screen.blit(txt_turno, (280, 90))

    pygame.display.flip()