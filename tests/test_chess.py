import chess


def test_create_pawn():
    pawn = chess.Pawn()
    assert isinstance(pawn, chess.Pawn)


def test_pawn_valid_move():
    start_square = ("a", "2")
    end_square = ("a", "3")
    p = chess.Pawn("white")
    assert p.is_valid_move(start_square, end_square)


def test_is_square_occupied():
    b = chess.Board()
    square = ("a", "1")
    assert not b.is_square_empty(square)


def test_is_square_empty():
    b = chess.Board()
    square = ("a", "3")
    assert b.is_square_empty(square)
