import new_oochesss as new_oochess


def test_is_bot_responding():
    bot = new_oochess.Bot('black')
    assert isinstance(bot, new_oochess.Bot)
    #assert bot.move()


def test_can_make_valid_move():
    pass


def test_can_make_valid_move_for_knight():
    game = new_oochess.Game.build_game()
    bot = new_oochess.Bot('white')

    game.board.clear()
    knight_position = (4, 5)  # e4
    game.board[knight_position] = new_oochess.Knight('white')

    expected_moves = [
        (2, 4), (2, 6),
        (3, 3), (3, 7),
        (5, 3), (5, 7),
        (6, 4), (6, 6)
    ]

    all_moves = bot.get_possible_bot_moves(game.board)
    legal_moves = [move for pos, move in all_moves if pos == knight_position]

    assert all(move in legal_moves for move in expected_moves)
    assert all(move in expected_moves for move in legal_moves)


def test_can_make_valid_move_for_rook():
    # Test 1: Rook on an empty board at position d4 (3, 3)
    game = new_oochess.Game.build_game()
    bot = new_oochess.Bot('white')

    game.board.clear()
    rook_position = (3, 3)
    game.board[rook_position] = new_oochess.Rook('white')

    expected_moves_d4 = [
        (3, 0), (3, 1), (3, 2), (3, 4), (3, 5), (3, 6), (3, 7),
        (0, 3), (1, 3), (2, 3), (4, 3), (5, 3), (6, 3), (7, 3)
    ]

    all_moves = bot.get_possible_bot_moves(game.board)
    legal_moves = [move for pos, move in all_moves if pos == rook_position]

    assert all(move in legal_moves for move in expected_moves_d4)
    assert all(move in expected_moves_d4 for move in legal_moves)


def test_can_make_valid_move_for_king():
    game = new_oochess.Game.build_game()
    bot = new_oochess.Bot('white')

    game.board.clear()
    king_position = (3, 4)
    game.board[king_position] = new_oochess.King('white')

    expected_moves_e4 = [
        (2, 3), (2, 4), (2, 5),
        (3, 3), (3, 5),
        (4, 3), (4, 4), (4, 5)
    ]

    all_moves = bot.get_possible_bot_moves(game.board)
    legal_moves = [move for pos, move in all_moves if pos == king_position]

    print("Expected Moves:", sorted(expected_moves_e4))
    print("Legal Moves:", sorted(legal_moves))

    assert all(move in legal_moves for move in expected_moves_e4)
    assert all(move in expected_moves_e4 for move in legal_moves)


def test_can_make_valid_move_for_bishop():
    game = new_oochess.Game.build_game()
    bot = new_oochess.Bot('white')

    game.board.clear()
    king_position = (3, 4)  #4, e row, column
    game.board[king_position] = new_oochess.King('white')

    expected_moves_e4 = [
        (2, 3), (2, 4), (2, 5),
        (3, 3), (3, 5),
        (4, 3), (4, 4), (4, 5)
    ]

    all_moves = bot.get_possible_bot_moves(game.board)
    legal_moves = [move for pos, move in all_moves if pos == king_position]

    print("Expected Moves:", sorted(expected_moves_e4))
    print("Legal Moves:", sorted(legal_moves))

    assert all(move in legal_moves for move in
               expected_moves_e4), "Not all expected moves are legal"
    assert all(move in expected_moves_e4 for move in
               legal_moves), "Not all legal moves are expected"


def test_can_make_valid_move_for_queen():
    game = new_oochess.Game.build_game()
    bot = new_oochess.Bot('white')

    game.board.clear()
    queen_position = (3, 3)
    game.board[queen_position] = new_oochess.Queen('white')

    expected_moves_d4 = [
        # Vertical
        (4, 3), (5, 3), (6, 3), (7, 3),  # Up
        (2, 3), (1, 3), (0, 3),  # Down
        # Horizontal
        (3, 4), (3, 5), (3, 6), (3, 7),  # Right
        (3, 2), (3, 1), (3, 0),  # Left
        # Diagonal
        (4, 4), (5, 5), (6, 6), (7, 7),  # Up-right
        (4, 2), (5, 1), (6, 0),  # Up-left
        (2, 4), (1, 5), (0, 6),  # Down-right
        (2, 2), (1, 1), (0, 0)  # Down-left
    ]

    all_moves = bot.get_possible_bot_moves(game.board)
    legal_moves = [move for pos, move in all_moves if pos == queen_position]

    print("Expected Moves:", sorted(expected_moves_d4))
    print("Legal Moves:", sorted(legal_moves))

    assert all(move in legal_moves for move in
               expected_moves_d4), "Not all expected moves are legal"
    assert all(move in expected_moves_d4 for move in
               legal_moves), "Not all legal moves are expected"


def test_can_make_valid_move_for_pawn():
    game = new_oochess.Game.build_game()
    bot = new_oochess.Bot('white')

    game.board.clear()
    pawn_position = (1, 4)
    game.board[pawn_position] = new_oochess.Pawn('white')

    expected_moves_e2 = [(2, 4), (3, 4)]

    all_moves = bot.get_possible_bot_moves(game.board)
    legal_moves = [move for pos, move in all_moves if pos == pawn_position]

    assert all(move in legal_moves for move in
               expected_moves_e2), "Not all expected moves are in legal moves."
    assert all(move in expected_moves_e2 for move in
               legal_moves), "Legal moves contain unexpected moves."


def test_can_take_for_pawn():
    game = new_oochess.Game.build_game()
    bot = new_oochess.Bot('white')

    game.board.clear()
    pawn_position = (1, 4)
    rook_position = (2, 5)

    game.board[rook_position] = new_oochess.Rook('black')
    game.board[pawn_position] = new_oochess.Pawn('white')

    expected_moves_e2 = [(2, 4), (3, 4), (2, 5)]

    all_moves = bot.get_possible_bot_moves(game.board)
    legal_moves = [move for pos, move in all_moves if pos == pawn_position]

    assert all(move in legal_moves for move in
               expected_moves_e2), "Not all expected moves are in legal moves."
    assert all(move in expected_moves_e2 for move in
               legal_moves), "Legal moves contain unexpected moves."


def test_bot_move_and_takes():
    game = new_oochess.Game.build_game()

    pawn_position = (1, 2)
    queen_position = (1, 1)
    game.board.clear()
    game.board[pawn_position] = new_oochess.Pawn('white')
    game.board[queen_position] = new_oochess.Queen('black')

    bot = new_oochess.Bot('black')
    bot.play_turn(game)  # just game

    assert isinstance(game.board.get(queen_position), new_oochess.Pawn)
    assert game.board[queen_position].color == 'black'

    assert (pawn_position not in game.board) or (game.board[pawn_position] is None)

    assert game.turn == 'white'

    #TODO: why is this ignoring the pawn on the test?
    """Modified var:.. move = ((1, 1), (1, 0))
17:13:49.025128 line       495             start_pos, end_pos = move[0]
17:13:49.025128 line       496             target_piece = game.board.get(end_pos)
17:13:49.025128 line       497             if target_piece and target_piece.color != self.color:
17:13:49.025128 line       494         for move in moves:"""



def test_king_castling():
        game = new_oochess.Game.build_game()
        bot = new_oochess.Bot('white')

        game.board.clear()

        king_position = (0, 4)
        rook_kingside_position = (0, 7)
        rook_queenside_position = (0, 0)

        game.board[king_position] = new_oochess.King('white')
        game.board[rook_kingside_position] = new_oochess.Rook('white')
        game.board[rook_queenside_position] = new_oochess.Rook('white')

        print(f"Board setup: {game.board}")

        expected_moves_castling = [(0, 6), (0, 2)]

        all_moves = bot.get_possible_bot_moves(game.board)
        king_moves = [move for pos, move in all_moves if pos == king_position]

        print(f"Expected castling moves: {expected_moves_castling}")
        print(f"All moves: {all_moves}")
        print(f"King moves: {king_moves}")

        assert all(move in king_moves for move in expected_moves_castling), "Not all castling moves are in king's legal moves."

def make_move_by_itself():
    game = new_oochess.Game.build_game()
    bot = new_oochess.Bot('white')

    game.board.clear()
    pawn_position = (1, 4)

    game.board[pawn_position] = new_oochess.Pawn('white')

    bot.play_turn("white")

    all_moves = bot.get_possible_bot_moves(game.board)
    legal_moves = [move for pos, move in all_moves if pos == pawn_position]

    assert game.board[pawn_position] is None

8.  ########
7.  ########
6.  ########
5.  ########
4.  ########
3.  #####R##
2.  ####P###
1.  ########
#'ABCDEFGH'
