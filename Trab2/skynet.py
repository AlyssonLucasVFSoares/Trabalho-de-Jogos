import random

class JogoDaVelhaAI:
    def __init__(self, player_id=2):
        self.player_id = player_id
        self.opponent_id = 1 if player_id == 2 else 2

    def _simular_vitoria(self, grid, r, c, player_turn):
        # Copia o estado atual da grade para não alterar o jogo real
        matriz = [[grid.cells[i][j].state for j in range(3)] for i in range(3)]
        matriz[r][c] = player_turn
        
        # Simula o desaparecimento da peça mais antiga se for a 4ª jogada
        historico = grid.history_p2 if player_turn == 2 else grid.history_p1
        if len(historico) == 3:
            old_r, old_c = historico[0]
            matriz[old_r][old_c] = 0 

        # Confere Linhas e Colunas na matriz simulada
        for i in range(3):
            if matriz[i][0] == player_turn and matriz[i][1] == player_turn and matriz[i][2] == player_turn: 
                return True
            if matriz[0][i] == player_turn and matriz[1][i] == player_turn and matriz[2][i] == player_turn: 
                return True
                
        # Confere Diagonais na matriz simulada
        if matriz[0][0] == player_turn and matriz[1][1] == player_turn and matriz[2][2] == player_turn: 
            return True
        if matriz[0][2] == player_turn and matriz[1][1] == player_turn and matriz[2][0] == player_turn: 
            return True
        
        return False

    def jogar(self, grid):
        casas_vazias = [(r, c) for r in range(grid.rows) for c in range(grid.cols) if grid.cells[r][c].state == 0]
        if not casas_vazias: 
            return None

        # 1. Tentar ganhar
        for r, c in casas_vazias:
            if self._simular_vitoria(grid, r, c, self.player_id):
                return (r, c)

        # 2. Bloquear o jogador humano
        for r, c in casas_vazias:
            if self._simular_vitoria(grid, r, c, self.opponent_id):
                return (r, c)

        # 3. Dominar o centro
        if (1, 1) in casas_vazias:
            return (1, 1)

        # 4. Jogada aleatória
        return random.choice(casas_vazias)