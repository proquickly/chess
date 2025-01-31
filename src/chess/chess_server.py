import os
import pprint
import functools
import time
import multiprocessing
import random
import pygame

pp = pprint.pprint

def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"Ran {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer

class Piece:
    def __init__(self, color):
        self.color = color
    def can_move_along_row(self, sr, sc, er, ec, board):
        return sr == er
    def can_move_along_col(self, sr, sc, er, ec, board):
        return sc == ec
    def can_move_along_diagonal(self, sr, sc, er, ec, board):
        return abs(sr - er) == abs(sc - ec)
    def get_legal_moves(self, position, board):
        raise NotImplementedError

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
    def get_legal_moves(self, position, board):
        moves = []
        x, y = position
        if self.color == 'white':
            if x - 1 >= 0 and board.get((x - 1, y)) is None:
                moves.append((x - 1, y))
                if x == 6 and board.get((x - 2, y)) is None:
                    moves.append((x - 2, y))
            for dy in [-1, 1]:
                nx, ny = x - 1, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    occupant = board.get((nx, ny))
                    if occupant and occupant.color != self.color:
                        moves.append((nx, ny))
        else:
            if x + 1 <= 7 and board.get((x + 1, y)) is None:
                moves.append((x + 1, y))
                if x == 1 and board.get((x + 2, y)) is None:
                    moves.append((x + 2, y))
            for dy in [-1, 1]:
                nx, ny = x + 1, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    occupant = board.get((nx, ny))
                    if occupant and occupant.color != self.color:
                        moves.append((nx, ny))
        return moves

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
    def get_legal_moves(self, position, board):
        moves = []
        x, y = position
        candidates = [
            (-2, -1), (-2, +1),
            (+2, -1), (+2, +1),
            (-1, -2), (-1, +2),
            (+1, -2), (+1, +2)
        ]
        for dx, dy in candidates:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                occupant = board.get((nx, ny))
                if occupant is None or occupant.color != self.color:
                    moves.append((nx, ny))
        return moves

class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
    def get_legal_moves(self, position, board):
        moves = []
        x, y = position
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                occupant = board.get((nx, ny))
                if occupant is None:
                    moves.append((nx, ny))
                else:
                    if occupant.color != self.color:
                        moves.append((nx, ny))
                    break
                nx += dx
                ny += dy
        return moves

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False
    def get_legal_moves(self, position, board):
        moves = []
        x, y = position
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                occupant = board.get((nx, ny))
                if occupant is None:
                    moves.append((nx, ny))
                else:
                    if occupant.color != self.color:
                        moves.append((nx, ny))
                    break
                nx += dx
                ny += dy
        return moves

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
    def get_legal_moves(self, position, board):
        moves = []
        x, y = position
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                occupant = board.get((nx, ny))
                if occupant is None:
                    moves.append((nx, ny))
                else:
                    if occupant.color != self.color:
                        moves.append((nx, ny))
                    break
                nx += dx
                ny += dy
        return moves

class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False
    def get_legal_moves(self, position, board):
        moves = []
        x, y = position
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                occupant = board.get((nx, ny))
                if occupant is None or occupant.color != self.color:
                    moves.append((nx, ny))
        if not self.has_moved:
            if self._can_castle_kingside(position, board):
                moves.append((x, y + 2))
            if self._can_castle_queenside(position, board):
                moves.append((x, y - 2))
        return moves
    def _can_castle_kingside(self, position, board):
        x, y = position
        rook = board.get((x, 7))
        if not isinstance(rook, Rook) or rook.has_moved:
            return False
        for col in range(y + 1, 7):
            if board.get((x, col)) is not None:
                return False
        return self._is_path_safe_for_castling((x, y), (x, 7), board)
    def _can_castle_queenside(self, position, board):
        x, y = position
        rook = board.get((x, 0))
        if not isinstance(rook, Rook) or rook.has_moved:
            return False
        for col in range(1, y):
            if board.get((x, col)) is not None:
                return False
        return self._is_path_safe_for_castling((x, y), (x, 0), board)
    def _is_path_safe_for_castling(self, from_pos, to_pos, board):
        x, y = from_pos
        step = 1 if y < to_pos[1] else -1
        for col in range(y, to_pos[1] + step, step):
            if self._is_square_attacked((x, col), board):
                return False
        return True
    def _is_square_attacked(self, position, board):
        for piece_pos, piece in board.items():
            if piece.color != self.color:
                if position in piece.get_legal_moves(piece_pos, board):
                    return True
        return False

class Player:
    def __init__(self):
        self.is_my_turn = None
    def move(self, piece_from_position, piece_to_position):
        pass

def get_piece_value(piece):
    values = {
        'Pawn': 1,
        'Knight': 3,
        'Bishop': 3,
        'Rook': 5,
        'Queen': 9,
        'King': 1000
    }
    return values.get(type(piece).__name__, 0)

class Bot(Player):
    def __init__(self, color):
        super().__init__()
        self.color = color
    def get_possible_bot_moves(self, board):
        manager = multiprocessing.Manager()
        possible_moves = manager.list()
        processes = []
        for row in range(8):
            for col in range(8):
                piece = board.get((row, col))
                if piece and piece.color == self.color:
                    proc = multiprocessing.Process(
                        target=self.get_legal_moves_worker,
                        args=((row, col), board, possible_moves)
                    )
                    processes.append(proc)
                    proc.start()
        for proc in processes:
            proc.join()
        return list(possible_moves)
    def get_legal_moves_worker(self, position, board, possible_moves):
        piece = board[position]
        if piece:
            legal_moves = piece.get_legal_moves(position, board)
            for move in legal_moves:
                possible_moves.append((position, move))
    def select_move(self, moves, game):
        best_move = None
        highest_capture_value = 0
        for (start_pos, end_pos) in moves:
            target_piece = game.board.get(end_pos)
            if target_piece and target_piece.color != self.color:
                target_value = get_piece_value(target_piece)
                if target_value > highest_capture_value:
                    highest_capture_value = target_value
                    best_move = (start_pos, end_pos)
        if not best_move and moves:
            best_move = random.choice(moves)
        return best_move
    def make_move(self, game, move):
        if not move:
            return
        start_pos, end_pos = move
        piece = game.board.get(start_pos)
        if piece:
            del game.board[start_pos]
            game.board[end_pos] = piece
            game.move_piece(start_pos, end_pos)
    def play_turn(self, game):
        possible_moves = self.get_possible_bot_moves(game.board)
        selected_move = self.select_move(possible_moves, game)
        self.make_move(game, selected_move)

class Game:
    @classmethod
    def build_game(cls):
        square_size = 60
        width, height = square_size * 8, square_size * 8
        screen = pygame.display.set_mode((width, height))
        board = {}
        board[(0, 0)] = Rook("black")
        board[(0, 1)] = Knight("black")
        board[(0, 2)] = Bishop("black")
        board[(0, 3)] = Queen("black")
        board[(0, 4)] = King("black")
        board[(0, 5)] = Bishop("black")
        board[(0, 6)] = Knight("black")
        board[(0, 7)] = Rook("black")
        for col in range(8):
            board[(1, col)] = Pawn("black")
        board[(7, 0)] = Rook("white")
        board[(7, 1)] = Knight("white")
        board[(7, 2)] = Bishop("white")
        board[(7, 3)] = Queen("white")
        board[(7, 4)] = King("white")
        board[(7, 5)] = Bishop("white")
        board[(7, 6)] = Knight("white")
        board[(7, 7)] = Rook("white")
        for col in range(8):
            board[(6, col)] = Pawn("white")
        bot = Bot("black")
        return cls(board, square_size, screen, bot)

    def __init__(self, board, square_size, screen, bot):
        self.board = board
        self.square_size = square_size
        self.screen = screen
        self.bot = bot
        self.turn = "white"
        self.display_pieces = {}
        self.piece_filenames = {
            "bK": "bK.png", "bQ": "bQ.png", "bR": "bR.png",
            "bB": "bB.png", "bN": "bN.png", "bp": "bp.png",
            "wK": "wK.png", "wQ": "wQ.png", "wR": "wR.png",
            "wB": "wB.png", "wN": "wN.png", "wp": "wp.png",
        }
        self.piece_images = {}
        for code, fname in self.piece_filenames.items():
            path = os.path.join("..", "images", fname)
            img = pygame.image.load(path)
            img = pygame.transform.smoothscale(img, (self.square_size, self.square_size))
            self.piece_images[code] = img
        for (r, c), piece in self.board.items():
            if piece.color == "black":
                if isinstance(piece, Rook):
                    self.display_pieces[piece] = "bR"
                elif isinstance(piece, Knight):
                    self.display_pieces[piece] = "bN"
                elif isinstance(piece, Bishop):
                    self.display_pieces[piece] = "bB"
                elif isinstance(piece, Queen):
                    self.display_pieces[piece] = "bQ"
                elif isinstance(piece, King):
                    self.display_pieces[piece] = "bK"
                elif isinstance(piece, Pawn):
                    self.display_pieces[piece] = "bp"
            else:
                if isinstance(piece, Rook):
                    self.display_pieces[piece] = "wR"
                elif isinstance(piece, Knight):
                    self.display_pieces[piece] = "wN"
                elif isinstance(piece, Bishop):
                    self.display_pieces[piece] = "wB"
                elif isinstance(piece, Queen):
                    self.display_pieces[piece] = "wQ"
                elif isinstance(piece, King):
                    self.display_pieces[piece] = "wK"
                elif isinstance(piece, Pawn):
                    self.display_pieces[piece] = "wp"

    def move_piece(self, from_square, to_square):
        piece = self.board.get(from_square)
        if piece:
            legal_moves = piece.get_legal_moves(from_square, self.board)
            if to_square in legal_moves:
                del self.board[from_square]
                self.board[to_square] = piece
                return True
        return False

    def draw_board(self):
        colors = [(233, 236, 239), (125, 135, 150)]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                rect = pygame.Rect(col * self.square_size,
                                   row * self.square_size,
                                   self.square_size,
                                   self.square_size)
                pygame.draw.rect(self.screen, color, rect)
        for (r, c), piece in self.board.items():
            code = self.display_pieces.get(piece, None)
            if code:
                image = self.piece_images.get(code, None)
                if image:
                    x_pos = c * self.square_size
                    y_pos = r * self.square_size
                    self.screen.blit(image, (x_pos, y_pos))

    def update_ui(self):
        self.draw_board()
        pygame.display.flip()

    def play_bot_move(self):
        move = self.bot.select_move(self.bot.get_possible_bot_moves(self.board), self)
        if move:
            self.bot.make_move(self, move)

    def is_square_attacked(self, square, color):
        opponent_color = "white" if color == "black" else "black"
        for pos, piece in self.board.items():
            if piece.color == opponent_color:
                if square in piece.get_legal_moves(pos, self.board):
                    return True
        return False

    def is_checkmate(self):
        king_pos = None
        for pos, piece in self.board.items():
            if isinstance(piece, King) and piece.color == self.turn:
                king_pos = pos
                break
        if king_pos is None:
            return True
        if not self.is_square_attacked(king_pos, self.turn):
            return False
        for pos, piece in self.board.items():
            if piece.color == self.turn:
                possible_moves = piece.get_legal_moves(pos, self.board)
                for new_pos in possible_moves:
                    captured = self.board.get(new_pos)
                    del self.board[pos]
                    self.board[new_pos] = piece
                    temp_king_pos = new_pos if pos == king_pos else king_pos
                    still_in_check = self.is_square_attacked(temp_king_pos, self.turn)
                    del self.board[new_pos]
                    self.board[pos] = piece
                    if captured:
                        self.board[new_pos] = captured
                    if not still_in_check:
                        return False
        return True

    def is_occupied(self, square):
        return square in self.board

def play_game():
    pygame.init()
    game = Game.build_game()
    running = True
    selected_square = None
    while running and not game.is_checkmate():
        game.update_ui()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                row = mouse_y // game.square_size
                col = mouse_x // game.square_size
                clicked_square = (row, col)
                if game.turn == "white":
                    if selected_square is None:
                        piece = game.board.get(clicked_square)
                        if piece and piece.color == "white":
                            selected_square = clicked_square
                    else:
                        from_sq = selected_square
                        to_sq = clicked_square
                        success = game.move_piece(from_sq, to_sq)
                        if success:
                            selected_square = None
                            game.turn = "black"
                            game.play_bot_move()
                            game.turn = "white"
                        else:
                            selected_square = None
    if game.is_checkmate():
        print("Checkmate detected!")
    pygame.quit()

if __name__ == "__main__":
    play_game()




