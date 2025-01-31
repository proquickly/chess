import os
import pprint
import functools
import time
import multiprocessing
import random
import pygame

pp = pprint.pprint


def timer(func):
    """Decorator to measure the execution time of a function."""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"Ran {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer


# -------------------------------------------------------------------------
#                            PIECE CLASSES
# -------------------------------------------------------------------------

class Piece:
    """Base chess Piece class with helper movement methods."""
    def __init__(self, color):
        self.color = color


    def can_move_along_row(start_row, start_col, end_row, end_col, board):
        """Checks if a move is along a row."""
        return start_row == end_row

    def can_move_along_col(self, start_row, start_col, end_row, end_col, board):
        """Checks if a move is along a column."""
        return start_col == end_col

    def can_move_along_diagonal(self, start_row, start_col, end_row, end_col, board):
        """Checks if a move is along a diagonal."""
        return abs(start_row - end_row) == abs(start_col - end_col)

    def get_legal_moves(self, position, board):
        """Return all legal moves for this piece. Subclasses must override."""
        raise NotImplementedError("Subclasses should implement get_legal_moves.")


class Pawn(Piece):
    """Pawn piece implementation."""

    def __init__(self, color):
        super().__init__(color)

    def is_valid_move(self, start_row, start_col, end_row, end_col, board):
        """
        Check if a given move is valid for a Pawn (ignoring check/checkmate rules).
        Currently unused in final logic but provided as an example.
        """
        moving_piece = board[start_row][start_col]
        if moving_piece is None:
            return False

        destination_piece = board[end_row][end_col]
        moving_piece_color = moving_piece[0] if moving_piece else None
        if destination_piece is not None:
            destination_piece_color = destination_piece[0]
            # Cannot capture your own piece
            if moving_piece_color == destination_piece_color:
                return False

        direction = -1 if self.color == 'w' else 1  # White up, black down if row=0 is top

        # Normal forward move
        if start_col == end_col and board[end_row][end_col] is None:
            if (end_row - start_row) == direction:
                return True
            # Double move from starting rank
            if start_row == (6 if self.color == 'w' else 1):
                if (end_row - start_row) == 2 * direction and board[start_row + direction][start_col] is None:
                    return True

        # Capture moves
        if abs(start_col - end_col) == 1 and (end_row - start_row) == direction:
            if board[end_row][end_col] is not None and board[end_row][end_col][0] != self.color:
                return True

        return False

    def get_legal_moves(self, position, board):
        """
        Return all possible legal moves (row, col) for this Pawn from `position`,
        given a dict-based board: {(row, col): pieceObject, ...}.
        White Pawns move "down" the board if row=0 is top (direction +1).
        Black Pawns move "up" the board if row=7 is bottom (direction -1).
        """
        moves = []
        x, y = position

        if self.color == 'white':
            # Move forward 1
            if x + 1 <= 7 and board.get((x + 1, y)) is None:
                moves.append((x + 1, y))
                # Initial double move
                if x == 1 and board.get((x + 2, y)) is None:
                    moves.append((x + 2, y))

            # Captures (diagonally forward)
            for dy in [-1, 1]:
                nx, ny = x + 1, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    target = board.get((nx, ny))
                    if target and target.color != self.color:
                        moves.append((nx, ny))

        else:  # black
            # Move forward 1
            if x - 1 >= 0 and board.get((x - 1, y)) is None:
                moves.append((x - 1, y))
                # Initial double move
                if x == 6 and board.get((x - 2, y)) is None:
                    moves.append((x - 2, y))

            # Captures (diagonally forward)
            for dy in [-1, 1]:
                nx, ny = x - 1, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    target = board.get((nx, ny))
                    if target and target.color != self.color:
                        moves.append((nx, ny))

        return moves


class King(Piece):
    """King piece implementation."""

    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def get_legal_moves(self, position, board):
        """
        Return all possible legal moves for this King, including castling if possible.
        """
        moves = []
        x, y = position

        # Normal king moves (one square in any direction)
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

        # Castling checks
        if not self.has_moved:
            if self._can_castle_kingside(position, board):
                moves.append((x, y + 2))
            if self._can_castle_queenside(position, board):
                moves.append((x, y - 2))

        return moves

    def _can_castle_kingside(self, position, board):
        x, y = position
        # Rook is at (x, 7)
        rook = board.get((x, 7))
        if not isinstance(rook, Rook) or rook.has_moved:
            return False
        # Squares between y+1..6 must be empty
        for col in range(y + 1, 7):
            if board.get((x, col)) is not None:
                return False
        # Check path safety
        return self._is_path_safe_for_castling((x, y), (x, 7), board)

    def _can_castle_queenside(self, position, board):
        x, y = position
        # Rook is at (x, 0)
        rook = board.get((x, 0))
        if not isinstance(rook, Rook) or rook.has_moved:
            return False
        # Squares between 1..(y-1) must be empty
        for col in range(1, y):
            if board.get((x, col)) is not None:
                return False
        # Check path safety
        return self._is_path_safe_for_castling((x, y), (x, 0), board)

    def _is_path_safe_for_castling(self, from_position, to_position, board):
        """
        Ensure the King does not pass through or end on attacked squares.
        """
        x, y = from_position
        step = 1 if y < to_position[1] else -1
        for col in range(y, to_position[1] + step, step):
            if self._is_square_attacked((x, col), board):
                return False
        return True

    def _is_square_attacked(self, position, board):
        """Check if `position` is attacked by any opponent piece."""
        for piece_pos, piece in board.items():
            if piece.color != self.color:
                if position in piece.get_legal_moves(piece_pos, board):
                    return True
        return False


class Queen(Piece):
    """Queen piece (Rook + Bishop movement)."""

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


class Knight(Piece):
    """Knight piece implementation."""

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


class Rook(Piece):
    """Rook piece implementation."""

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


class Bishop(Piece):
    """Bishop piece implementation."""

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


# -------------------------------------------------------------------------
#                             PLAYER CLASSES
# -------------------------------------------------------------------------

class Player:
    """Generic Player class."""

    def __init__(self):
        self.is_my_turn = None

    def move(self, piece_from_position, piece_to_position):
        """Placeholder for future expansions."""
        pass


def get_piece_value(piece):
    """
    Quick evaluation heuristic:
    Pawn=1, Knight=3, Bishop=3, Rook=5, Queen=9, King=1000
    """
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
    """
    Example Bot class that selects a move by:
      1. Looking for the highest-value capture.
      2. Otherwise picking a random move.
    """

    def __init__(self, color):
        super().__init__()
        self.color = color

    def get_possible_bot_moves(self, board):
        """
        Return all possible moves [(start_pos, end_pos), ...] for this Bot's color.
        Uses multiprocessing to gather legal moves in parallel.
        """
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
        """Worker process to get all legal moves for the piece at `position`."""
        piece = board[position]
        if piece:
            legal_moves = piece.get_legal_moves(position, board)
            for move in legal_moves:
                possible_moves.append((position, move))

    def select_move(self, moves, game):
        """
        From the list of possible moves, pick the one that captures the
        most valuable piece. If no captures are available, pick randomly.
        """
        best_move = None
        highest_capture_value = 0

        for (start_pos, end_pos) in moves:
            target_piece = game.board.get(end_pos)
            if target_piece and target_piece.color != self.color:
                # Evaluate the capture
                target_value = get_piece_value(target_piece)
                if target_value > highest_capture_value:
                    highest_capture_value = target_value
                    best_move = (start_pos, end_pos)

        if not best_move and moves:
            best_move = random.choice(moves)

        return best_move

    def make_move(self, game, move):
        """Execute the chosen move on the `game` board."""
        if not move:
            return
        start_pos, end_pos = move
        piece = game.board.get(start_pos)
        if piece:
            game.board[start_pos] = None
            game.board[end_pos] = piece
            game.move_piece(start_pos, end_pos)

    def play_turn(self, game):
        """Perform this Bot's turn."""
        possible_moves = self.get_possible_bot_moves(game.board)
        selected_move = self.select_move(possible_moves, game)
        self.make_move(game, selected_move)


# -------------------------------------------------------------------------
#                                GAME CLASS
# -------------------------------------------------------------------------

class Game:
    """Main Game class to store board, pieces, and handle moves/drawing."""

    @classmethod
    def build_game(cls):
        """
        Create a Game object with an 8x8 board, place pieces for both sides,
        initialize PyGame screen, etc.
        """
        square_size = 60
        width, height = square_size * 8, square_size * 8
        screen = pygame.display.set_mode((width, height))

        # Initialize a dictionary-based board
        board = {}

        # -------------------------
        # Place White pieces (row=0) & White pawns (row=1)
        # R  N  B  Q  K  B  N  R
        board[(0, 0)] = Rook("white")
        board[(0, 1)] = Knight("white")
        board[(0, 2)] = Bishop("white")
        board[(0, 3)] = Queen("white")
        board[(0, 4)] = King("white")
        board[(0, 5)] = Bishop("white")
        board[(0, 6)] = Knight("white")
        board[(0, 7)] = Rook("white")

        for col in range(8):
            board[(1, col)] = Pawn("white")

        # -------------------------
        # Place Black pieces (row=7) & Black pawns (row=6)
        board[(7, 0)] = Rook("black")
        board[(7, 1)] = Knight("black")
        board[(7, 2)] = Bishop("black")
        board[(7, 3)] = Queen("black")
        board[(7, 4)] = King("black")
        board[(7, 5)] = Bishop("black")
        board[(7, 6)] = Knight("black")
        board[(7, 7)] = Rook("black")

        for col in range(8):
            board[(6, col)] = Pawn("black")

        bot = Bot("black")
        return cls(board, square_size, screen, bot)

    def __init__(self, board, square_size, screen, bot):
        self.board = board
        self.square_size = square_size
        self.screen = screen
        self.bot = bot
        self.turn = "white"  # White moves first

        # Map from piece objects to piece codes for loading images
        self.display_pieces = {}
        # Example piece code mapping to filenames in ../images/:
        self.piece_filenames = {
            "bK": "bK.png", "bQ": "bQ.png", "bR": "bR.png",
            "bB": "bB.png", "bN": "bN.png", "bp": "bp.png",
            "wK": "wK.png", "wQ": "wQ.png", "wR": "wR.png",
            "wB": "wB.png", "wN": "wN.png", "wp": "wp.png",
        }

        # Load piece images
        self.piece_images = {}
        for code, fname in self.piece_filenames.items():
            path = os.path.join("..", "images", fname)
            img = pygame.image.load(path)
            # Scale to square size
            img = pygame.transform.smoothscale(img, (self.square_size, self.square_size))
            self.piece_images[code] = img

        # Assign codes to each piece object
        for pos, piece in self.board.items():
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
                # White
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
        """Perform a move if it is legal."""
        piece = self.board.get(from_square)
        if piece:
            legal_moves = piece.get_legal_moves(from_square, self.board)
            if to_square in legal_moves:
                self.board[to_square] = piece
                del self.board[from_square]
                return True
        return False

    def draw_board(self):
        """
        Draw an 8x8 board of alternating colors,
        then blit each piece image on its square.
        """
        # Light/dark square colors
        colors = [(233, 236, 239), (125, 135, 150)]

        # Draw squares
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                rect = pygame.Rect(col * self.square_size,
                                   row * self.square_size,
                                   self.square_size,
                                   self.square_size)
                pygame.draw.rect(self.screen, color, rect)

        # Draw pieces
        for (r, c), piece in self.board.items():
            code = self.display_pieces.get(piece, None)
            if code:
                image = self.piece_images.get(code, None)
                if image:
                    x_pos = c * self.square_size
                    y_pos = r * self.square_size
                    self.screen.blit(image, (x_pos, y_pos))

    def update_ui(self):
        """Refresh the entire board and display."""
        self.draw_board()
        pygame.display.flip()

    def play_bot_move(self):
        """Have the bot select and make a move."""
        move = self.bot.select_move(self.bot.get_possible_bot_moves(self.board), self)
        if move:
            self.bot.make_move(self, move)

    def is_square_attacked(self, square, color):
        """
        Return True if 'square' is attacked by the opponent of 'color'.
        That is, any piece of the opposite color can move to 'square'.
        """
        opponent_color = "white" if color == "black" else "black"
        for pos, piece in self.board.items():
            if piece.color == opponent_color:
                if square in piece.get_legal_moves(pos, self.board):
                    return True
        return False

    def is_checkmate(self):
        """
        Simple checkmate logic (not fully robust):
        1. Find the current side's king.
        2. If king not in check, not checkmate.
        3. If no move can get out of check, checkmate.
        """
        king_pos = None
        for pos, piece in self.board.items():
            if isinstance(piece, King) and piece.color == self.turn:
                king_pos = pos
                break

        if king_pos is None:
            return True  # No king found => treat as checkmate or special condition

        # Is king in check?
        if not self.is_square_attacked(king_pos, self.turn):
            return False

        # Try to find a move that would evade check
        for pos, piece in self.board.items():
            if piece.color == self.turn:
                possible_moves = piece.get_legal_moves(pos, self.board)
                for new_pos in possible_moves:
                    captured = self.board.get(new_pos)
                    self.board[new_pos] = piece
                    del self.board[pos]

                    # If the king was moved, track new position
                    temp_king_pos = new_pos if pos == king_pos else king_pos
                    still_in_check = self.is_square_attacked(temp_king_pos, self.turn)

                    # Revert
                    self.board[pos] = piece
                    if captured:
                        self.board[new_pos] = captured
                    else:
                        del self.board[new_pos]

                    if not still_in_check:
                        return False

        return True

    def is_occupied(self, square):
        """Check if a given square is occupied."""
        return square in self.board


# -------------------------------------------------------------------------
#                           MAIN LOOP FUNCTION
# -------------------------------------------------------------------------

def play_game():
    """Main game loop using PyGame events."""
    pygame.init()
    game = Game.build_game()
    running = True
    bot_turn = False

    while running and not game.is_checkmate():
        game.update_ui()  # Redraw board each iteration

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # For example, handle user moves or piece selection
                pass

        if bot_turn:
            game.play_bot_move()
            # Switch turn to White
            game.turn = "white"
            bot_turn = False
        else:
            # Wait or handle the player's move
            # If the player makes a move, switch turn to black, e.g.:
            # game.turn = "black"
            pass

        # (Optional) Decide how to toggle `bot_turn` or handle player moves.
        # For now, let's just always let the bot move so you can see it run:
        bot_turn = True

    if game.is_checkmate():
        print("Checkmate detected!")

    pygame.quit()


if __name__ == "__main__":
    play_game()
