import new_oochesss as new_oochess

def test_create_game():
    g = new_oochess.Game.build_game()
    assert isinstance(g, new_oochess.Game)
    assert g.square_size == 60
    assert isinstance(g.bot, new_oochess.Bot)
    assert isinstance(g.board, dict)
    assert g.turn == "white"

def test_board():
    pass

def test_is_valid_rook():
    rook = new_oochess.Rook('white')
    assert isinstance(rook, new_oochess.Rook)

def test_is_rook_move_valid():
    r = new_oochess.Rook('white')
    at = (1, 1)
    to = (1, 2)
    assert r.is_valid_move(at, to)

def test_is_valid_knight():
    knight = new_oochess.Knight('white')
    assert isinstance(knight, new_oochess.Knight)

def test_is_knight_move_valid():
    n = new_oochess.Knight('white')
    at = (2, 3)
    to = (4, 5)
    assert not n.is_valid_move(at, to)

def test_is_valid_king():
    king = new_oochess.King('white')
    assert isinstance(king, new_oochess.King)

def test_is_king_move_valid():
    k = new_oochess.King('white')
    at = (1, 1)
    to = (2, 1)
    assert k.is_valid_move(at, to)

def test_is_king_diognal_move_valid():
    k = new_oochess.King('white')
    at = (1, 4)
    to = (2, 3)
    assert k.is_valid_move(at, to)

def test_is_valid_queen():
    queen = new_oochess.Queen('white')
    assert isinstance(queen, new_oochess.Queen)

def test_is_queen_move_valid():
    q = new_oochess.Queen('white')
    at = (1, 5)
    to = (4, 8)
    assert q.is_valid_move(at, to)

def test_is_valid_bishop():
    bishop = new_oochess.Bishop('white')
    assert isinstance(bishop, new_oochess.Bishop)

def test_is_bishop_move_valid():
    #TBD fix: doesnt work correctly
    b = new_oochess.Bishop('white')
    at = (1, 1)
    to = (2, 2)
    assert b.is_valid_move(at, to)

def test_is_valid_black_piece():
    piece = new_oochess.Piece('black')
    assert isinstance(piece, new_oochess.Piece)
    assert piece.color == 'black'

def test_is_valid_white_piece():
    piece = new_oochess.Piece('white')
    assert isinstance(piece, new_oochess.Piece)
    assert piece.color == 'white'

