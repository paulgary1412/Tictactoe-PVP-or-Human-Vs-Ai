import sys
import pygame
import random
import numpy as np
import copy

from constants import *

# --- PYGAME SETUP ---

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT + 150))  # Added extra space for buttons and winner display
pygame.display.set_caption('TIC TAC TOE AI')  # Fixed typo here
screen.fill(BG_COLOR)

# --- CLASSES ---

class Board:
    def __init__(self):
        self.squares = np.zeros((ROWS, COLS))
        self.empty_sqrs = self.squares  # [squares]
        self.marked_sqrs = 0

    def final_state(self, show=False):
        '''
            @return 0 if there is no win yet
            @return 1 if player 1 wins
            @return 2 if player 2 wins
        '''

        # vertical wins
        for col in range(COLS):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] != 0:
                if show:
                    color = CIRC_COLOR if self.squares[0][col] == 2 else CROSS_COLOR
                    iPos = (col * SQSIZE + SQSIZE // 2, 20)
                    fPos = (col * SQSIZE + SQSIZE // 2, HEIGHT - 20)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[0][col]

        # horizontal wins
        for row in range(ROWS):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] != 0:
                if show:
                    color = CIRC_COLOR if self.squares[row][0] == 2 else CROSS_COLOR
                    iPos = (20, row * SQSIZE + SQSIZE // 2)
                    fPos = (WIDTH - 20, row * SQSIZE + SQSIZE // 2)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[row][0]

        # desc diagonal
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            if show:
                color = CIRC_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, 20)
                fPos = (WIDTH - 20, HEIGHT - 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return self.squares[1][1]

        # asc diagonal
        if self.squares[2][0] == self.squares[1][1] == self.squares[0][2] != 0:
            if show:
                color = CIRC_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, HEIGHT - 20)
                fPos = (WIDTH - 20, 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return self.squares[1][1]

        # no win yet
        return 0

    def mark_sqr(self, row, col, player):
        self.squares[row][col] = player
        self.marked_sqrs += 1

    def empty_sqr(self, row, col):
        return self.squares[row][col] == 0

    def get_empty_sqrs(self):
        empty_sqrs = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.empty_sqr(row, col):
                    empty_sqrs.append((row, col))
        
        return empty_sqrs

    def isfull(self):
        return self.marked_sqrs == 9

    def isempty(self):
        return self.marked_sqrs == 0

class AI:
    def __init__(self, level=1, player=2):
        self.level = level
        self.player = player

    # --- RANDOM ---

    def rnd(self, board):
        empty_sqrs = board.get_empty_sqrs()
        idx = random.randrange(0, len(empty_sqrs))

        return empty_sqrs[idx]  # (row, col)

    # --- MINIMAX ---

    def minimax(self, board, maximizing):
        
        # terminal case
        case = board.final_state()

        # player 1 wins
        if case == 1:
            return 1, None  # eval, move

        # player 2 wins
        if case == 2:
            return -1, None

        # draw
        elif board.isfull():
            return 0, None

        if maximizing:
            max_eval = -100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, 1)
                eval = self.minimax(temp_board, False)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)

            return max_eval, best_move

        elif not maximizing:
            min_eval = 100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.player)
                eval = self.minimax(temp_board, True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)

            return min_eval, best_move

    # --- MAIN EVAL ---

    def eval(self, main_board):
            if self.level == 0:
                # random choice
                eval = 'random'
                move = self.rnd(main_board)
            else:
                # minimax algo choice
                eval, move = self.minimax(main_board, False)

            if move is None:
                print("No valid move found!")
            else:
                print(f'AI has chosen to mark the square in pos {move} with an eval of: {eval}')

            return move  # row, col

class Game:
    def __init__(self):
        self.board = Board()
        self.ai_1 = AI(player=1)  # First AI agent as player 1
        self.ai_2 = AI(player=2)  # Second AI agent as player 2
        self.player = 1  # 1-cross  #2-circles
        self.gamemode = 'pvp'  # pvp, ai_vs_ai, or ai_vs_human
        self.running = True
        self.show_lines()
        self.create_buttons()
        self.create_input_fields()
        self.players = ['Player 1', 'Player 2']  # Default player names

    # --- DRAW METHODS ---

    def show_lines(self):
        # bg
        screen.fill(BG_COLOR)

        # vertical
        pygame.draw.line(screen, LINE_COLOR, (SQSIZE, 0), (SQSIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (WIDTH - SQSIZE, 0), (WIDTH - SQSIZE, HEIGHT), LINE_WIDTH)

        # horizontal
        pygame.draw.line(screen, LINE_COLOR, (0, SQSIZE), (WIDTH, SQSIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (0, HEIGHT - SQSIZE), (WIDTH, HEIGHT - SQSIZE), LINE_WIDTH)

    def draw_fig(self, row, col):
        if self.player == 1:
            # draw cross
            # desc line
            start_desc = (col * SQSIZE + OFFSET, row * SQSIZE + OFFSET)
            end_desc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_desc, end_desc, CROSS_WIDTH)
            # asc line
            start_asc = (col * SQSIZE + OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            end_asc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_asc, end_asc, CROSS_WIDTH)
        
        elif self.player == 2:
            # draw circle
            center = (col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2)
            pygame.draw.circle(screen, CIRC_COLOR, center, RADIUS, CIRC_WIDTH)

    # --- OTHER METHODS ---

    def create_buttons(self):
        self.buttons = {
            'game_mode': pygame.Rect(10, HEIGHT + 20, 150, 30),
            'difficulty': pygame.Rect(175, HEIGHT + 20, 150, 30),
            'restart': pygame.Rect(340, HEIGHT + 20, 150, 30)
        }
        self.button_texts = {
            'game_mode': 'Mode: PvP',
            'difficulty': 'Difficulty: Easy',
            'restart': 'Restart'
        }
        self.render_buttons()

    def get_button_font(self, size=25):
        return pygame.font.Font(None, size)
    def render_buttons(self):
        for key, rect in self.buttons.items():
            pygame.draw.rect(screen, (100, 100, 100), rect)
            font = self.get_button_font(size=25)  # Adjust font size here
            text_surf = font.render(self.button_texts[key], True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)

    def handle_button_click(self, pos):
        for key, rect in self.buttons.items():
            if rect.collidepoint(pos):
                if key == 'game_mode':
                    self.change_gamemode()
                elif key == 'difficulty':
                    self.change_difficulty()
                elif key == 'restart':
                    self.reset()
                    # Clear the screen and redraw everything
                    self.show_lines()
                    self.render_buttons()
                    self.render_input_fields()
                    pygame.display.update()


    def create_input_fields(self):
        self.input_rects = [
            pygame.Rect(40, HEIGHT + 60, 200, 30),
            pygame.Rect(250, HEIGHT + 60, 200, 30)
        ]
        self.input_texts = ['', '']
        self.input_active = [False, False]

    def render_input_fields(self):
        for idx, rect in enumerate(self.input_rects):
            pygame.draw.rect(screen, (255, 255, 255), rect)
            font = pygame.font.Font(None, 36)
            text_surf = font.render(self.input_texts[idx], True, (0, 0, 0))
            screen.blit(text_surf, (rect.x + 5, rect.y + 5))
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)

    def handle_input_field_click(self, pos):
        for idx, rect in enumerate(self.input_rects):
            if rect.collidepoint(pos):
                self.input_active[idx] = True
            else:
                self.input_active[idx] = False

    def handle_input_field_event(self, event):
        for idx in range(2):
            if self.input_active[idx] and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.input_texts[idx].strip():
                        self.players[idx] = self.input_texts[idx].strip()
                    self.input_texts[idx] = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.input_texts[idx] = self.input_texts[idx][:-1]
                else:
                    self.input_texts[idx] += event.unicode

    def change_gamemode(self):
        if self.gamemode == 'pvp':
            self.gamemode = 'ai_vs_human'
            self.players[1] = 'Computer'
        elif self.gamemode == 'ai_vs_human':
            self.gamemode = 'ai_vs_ai'
            self.players[0] = 'Computer 1'
            self.players[1] = 'Computer 2'
        else:
            self.gamemode = 'pvp'
            self.players[0] = 'Player 1'
            self.players[1] = 'Player 2'
        self.button_texts['game_mode'] = f'Game Mode: {self.gamemode.replace("_", " ").title()}'
        self.render_buttons()

    def change_difficulty(self):
        self.ai_1.level = 0 if self.ai_1.level == 1 else 1
        self.ai_2.level = self.ai_1.level  # Ensure both AIs have the same difficulty
        self.button_texts['difficulty'] = f'Difficulty: {"Easy" if self.ai_1.level == 0 else "Hard"}'
        self.render_buttons()

    def make_move(self, row, col):
        self.board.mark_sqr(row, col, self.player)
        self.draw_fig(row, col)
        self.next_turn()

    def next_turn(self):
        self.player = self.player % 2 + 1

    def isover(self):
        return self.board.final_state(show=True) != 0 or self.board.isfull()

    def display_winner(self, winner):
        font = pygame.font.Font(None, 48)
        winner_text = f'Congratulations,{winner} you have won the game !'
        text_surf = font.render(winner_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT + 120))
        screen.blit(text_surf, text_rect)

    def reset(self):
        self.__init__()

def main():
    # --- OBJECTS ---

    game = Game()
    board = game.board
    ai_1 = game.ai_1
    ai_2 = game.ai_2

    # --- MAINLOOP ---

    while True:
        
        # pygame events
        for event in pygame.event.get():

            # quit event
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # keydown event
            if event.type == pygame.KEYDOWN:

                # g-gamemode
                if event.key == pygame.K_g:
                    game.change_gamemode()

                # r-restart
                if event.key == pygame.K_r:
                    game.reset()
                    board = game.board
                    ai_1 = game.ai_1
                    ai_2 = game.ai_2

                # 0-random ai
                if event.key == pygame.K_0:
                    ai_1.level = 0
                    ai_2.level = 0
                
                # 1-random ai
                if event.key == pygame.K_1:
                    ai_1.level = 1
                    ai_2.level = 1

            # click event
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if pos[1] > HEIGHT:
                    game.handle_button_click(pos)
                    game.handle_input_field_click(pos)
                else:
                    row = pos[1] // SQSIZE
                    col = pos[0] // SQSIZE
                    
                    # human mark sqr
                    if board.empty_sqr(row, col) and game.running and game.gamemode != 'ai_vs_ai':
                        game.make_move(row, col)

                        if game.isover():
                            game.running = False
                            winner = game.players[int(board.final_state()) - 1] if board.final_state() != 0 else "No one"
                            game.display_winner(winner)

            # handle input field event
            game.handle_input_field_event(event)

        # AI move
        if game.gamemode == 'ai_vs_human' and game.player == ai_2.player and game.running:
            # update the screen
            pygame.display.update()

            # eval
            row, col = ai_2.eval(board)
            game.make_move(row, col)

            if game.isover():
                game.running = False
                winner = game.players[int(board.final_state()) - 1] if board.final_state() != 0 else "No one"
                game.display_winner(winner)

        # AI vs AI move
        if game.gamemode == 'ai_vs_ai' and game.running:
            pygame.display.update()
            
            if game.player == ai_1.player:
                row, col = ai_1.eval(board)
            else:
                row, col = ai_2.eval(board)
                
            game.make_move(row, col)

            if game.isover():
                game.running = False
                winner = game.players[int(board.final_state()) - 1] if board.final_state() != 0 else "No one"
                game.display_winner(winner)
            
            pygame.time.delay(1000)

        game.render_input_fields()
        pygame.display.update()

main()
