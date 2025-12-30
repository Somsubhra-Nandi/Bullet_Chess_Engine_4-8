"""
The GameEngine for Chess game.
"""
from config import *

class Move:
    def __init__(self, start_square, end_square, board):
        self.start_row, self.start_col = start_square
        self.end_row, self.end_col = end_square
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.start_row == other.start_row and \
                   self.start_col == other.start_col and \
                   self.end_row == other.end_row and \
                   self.end_col == other.end_col
        return False
    
    def __repr__(self):
        # Helper for debugging tests
        return f"Move({(self.start_row, self.start_col)} -> {(self.end_row, self.end_col)})"

class GameEngine:
    def __init__(self):
        self.board = self.get_initial_board()
        self.white_to_move = True
        self.move_log = []
       #history
        self.position_history = {}
        self.update_position_history()

    def update_position_history(self):
        """Adds the current board state to the history log."""
        board_tuple = tuple(tuple(row) for row in self.board)
        key = (board_tuple, self.white_to_move)
        self.position_history[key] = self.position_history.get(key, 0) + 1
        
    def get_repetition_count(self):
        """Returns how many times the current position has been reached."""
        board_tuple = tuple(tuple(row) for row in self.board)
        key = (board_tuple, self.white_to_move)
        return self.position_history.get(key, 0)

    def get_initial_board(self):
        board = [[EMPTY_SQUARE] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        board[0] = [BLACK_KNIGHT, BLACK_BISHOP, BLACK_KING, BLACK_KNIGHT]
        board[1] = [BLACK_PAWN] * BOARD_WIDTH
        board[6] = [WHITE_PAWN] * BOARD_WIDTH
        board[7] = [WHITE_KNIGHT, WHITE_BISHOP, WHITE_KING, WHITE_KNIGHT]
        return board

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = EMPTY_SQUARE
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        self.update_position_history()

    def undo_move(self):
        if not self.move_log: return
        board_tuple = tuple(tuple(row) for row in self.board)
        key = (board_tuple, self.white_to_move)
        self.position_history[key] -= 1

        move = self.move_log.pop()
        self.board[move.start_row][move.start_col] = move.piece_moved
        self.board[move.end_row][move.end_col] = move.piece_captured
        self.white_to_move = not self.white_to_move

    def get_legal_moves(self):
        possible_moves = self._get_all_possible_moves()
        legal_moves = []
        for move in possible_moves:
            self.make_move(move)
            if not self._is_king_in_check():
                legal_moves.append(move)
            self.undo_move()
        return legal_moves

    def get_game_state(self):
        legal_moves = self.get_legal_moves()
        in_check = self.is_in_check()
        if not legal_moves:
            return "checkmate" if in_check else "stalemate"
        return "ongoing"

    def is_in_check(self):
        """Is the CURRENT player to move in check?"""
        return self._is_king_in_check(check_current_player=True)

    def _is_king_in_check(self, check_current_player=False):
        if check_current_player:
            king_color = 'w' if self.white_to_move else 'b'
        else:
            king_color = 'b' if self.white_to_move else 'w'
        
        king_pos = self._find_king(king_color)
        if king_pos is None: return True
        
        return self._is_square_attacked(king_pos, king_color)

    def _find_king(self, color):
        king_piece = WHITE_KING if color == 'w' else BLACK_KING
        for r, row in enumerate(self.board):
            for c, piece in enumerate(row):
                if piece == king_piece:
                    return (r, c)
        return None

    def _is_square_attacked(self, square, friendly_color):
        return (self._is_attacked_by_pawn(square, friendly_color) or
                self._is_attacked_by_knight(square, friendly_color) or
                self._is_attacked_by_bishop(square, friendly_color) or
                self._is_attacked_by_king(square, friendly_color))

    def _is_attacked_by_pawn(self, square, friendly_color):
        r, c = square
        if friendly_color == 'w':
            if self._is_valid(r - 1, c - 1) and self.board[r-1][c-1] == BLACK_PAWN: return True
            if self._is_valid(r - 1, c + 1) and self.board[r-1][c+1] == BLACK_PAWN: return True
        else:
            if self._is_valid(r + 1, c - 1) and self.board[r+1][c-1] == WHITE_PAWN: return True
            if self._is_valid(r + 1, c + 1) and self.board[r+1][c+1] == WHITE_PAWN: return True
        return False

    def _is_attacked_by_knight(self, square, friendly_color):
        r, c = square
        opponent_knight = BLACK_KNIGHT if friendly_color == 'w' else WHITE_KNIGHT
        for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
            if self._is_valid(r+dr, c+dc) and self.board[r+dr][c+dc] == opponent_knight:
                return True
        return False

    def _is_attacked_by_bishop(self, square, friendly_color):
        r, c = square
        opponent_bishop = BLACK_BISHOP if friendly_color == 'w' else WHITE_BISHOP
        for dr, dc in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            for i in range(1, 8):
                end_r, end_c = r + dr * i, c + dc * i
                if not self._is_valid(end_r, end_c): break
                piece = self.board[end_r][end_c]
                if piece != EMPTY_SQUARE:
                    if piece == opponent_bishop: return True
                    break
        return False

    def _is_attacked_by_king(self, square, friendly_color):
        r, c = square
        opponent_king = BLACK_KING if friendly_color == 'w' else WHITE_KING
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            if self._is_valid(r+dr, c+dc) and self.board[r+dr][c+dc] == opponent_king:
                return True
        return False

    def _get_all_possible_moves(self):
        moves = []
        turn_color = 'w' if self.white_to_move else 'b'
        for r, row in enumerate(self.board):
            for c, piece in enumerate(row):
                if piece.startswith(turn_color):
                    ptype = piece[1]
                    if ptype == 'P': self._get_pawn_moves(r, c, moves)
                    elif ptype == 'N': self._get_knight_moves(r, c, moves)
                    elif ptype == 'B': self._get_bishop_moves(r, c, moves)
                    elif ptype == 'K': self._get_king_moves(r, c, moves)
        return moves

    def _get_pawn_moves(self, r, c, moves):
        direction = -1 if self.white_to_move else 1
        opponent_color = 'b' if self.white_to_move else 'w'
        if self._is_valid(r + direction, c) and self.board[r+direction][c] == EMPTY_SQUARE:
            moves.append(Move((r, c), (r + direction, c), self.board))
        for dc in [-1, 1]:
            if self._is_valid(r+direction,c+dc) and self.board[r+direction][c+dc].startswith(opponent_color):
                moves.append(Move((r, c), (r + direction, c + dc), self.board))

    def _get_knight_moves(self, r, c, moves):
        friendly_color = 'w' if self.white_to_move else 'b'
        for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
            end_r, end_c = r + dr, c + dc
            if self._is_valid(end_r, end_c) and not self.board[end_r][end_c].startswith(friendly_color):
                moves.append(Move((r, c), (end_r, end_c), self.board))

    def _get_bishop_moves(self, r, c, moves):
        friendly_color = 'w' if self.white_to_move else 'b'
        for dr, dc in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            for i in range(1, 8):
                end_r, end_c = r + dr * i, c + dc * i
                if not self._is_valid(end_r, end_c): break
                target = self.board[end_r][end_c]
                if not target.startswith(friendly_color):
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                if target != EMPTY_SQUARE: break

    def _get_king_moves(self, r, c, moves):
        friendly_color = 'w' if self.white_to_move else 'b'
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            end_r, end_c = r + dr, c + dc
            if self._is_valid(end_r, end_c) and not self.board[end_r][end_c].startswith(friendly_color):
                moves.append(Move((r, c), (end_r, end_c), self.board))
    
    def _is_valid(self, r, c):
        return 0 <= r < BOARD_HEIGHT and 0 <= c < BOARD_WIDTH
