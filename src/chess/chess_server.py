"""pip install chess
and make sure to rename your program chess to chess_p before running this"""
import pygame
import chess
import chess.svg
import pprint
from loguru import logger
import pysnooper

print = pprint.pprint
import functools
import multiprocessing
import time
import multiprocessing
import random
import pysnooper
import chess_p


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

    def can_move_along_row(self, start_row, start_col, end_row, end_col,
                           board):
        return start_row == end_row

    def can_move_along_col(self, start_row, start_col, end_row, end_col,
                           board):
        return start_col == end_col

    def can_move_along_diagonal(self, start_row, start_col, end_row, end_col,
                                board):
        return abs(start_row - end_row) == abs(start_col - end_col)

    def get_legal_moves(self, position, board):
        pass
    #FIXME: make for the king


class Pawn(Piece):
    def __init__(self, color):
        self.color = color

    def is_valid_move(self, start_row, start_col, end_row, end_col, board):
        moving_piece = board[start_row][start_col]
        destination_piece = board[end_row][end_col]
        if moving_piece is None:
            return False
        moving_piece_color = moving_piece[0]
        if destination_piece is not None:
            destination_piece_color = destination_piece[0]
            if moving_piece_color == destination_piece_color:
                return False
        direction = -1 if self.color == 'w' else 1
        if start_col == end_col and board[end_row][end_col] is None:
            if (end_row - start_row) == direction:
                return True
            if start_row == (6 if self.color == 'w' else 1) and (
                    end_row - start_row) == 2 * direction and \
                    board[start_row + direction][start_col] is None:
                return True
        elif abs(start_col - end_col) == 1 and (
                end_row - start_row) == direction and board[end_row][
            end_col] is not None and board[end_row][end_col][0] != self.color:
            return True
        return False

    def get_legal_moves(self, position, board):
        moves = []
        x, y = position

        if self.color == 'white':
            # Move forward
            if x + 1 <= 7 and board.get((x + 1, y)) is None:
                moves.append((x + 1, y))
                # Check for the initial double move
                if x == 1 and board.get((x + 2, y)) is None:
                    moves.append((x + 2, y))
            # Captures
            for dx in [-1, 1]:
                if 0 <= y + dx <= 7 and board.get(
                        (x + 1, y + dx)) and board.get(
                        (x + 1, y + dx)).color != self.color:
                    moves.append((x + 1, y + dx))
        elif self.color == 'black':
            # Move forward
            if x - 1 >= 0 and board.get((x - 1, y)) is None:
                moves.append((x - 1, y))
                # Check for the initial double move
                if x == 6 and board.get((x - 2, y)) is None:
                    moves.append((x - 2, y))
            # Captures
            for dx in [-1, 1]:
                if 0 <= y + dx <= 7 and board.get(
                        (x - 1, y + dx)) and board.get(
                        (x - 1, y + dx)).color != self.color:
                    moves.append((x - 1, y + dx))

        return moves


class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.has_moved = False

    def get_legal_moves(self, position, board):
        moves = []
        x, y = position
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1),
                      (1, 0), (1, 1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                if board.get((nx, ny)) is None or board.get(
                        (nx, ny)).color != self.color:
                    moves.append((nx, ny))

        if not self.has_moved:
            if self._can_castle_kingside(position, board):
                moves.append((x, y + 2))
                print(f"Adding kingside castling move {(x, y + 2)}")
            if self._can_castle_queenside(position, board):
                moves.append((x, y - 2))
                print(f"Adding queenside castling move {(x, y - 2)}")

        print(f"King at {position} legal moves: {moves}")
        return moves

    def _can_castle_kingside(self, position, board):
        x, y = position
        rook = board.get((x, 7))
        print(
            f"Checking kingside castling for King at {position}, Rook at {(x, 7)}: {rook}")
        if isinstance(rook, Rook) and not rook.has_moved:
            if all(board.get((x, col)) is None for col in range(y + 1, 7)):
                if self._is_path_safe_for_castling((x, y), (x, 7), board):
                    print(
                        f"Kingside castling is possible for King at {position}")
                    return True
        return False

    def _can_castle_queenside(self, position, board):
        x, y = position
        rook = board.get((x, 0))
        print(
            f"Checking queenside castling for King at {position}, Rook at {(x, 0)}: {rook}")
        if isinstance(rook, Rook) and not rook.has_moved:
            if all(board.get((x, col)) is None for col in range(1, y)):
                if self._is_path_safe_for_castling((x, y), (x, 0), board):
                    print(
                        
                        f"Queenside castling is possible for King at {position}")
                    return True
        return False

    def _is_path_safe_for_castling(self, from_position, to_position, board):
        x, y = from_position
        step = 1 if y < to_position[1] else -1

        for col in range(y + step, to_position[1], step):
            if self._is_square_attacked((x, col), board):
                print(
                    f"Square {(x, col)} is under attack, castling not possible")
                return False
        return True

    def _is_square_attacked(self, position, board):
        for piece_position, piece in board.items():
            if piece.color != self.color:
                if position in piece.get_legal_moves(piece_position, board):
                    print(
                        f"Square {position} is attacked by {piece} at {piece_position}")
                    return True
        return False


    def get_legal_moves(self, position, board):#FIXME:
        moves = []
        x, y = position
        if not self.has_moved:
            if self.color == "black":
                # Kingside castling (assuming right side rook is at (x, 7)) + add private functions!!!!
                #"_unknown1() == True" check if it can return true
                if self.check_if_in_the_right_position_kingside() and self._check_if_under_attack():
                    rook = board.get((x, 7))
                    if rook and isinstance(rook, Rook) and not rook.has_moved:
                        moves.append((x, y + 2))
                        print(f"Adding kingside castling move {(x, y + 2)}")

                # Queenside castling (assuming left side rook is at (x, 0))
                if all(board.get((x, col)) is None for col in range(1, y)) and \
                    not any(self._is_square_attacked((x, col), board) for col in range(y - 2, y + 1)):
                    rook = board.get((x, 0))
                    if rook and isinstance(rook, Rook) and not rook.has_moved:
                        moves.append((x, y - 2))
                        print(f"Adding queenside castling move {(x, y - 2)}")
            elif self.color == "white":
                    pass

        return moves




class Queen(Piece):
    def __init__(self, color):
        self.color = color

    def is_valid_move(self, at, to):
        row_start, col_start = at
        row_end, col_end = to

        if not (row_start == row_end or col_start == col_end or
                abs(row_end - row_start) == abs(col_end - col_start)):
            return False

        row_step = (row_end - row_start) // max(abs(row_end - row_start), 1)
        col_step = (col_end - col_start) // max(abs(col_end - col_start), 1)

        current_row, current_col = row_start, col_start
        while (current_row, current_col) != (row_end, col_end):
            current_row += row_step
            current_col += col_step
            if (current_row, current_col) == (row_end, col_end):
                break
            if not self._check_piece_presence((current_row, current_col)):
                return False

        return True

    def _check_piece_presence(self, position):

        row, col = position
        if 0 <= row < 8 and 0 <= col < 8:
            return True
        return False

    def get_legal_moves(self, position, board):
        board_size = 8
        moves = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1),
                      (1, 0), (1, 1)]

        #diognal moves
        for dx, dy in directions:
            x, y = position
            while True:
                x += dx
                y += dy
                if 0 <= x < board_size and 0 <= y < board_size:
                    if board.get((x, y)) is not None:
                        if board.get((x, y)).color != self.color:
                            moves.append((x, y))
                        break

                    moves.append((x, y))
                else:
                    break

                    #horizontal and vertical moves

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                if board.get((nx, ny)) is None:
                    moves.append((nx, ny))
                elif board((nx, ny)).color != self.color:
                    moves.append((nx, ny))
                    break
                else:
                    break
                nx += dx
                ny += dy

        return moves


"""        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                if board.get((nx, ny)) is None:
                    moves.append((nx, ny))
                elif board.get((nx, ny)).color != self.color:
                    moves.append((nx, ny))
                    break
                else:
                    break

                nx += dx
                ny += dy"""


class Knight(Piece):
    def __init__(self, color):
        self.color = color

    def is_valid_move(self, at, to):
        deltas = [(-2, -1), (-2, +1), (+2, -1), (+2, +1), (-1, -2), (-1, +2),
                  (+1, -2), (+1, +2)]
        valid_to_positions = []
        for row, column in deltas:
            row_candidate = at[0] + row
            column_candidate = at[1] + column
            if 0 < row_candidate <= 8 and 0 < column_candidate <= 8:
                valid_to_positions.append((row_candidate, column_candidate))
        return to in valid_to_positions

    def get_legal_moves(self, position, board):
        moves = []
        x, y = position
        steps = [(-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2),
                 (-2, 1)]
        for dx, dy in steps:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                if board.get((nx, ny), None) is None or board[
                    (nx, ny)].color != 'white':
                    moves.append((nx, ny))
        return moves


class Rook(Piece):
    def __init__(self, color):
        self.color = color
        self.has_moved = False

    def _is_destination_empty(self, destination_place):
        return destination_place is None

    def is_valid_move(self, at, to):
        if at[0] != to[0] and at[1] != to[1]:
            return False

        if at[0] == to[0]:
            direction = 1 if to[1] > at[1] else -1
            for x in range(at[1] + direction, to[1], direction):
                if self._check_piece_presence((at[0], x)):
                    return False
        else:
            direction = 1 if to[0] > at[0] else -1
            for x in range(at[0] + direction, to[0], direction):
                if self._check_piece_presence((x, at[1])):
                    return False
        return True

    def get_legal_moves(self, position, board):
        moves = []
        x, y = position
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                if board.get((nx, ny)) is None:
                    moves.append((nx, ny))
                elif board.get(
                        (nx, ny)).color != self.color:  # get was missing
                    moves.append((nx, ny))
                    break
                else:
                    break
                nx += dx
                ny += dy

        return moves

    def _check_piece_presence(self, position, board):
        x, y = position
        return 0 <= x < 8 and 0 <= y < 8 and board[x][y] is not None


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)

    def is_valid_move(self, at, to):
        start_row, start_col = at
        end_row, end_col = to
        if self.can_move_along_diagonal(start_row, start_col, end_row, end_col,
                                        None):
            return self._is_valid_diagonal_move(start_row, start_col, end_row,
                                                end_col, None)
        else:
            return False

    def _is_valid_diagonal_move(self, start_row, start_col, end_row, end_col,
                                board):
        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1

        current_row, current_col = start_row + row_step, start_col + col_step
        while (current_row, current_col) != (end_row, end_col):
            if board is not None and board[current_row][
                current_col] is not None:
                return False
            current_row += row_step
            current_col += col_step

        return True

    def _check_piece_presence(self, position):
        row, col = position
        if 0 <= row < 8 and 0 <= col < 8:
            return True
        return False

    def get_legal_moves(self, position, board):
        board_size = 8
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        moves = []

        for dx, dy in directions:
            x, y = position
            while True:
                x += dx
                y += dy
                if 0 <= x < board_size and 0 <= y < board_size:
                    if board.get((x, y)) is not None:
                        if board.get((x, y)).color != self.color:
                            moves.append((x, y))
                        break

                    moves.append((x, y))
                else:
                    break

        return moves


class Player:
    def __init__(self):
        self.is_my_turn = None

    def move(self, piece_from_position, piece_to_position):
        pass


def get_piece_value(piece):
    values = {'Pawn': 1, 'Knight': 3, 'Bishop': 3, 'Rook': 5, 'Queen': 9,
              'King': 1000}
    return values.get(type(piece).__name__, 0)


class Bot(Player):
    def __init__(self, color):
        self.color = color

    def get_possible_bot_moves(self, board):
        manager = multiprocessing.Manager()
        possible_moves = manager.list()

        processes = []
        for row in range(8):
            for col in range(8):
                piece = board.get((row, col))
                if piece is not None and piece.color == self.color:
                    print(f"Processing piece {piece} at {(row, col)}")
                    process = multiprocessing.Process(
                        target=self.get_legal_moves_worker,
                        args=((row, col), board, possible_moves))
                    processes.append(process)
                    process.start()

        for process in processes:
            process.join()

        print(f"Possible bot moves: {list(possible_moves)}")
        return list(possible_moves)

    def get_legal_moves_worker(self, position, board, possible_moves):
        piece = board[position]
        if piece is not None:
            legal_moves = piece.get_legal_moves(position, board)
            print(
                f"Legal moves for piece {piece} at {position}: {legal_moves}")
            for move in legal_moves:
                possible_moves.append((position, move))

    #@pysnooper.snoop("pysnooper.txt")
    def select_move(self, moves, game):
        best_move = None
        highest_capture_value = 0
        for move in moves:
            start_pos, end_pos = move
            target_piece = game.board.get(end_pos)
            if target_piece and target_piece.color != self.color:
                target_value = get_piece_value(target_piece)
                if target_value > highest_capture_value:
                    highest_capture_value = target_value
                    best_move = move[1]
                    print(f"currently the best move is {best_move}")

        if not best_move:
            best_move = random.choice(moves)
        print(f"selected move {best_move} from game")

        return best_move

    @pysnooper.snoop()
    def make_move(self, game, move):
        start_pos, end_pos = move
        start_piece = game.board[start_pos]
        game.board[start_pos] = None
        game.board[end_pos] = start_piece
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
        colors = [(233, 236, 239), (125, 135, 150)]
        for r in range(8):
            for c in range(8):
                color = colors[((r + c) % 2)]
                pygame.draw.rect(screen, color,
                                 pygame.Rect(c * square_size, r * square_size,
                                             square_size, square_size))
        bot = Bot("black")
        player = Player()
        board = {}
        for row, color in enumerate(("white", "black")):
            if row == 0:
                row = 1
            else:
                row = 8
            board = {**board, **{
                (row, 1): Rook(color),
                (row, 2): Knight(color),
                (row, 3): Bishop(color),
                (row, 4): Queen(color),
                (row, 5): King(color),
                (row, 6): Bishop(color),
                (row, 7): Knight(color),
                (row, 8): Rook(color),

            }}
        for column in range(1, 9):
            board[(2, column)] = Pawn("white")
            board[(7, column)] = Pawn("black")
        return cls(board, square_size, screen, bot)

    def convert_object_to_display(self, piece):
        return self.display_pieces[piece]

    def __init__(self, board, square_size, screen, bot):
        self.square_size = square_size
        self.screen = screen
        self.bot = bot
        self.board = board
        self.turn = "white"
        self.display_pieces = {
            self.board[(8, 1)]: 'bR',
            self.board[(8, 2)]: 'bN',
            self.board[(8, 3)]: 'bB',
            self.board[(8, 4)]: 'bQ',
            self.board[(8, 5)]: 'bK',
            self.board[(8, 6)]: 'bB',
            self.board[(8, 7)]: 'bN',
            self.board[(8, 8)]: 'bR',
            self.board[(7, 1)]: 'bp',
            self.board[(7, 2)]: 'bp',
            self.board[(7, 3)]: 'bp',
            self.board[(7, 4)]: 'bp',
            self.board[(7, 5)]: 'bp',
            self.board[(7, 6)]: 'bp',
            self.board[(7, 7)]: 'bp',
            self.board[(7, 8)]: 'bp',
            self.board[(1, 1)]: 'bR',
            self.board[(1, 2)]: 'bN',
            self.board[(1, 3)]: 'bB',
            self.board[(1, 4)]: 'bQ',
            self.board[(1, 5)]: 'bK',
            self.board[(1, 6)]: 'bB',
            self.board[(1, 7)]: 'bN',
            self.board[(1, 8)]: 'bR',
            self.board[(2, 1)]: 'bp',
            self.board[(2, 2)]: 'bp',
            self.board[(2, 3)]: 'bp',
            self.board[(2, 4)]: 'bp',
            self.board[(2, 5)]: 'bp',
            self.board[(2, 6)]: 'bp',
            self.board[(2, 7)]: 'bp',
            self.board[(2, 8)]: 'bp',
        }

    def move_piece(self, from_square, to_square):
        piece = self.board.get(from_square)
        if piece is not None:
            legal_moves = piece.get_legal_moves(from_square, self.board)
            if to_square in legal_moves:
                self.board[to_square] = piece
                del self.board[from_square]
                return True
        return False

    def play_bot_move(self):
        bot = Bot("black")
        bot_move = bot(self.board)
        if bot_move:
            from_square, to_square = bot_move
            self.move_piece(from_square, to_square)

    def is_checkmate(self):
        pass

    def is_occupied(self, square):
        logger.info(square)
        isoccupied = self.board.get(square, None)
        if isoccupied is not None:
            return True
        return False

    def _ui_to_piece(self, from_square):
        return self.display_pieces[self.board[from_square]]

    def update(self, from_square, to_square, piece):
        piece = self._ui_to_piece(from_square, piece)
        # is move valid?


def play_game():
    board = Game.build_game()

    bot_turn = False
    while not board.is_checkmate():
        # the code in here deals with the screen.
        # it contains no chess logic
        # chess logic comes from the Game class
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass
                # board.update(from_square, to_square, piece)
            # etc
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    chess_p.play_game()
#TODO:make a test for checking the mouse pos and figure out how to convert the xy (pixels) coordinates to squares