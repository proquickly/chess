"""pip install chess
and make sure to rename your program chess to chess_p before running this"""
import pygame
import chess
import chess.svg


class Piece:
    def __init__(self, color):
        self.color = color

    def is_valid_move(self):
        pass


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)

    def is_valid_move(start_row, start_col, end_row, end_col, board):
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


class King(Piece):
    def __init__(self, color):
        super().__init__(color)

    def is_valid_move(start_row, start_col, end_row, end_col, board):
        moving_piece = board[start_row][start_col]
        destination_piece = board[end_row][end_col]
        if moving_piece is None:
            return False
        moving_piece_color = moving_piece[0]
        if destination_piece is not None:
            destination_piece_color = destination_piece[0]
            if moving_piece_color == destination_piece_color:
                return False
        return abs(start_row - end_row) <= 1 and abs(start_col - end_col) <= 1

    # encapsulation
    def _can_castle(self, king_side, color, board, king_moved, rook_moved):
        if king_moved[color]:
            return False
        rook_position = (7 if king_side else 0)
        rook_key = 'right' if king_side else 'left'
        if rook_moved[color][rook_key]:
            return False
        start, end = (4, rook_position) if rook_position > 4 else (
        rook_position, 4)
        for col in range(start + 1, end):
            if board[7 if color == 'w' else 0][col] is not None:
                return False
        return True

    def is_in_check(self):
        pass

    def castle(self):
        if self._can_castle():
            pass
        # etc


class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)

    def is_valid_queen_move(start_row, start_col, end_row, end_col, board):
        moving_piece = board[start_row][start_col]
        destination_piece = board[end_row][end_col]
        if moving_piece is None:
            return False
        moving_piece_color = moving_piece[0]
        if destination_piece is not None:
            destination_piece_color = destination_piece[0]
            if moving_piece_color == destination_piece_color:
                return False
        return (is_valid_rook_move(
            start_row,
            start_col,
            end_row,
            end_col,
            board) or
                is_valid_bishop_move(
                    start_row,
                    start_col,
                    end_row,
                    end_col,
                    board)
                )


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)

    def is_valid_knight_move(start_row, start_col, end_row, end_col, board):
        moving_piece = board[start_row][start_col]
        destination_piece = board[end_row][end_col]
        if moving_piece is None:
            return False
        moving_piece_color = moving_piece[0]
        if destination_piece is not None:
            destination_piece_color = destination_piece[0]
            if moving_piece_color == destination_piece_color:
                return False
        return (abs(start_row - end_row) == 2 and abs(
            start_col - end_col) == 1) or (
                    abs(start_row - end_row) == 1 and abs(
                start_col - end_col) == 2)


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)

    def is_valid_rook_move(start_row, start_col, end_row, end_col, board):
        moving_piece = board[start_row][start_col]
        destination_piece = board[end_row][end_col]
        if moving_piece is None:
            return False
        moving_piece_color = moving_piece[0]
        if destination_piece is not None:
            destination_piece_color = destination_piece[0]
            if moving_piece_color == destination_piece_color:
                return False
        if start_row == end_row:
            step = 1 if start_col < end_col else -1
            for col in range(start_col + step, end_col, step):
                if board[start_row][col] is not None:
                    return False
            return True
        elif start_col == end_col:
            step = 1 if start_row < end_row else -1
            for row in range(start_row + step, end_row, step):
                if board[row][start_col] is not None:
                    return False
            return True
        return False


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)

    def is_valid_bishop_move(start_row, start_col, end_row, end_col, board):
        moving_piece = board[start_row][start_col]
        destination_piece = board[end_row][end_col]
        if moving_piece is None:
            return False
        moving_piece_color = moving_piece[0]
        if destination_piece is not None:
            destination_piece_color = destination_piece[0]
            if moving_piece_color == destination_piece_color:
                return False
        if abs(start_row - end_row) != abs(start_col - end_col):
            return False
        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1
        row, col = start_row + row_step, start_col + col_step
        while row != end_row and col != end_col:
            if board[row][col] is not None:
                return False
            row += row_step
            col += col_step
        return True


class Player:
    def __init__(self):
        is_my_turn = None

    def move(self, piece_from_position, piece_to_position):
        pass


class Bot(Player):
    def __init__(self):
        pass

    def _find_moveable_piece(self):
        return

    def _attempt_move(self, piece):
        return

    def _update_board(self):
        return

    def move(self):
        piece = self._find_moveable_piece()
        success = self._attempt_move(piece)
        if success:
            self._update_board()


class Game(chess.Board):
    @classmethod
    def build_game(cls):
        square_size = 60
        width, height = square_size * 8, square_size * 8
        screen = pygame.display.set_mode((width, height))
        colors = [(233, 236, 239), (125, 135, 150)]
        for r in range(8):
            for c in range(8):
                color = colors[((r + c) % 2)]
                pygame.draw.rect(
                    screen,
                    color,
                    pygame.Rect(
                        c * square_size,
                        r * square_size,
                        square_size, square_size))
        bot = Bot()
        player = Player()
        board = {}
        white, black = "white", "black"
        board[("a", "1")] = Rook(white)
        board[("b", "1")] = Knight(white)
        board[("c", "1")] = Bishop(white)
        board[("d", "1")] = Queen(white)
        board[("e", "1")] = King(white)
        board[("f", "1")] = Bishop(white)
        board[("g", "1")] = Kinght(white)
        board[("h", "1")] = Rook(white)
        for column in ("a", "b", "c", "d", "e", "f", "g", "h"):
            board[(column, 2)] = Pawn(white)
            board[(column, 7)] = Pawn(black)
        board[("a", "8")] = Rook(black)
        board[("b", "8")] = Knight(black)
        board[("c", "8")] = Bishop(black)
        board[("d", "8")] = Queen(black)
        board[("e", "8")] = King(black)
        board[("f", "8")] = Bishop(black)
        board[("g", "8")] = Kinght(black)
        board[("h", "8")] = Rook(black)
        return cls(board, square_size, square_size, player, bot)

    def __init__(self, board, square_size, screen, player, bot):
        super().__init__()
        self.square_size = square_size
        self.screen = screen
        self.player = player
        self.bot = bot
        self.board = board
        self.is_human_turn = False

    def is_checkmate(self):
        pass


def play_game():
    board = Game.build_game()
    board.is_human_turn = not board.is_human_turn
    while not board.is_checkmate():
        # the code in here deals with the screen.
        # it contains no chess logic
        # chess logic comes from the Game class
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass
            # etc
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    play_game()
