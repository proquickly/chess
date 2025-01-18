import new_oochesss
import chess_p


def test_piece_to_board_map():
    g = new_oochesss.Game.build_game()
    assert g.display_pieces[g.board[(8, 1)]] == "bR"


def test_ui_to_piece():
    g = new_oochesss.Game.build_game()
    assert isinstance(g._ui_to_piece((2, 1), "wp"))


def test_screen_to_board():
    print("Testing screen_to_board function:")
    assert chess_p.screen_to_board(0, 0) == (8, 1), f"Failed on (0, 0), got {chess_p.screen_to_board(0, 0)}"
    assert chess_p.screen_to_board(420, 420) == (1, 8), f"Failed on (420, 420), got {chess_p.screen_to_board(420, 420)}"
    #assert chess_p.screen_to_board(210, 210) == (4, 4), f"Failed on (210, 210), got {chess_p.screen_to_board(210, 210)}"
    assert chess_p.screen_to_board(60, 0) == (8, 2), f"Failed on (60, 0), got {chess_p.screen_to_board(60, 0)}"
    assert chess_p.screen_to_board(60, 60) == (7, 2), f"Failed on (60, 60), got {chess_p.screen_to_board(60, 60)}"


def test_board_to_screen():
    assert chess_p.board_to_screen(1, 1) == (420, 0)
    assert chess_p.board_to_screen(8, 8) == (0, 420)


"""
SQUARES
col 1                   col 8
------|---------|-----|---------
0,0   | 0, 60   | ... | 0, 420     -> row 8
60,0  | 60, 60  | ... | 60, 420
120,0 | 120, 60 | ... | 120, 420
180,0 | 180, 60 | ... | 180, 420
240,0 | 240, 60 | ... | 240, 420
300,0 | 300, 60 | ... | 300, 420
360,0 | 360, 60 | ... | 360, 420
420,0 | 420, 60 | ... | 420, 420   -> row 1
"""
