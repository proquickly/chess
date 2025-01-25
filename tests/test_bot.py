import pytest
from chess.bot import Bot, evaluate_board, piece_value


# Mock classes for testing
class Piece:
    def __init__(self, color, name):
        self.color = color
        self.__class__.__name__ = name


class Game:
    def __init__(self, board):
        self.board = board


def test_piece_value():
    assert piece_value(Piece('White', 'Pawn')) == 1
    assert piece_value(Piece('Black', 'Knight')) == 3
    assert piece_value(Piece('White', 'Bishop')) == 3
    assert piece_value(Piece('Black', 'Rook')) == 5
    assert piece_value(Piece('White', 'Queen')) == 9
    assert piece_value(Piece('Black', 'King')) == 1000
    assert piece_value(Piece('White', 'UnknownPiece')) == 0


def test_evaluate_board():
    board = {
        (0, 0): Piece('White', 'Pawn'),
        (0, 1): Piece('Black', 'Rook'),
        (0, 2): Piece('White', 'Queen'),
        (0, 3): Piece('Black', 'King'),
        (0, 4): Piece('White', 'Bishop'),
    }
    assert evaluate_board(board, 'White') == (1 - 5 + 9 - 1000 + 3)
    assert evaluate_board(board, 'Black') == (-1 + 5 - 9 + 1000 - 3)


def test_bot_select_move():
    # Create a simple board scenario
    board = {
        (0, 0): Piece('White', 'Queen'),
        (1, 1): Piece('Black', 'Pawn'),
        (2, 2): None,
    }
    game = Game(board)

    # Define possible moves
    moves = [((0, 0), (1, 1)),
             ((0, 0), (2, 2))]  # Attack or move to an empty square

    # Create bot and find selected move
    bot = Bot('White')
    selected_move = bot.select_move(moves, game)

    # Bot should choose the move that captures the black pawn
    assert selected_move == ((0, 0), (1, 1))
