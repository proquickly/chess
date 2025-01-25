import random


def evaluate_board(board, color):
    value = 0
    for position, piece in board.items():
        multiplier = 1 if piece.color == color else -1
        value += multiplier * piece_value(piece)
    return value


def piece_value(piece):
    return {
        'Pawn': 1, 'Knight': 3, 'Bishop': 3,
        'Rook': 5, 'Queen': 9, 'King': 1000
    }.get(piece.__class__.__name__, 0)


class Bot:
    def __init__(self, color):
        self.color = color

    def select_move(self, moves, game):
        best_move = None
        max_eval = float('-inf')
        for move in moves:
            # Simulate the move
            start, end = move
            target_piece = game.board.get(end)
            game.board[end] = game.board[start]
            game.board[start] = None

            evaluation = evaluate_board(game.board, self.color)
            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move

            # Undo the move
            game.board[start] = game.board[end]
            game.board[end] = target_piece

        return best_move or random.choice(moves)
