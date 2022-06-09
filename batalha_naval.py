# Estruturando o programa da batalha naval.

import pygame
import os
import time
import math
from enum import Enum
import spritesheet

WHITE = (255,250,250)
BLACK = (0,0,0)
BLUE = (125,158,192)

#Navio de batalha
class Embarcacao():

    class EstadoCelula(Enum):
        OCULTA = 0
        DESTRUIDA = 1
        VISIVEL = 2

    # Construtor
    def __init__(self, posicao, tamanho, sentido):
        self.posicao = posicao
        self.tamanho = tamanho
        self.sentido = sentido
        
        self.lista_celulas = list()
        for indice_celula in range(len(lista_celulas)):
            lista_celulas[indice_celula] = EstadoCelula.VISIVEL

class Jogador():
    def __init__(self, posicao, tamanho, sentido):
        self.embarcacoes = list()

    def adicionar_embarcacao(self, embarcacao):
        self.embarcacoes.append(embarcacao)


class Game():

    class State(Enum):
        """
            INICIO é a parte do jogo onde cada jogador coloca suas embarcações no 
            seu respectivo tabuleiro
        """
        INICIO_JOGADOR_1 = 0
        INICIO_JOGADOR_2 = 1

        """ 
            VEZ é a parte principal da partida, onde cada jogador escolhe uma célula
            do tabuleiro inimigo para atacar
        """
        VEZ_JOGADOR_1 = 2
        VEZ_JOGADOR_2 = 3

        """ 
            VITORIA é a parte final da partida, na qual algum dos dois jogadores
            destruiu todas as embarcações do inimigo
        """
        VITORIA_JOGADOR_1 = 4
        VITORIA_JOGADOR_2 = 5

    def __init__(self, tamanho_horizontal_cada_tabuleiro, tamanho_vertical_cada_tabuleiro):

        # Variável que indica o estado atual do jogo
        self.estado_jogo = Game.State.INICIO_JOGADOR_1

        # Ajustando as variáveis relacionadas com a tela e inicialização do pygame
        self.qnt_celulas_x_cada_tabuleiro = tamanho_horizontal_cada_tabuleiro
        self.qnt_celulas_y_cada_tabuleiro = tamanho_vertical_cada_tabuleiro
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        pygame.display.init()
        self.margin = 20 # Margens laterais
        self.cell_size = 20  + 1 # Tamanho de cada celula (quadradinho da matriz)

        # Definindo o tamanho horizontal da tela do jogo:
        # 1) Tem que comportar células dos DOIS tabuleiros
        tamanho_horizontal_tela = self.qnt_celulas_x_cada_tabuleiro * self.cell_size * 2
        # 2) Adicionando um pixel para seperar visualmente as células dos DOIS tabuleiros:
        tamanho_horizontal_tela += self.qnt_celulas_x_cada_tabuleiro * 1 * 2
        # 3) Adicionando espaço para a margem esquerda e direita:
        tamanho_horizontal_tela += 2 * self.margin

        # Definindo o tamanho vertical da tela do jogo:
        # 1) Tem que comportar células verticais apenas em relação a um tabuleiro:
        tamanho_vertical_tela = self.qnt_celulas_y_cada_tabuleiro * self.cell_size
        # 2) Adicionando um pixel para seperar as células visualmente:
        tamanho_vertical_tela += self.qnt_celulas_x_cada_tabuleiro * 1
        # 3) Adicionando espaço para a margem superior e inferior:
        tamanho_vertical_tela += 2 * self.margin

        self.screen_size = (tamanho_horizontal_tela, tamanho_vertical_tela)
        self.board = pygame.display.set_mode(self.screen_size)

        # Carregando as imagens do spritesheet criado até agora
        ss = spritesheet.spritesheet('battle_ship_sprites.png')
        self.SEA_SPRITE = ss.image_at((0, 0, 20, 20)) # Imagem do mar sem nada
        self.BARCOS = [] # Imagens das três celulas das embarcações horizontais
        # Load two images into an array, their transparent bit is (255, 255, 255)
        self.BARCOS = ss.images_at([
            (20, 0, 20, 20),  # Celula esquerda
            (40, 0, 20, 20),  # Celula centro
            (60, 0, 20, 20)])  # Celula direita

    def clear_screen(self):
        """
            Função que limpa os pixels da tela na memória para exibir apenas o mar com
            o tabuleiro vazio (Não imprime na tela ainda, pois outras funções vão definir
            os elementos do jogo, como embarcações abatidas, tiros errados etc).
            Ao final de todas as chamadas de funções visuais, o jogo é finalmente impresso
            na tela. Isso evita glitches em computadores mais lentos, pois toda a informação
            da tela é impressa de uma única vez.
        """
        self.board.fill(BLACK) # Cor de fundo
        quantos = 0
        for x in range(self.margin + 1, self.screen_size[0] - self.margin, self.cell_size):
            for y in range(self.margin + 1, self.screen_size[1] - self.margin, self.cell_size):
                # Desenhando as células do mar
                self.board.blit(self.SEA_SPRITE, (x, y))

        central_line = [(self.screen_size[0]//2, 0),  # Ponto inicial
                        (self.screen_size[0]//2, self.screen_size[1])]  # Ponto final
        pygame.draw.line(self.board, (255, 0, 0), central_line[0], central_line[1], 2)

    def celula_por_posicao(self, posicao):
        x = (posicao[0] - self.margin) // (self.cell_size)
        y = (posicao[1] - self.margin) // (self.cell_size)
        x = self.margin + 1 + x * (self.cell_size)
        y = self.margin + 1 + y * (self.cell_size)
        return (x, y)

    def indice_tabuleiro_jogador_por_posicao(self, posicao):
        """
            Retorna um índice referente à célula da matriz do tabuleiro.
            Mapeia o índice para uma posição da matriz do jogo.
            Tipicamente, para um tabuleiro 20x20, o retorno é uma 2-tupla
            da forma: (i, j), 0 <= i, j <= 19.
        """
        area_jogador_1 = pygame.Rect(
                        self.margin + 1,
                        self.margin + 1,
                        self.cell_size * self.qnt_celulas_x_cada_tabuleiro,
                        self.cell_size * self.qnt_celulas_y_cada_tabuleiro)

        area_jogador_2 = pygame.Rect(
                        (self.screen_size[0] // 2) + 1,
                        self.margin + 1,
                        self.cell_size * self.qnt_celulas_x_cada_tabuleiro,
                        self.cell_size * self.qnt_celulas_y_cada_tabuleiro)
        
        if (area_jogador_1.collidepoint(posicao)):
            # Clicou na regiao do jogador 1
            self.celula_por_posicao(posicao)
        elif (area_jogador_2.collidepoint(posicao)):
            # Clicou na regiao do jogador 2
            pass
        else:
            # Região não pertence a nenhum dos tabuleiros
            pass


    def draw_embarcacao(self, posicao):
        pos_inicial = self.celula_por_posicao(posicao)
        for i in range(3):
            pos_atual = (pos_inicial[0] + (i * self.cell_size), pos_inicial[1])
            self.board.blit(self.BARCOS[i], pos_atual)
    
    def draw_embarcacoes(self, barcos):
        for barco in barcos:
            self.draw_embarcacao(barco)

    def reagir_a_clique(self, posicao_clique):
        if (self.estado_jogo == Game.State.INICIO_JOGADOR_1):
            regiao_clicavel = pygame.Rect(
                        self.margin + 1,
                        self.margin + 1,
                        self.cell_size * 18,
                        self.cell_size * 20)
            if (regiao_clicavel.collidepoint(posicao_clique)):
                nova_embarcacao = Embarcacao()
                self.jogador1.barcos.append(celula_por_posicao(posicao_clique))

    def main_game_loop(self):
        leave = False
        lista_barcos = []  # Apenas para testar!! Retirar depois.
        while leave == False:
            self.clear_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    leave = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.reagir_a_clique(pygame.mouse.get_pos())
            self.draw_embarcacoes(lista_barcos)
            pygame.display.update()


if __name__ == "__main__":
    game = Game(20, 20)
    game.clear_screen()
    game.main_game_loop() # Chamada bloqueante
    pygame.quit() # Só chega aqui quando o game_loop acaba