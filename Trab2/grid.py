from abc import ABC, abstractmethod
import pygame

class obj(ABC):
    def __init__(self, x, y, sprites):
        self.x = x
        self.y = y
        self.sprites = sprites
    def draw(self, screen):
        pass
    @abstractmethod
    def update(self, dt):
        pass

class Cell(obj):
    def __init__(self, x, y, sprites, row, col, size):
        super().__init__(x, y, sprites)
        self.row = row
        self.col = col
        self.size = size
        self.rect = pygame.Rect(x, y, size, size)
        self.state = 0 
        self.is_focused = False
        self.is_blinking = False 

    # NOVO: Recebe a cor da borda (border_color) do turno atual
    def draw(self, screen, border_color):
        color = (120, 120, 120) if self.is_focused else (50, 50, 50)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2) # Linha com a cor do turno
        
        draw_sprite = True
        if self.is_blinking:
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                draw_sprite = False

        if self.state != 0 and len(self.sprites) >= self.state and draw_sprite:
            sprite = self.sprites[self.state - 1]
            screen.blit(sprite, (self.x + 10, self.y + 10))

    def update(self, dt):
        pass

class Grid(obj):
    def __init__(self, x, y, sprites, rows=3, cols=3, cell_size=100):
        super().__init__(x, y, sprites)
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.cells = []
        
        self.turn = 1 
        self.history_p1 = [] 
        self.history_p2 = []
        self.game_over = False 
        self.winner = 0        
        
        # NOVO: Placar de vitórias
        self.score_p1 = 0
        self.score_p2 = 0
        
        self.cursor_r = 0
        self.cursor_c = 0
        
        for r in range(rows):
            row_list = []
            for c in range(cols):
                cx = self.x + c * cell_size
                cy = self.y + r * cell_size
                row_list.append(Cell(cx, cy, sprites, r, c, cell_size))
            self.cells.append(row_list)
            
        self.update_focus()
        self.update_blinking()

    # NOVO: Função para zerar o tabuleiro para a revanche
    def reset_match(self):
        self.game_over = False
        self.winner = 0
        self.history_p1.clear()
        self.history_p2.clear()
        self.turn = 1
        for r in range(self.rows):
            for c in range(self.cols):
                self.cells[r][c].state = 0
                self.cells[r][c].is_blinking = False
        self.update_blinking()

    def update_focus(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.cells[r][c].is_focused = (r == self.cursor_r and c == self.cursor_c)

    def update_blinking(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.cells[r][c].is_blinking = False
        
        if self.game_over: return
        
        if self.turn == 1 and len(self.history_p1) == 3:
            r, c = self.history_p1[0]
            self.cells[r][c].is_blinking = True
            
        if self.turn == 2 and len(self.history_p2) == 3:
            r, c = self.history_p2[0]
            self.cells[r][c].is_blinking = True

    def move_cursor(self, dr, dc):
        if self.game_over: return
        self.cursor_r = (self.cursor_r + dr) % self.rows
        self.cursor_c = (self.cursor_c + dc) % self.cols
        self.update_focus()

    def check_win(self):
        for p in [1, 2]:
            won = False
            # Linhas e Colunas
            for i in range(3):
                if self.cells[i][0].state == p and self.cells[i][1].state == p and self.cells[i][2].state == p:
                    won = True
                if self.cells[0][i].state == p and self.cells[1][i].state == p and self.cells[2][i].state == p:
                    won = True
            # Diagonais
            if self.cells[0][0].state == p and self.cells[1][1].state == p and self.cells[2][2].state == p:
                won = True
            if self.cells[0][2].state == p and self.cells[1][1].state == p and self.cells[2][0].state == p:
                won = True
                
            if won:
                self.winner = p
                self.game_over = True
                if p == 1:
                    self.score_p1 += 1
                else:
                    self.score_p2 += 1
                return # Encerra a verificação

    def try_play(self, r, c):
        if self.game_over: return 
        
        cell = self.cells[r][c]
        if cell.state == 0:
            cell.state = self.turn
            
            if self.turn == 1:
                self.history_p1.append((r, c))
                if len(self.history_p1) > 3:
                    old_r, old_c = self.history_p1.pop(0)
                    self.cells[old_r][old_c].state = 0
                self.turn = 2
            else:
                self.history_p2.append((r, c))
                if len(self.history_p2) > 3:
                    old_r, old_c = self.history_p2.pop(0)
                    self.cells[old_r][old_c].state = 0
                self.turn = 1
            
            self.check_win() 
            self.update_blinking()

    def draw(self, screen):
        # NOVO: Define a cor da borda com base no turno ou em quem venceu
        if self.game_over:
            border_color = (255, 50, 50) if self.winner == 1 else (50, 150, 255)
        else:
            border_color = (255, 50, 50) if self.turn == 1 else (50, 150, 255)
            
        for r in range(self.rows):
            for c in range(self.cols):
                self.cells[r][c].draw(screen, border_color)

    def update(self, dt):
        pass