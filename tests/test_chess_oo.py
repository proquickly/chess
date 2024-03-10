from chess_oo import chess_oo


def test_create_pawn():
    pawn = chess_oo.Pawn("white")
    assert isinstance(pawn, chess_oo.Pawn)


def test_pawn_valid_move():
    start_square = ("a", "2")
    end_square = ("a", "3")
    p = chess_oo.Pawn("white")
    assert p.is_valid_move(start_square, end_square)


def test_is_square_occupied():
    b = chess_oo.Game()
    square = ("a", "1")
    assert not b.is_square_empty(square)


def test_is_square_empty():
    b = chess_oo.Game()
    square = ("a", "3")
    assert b.is_square_empty(square)


def test_king_is_valid_move():
    start_square = ("e", "1")
    end_square = ("e", "2")
    k = chess_oo.King("white")
    assert k.is_valid_move(start_square, end_square)


def test_king_castle():
    pass
