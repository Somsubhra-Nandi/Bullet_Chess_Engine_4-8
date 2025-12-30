import time
import random
from config import *
from board import Move

INF = 10**9


class Neural_Wars:
    """
    AI Agent for Prometeo 2026: Neural Wars
    Features: Negamax, Alpha-Beta, Iterative Deepening, Quiescence Search
    """

    def __init__(self, board):
        self.board = board
        self.my_time = 60.0
        self.start_time = None
        self.time_limit = 0.1
        self.best_move = None

    # ======================================================
    # REQUIRED ENTRY POINT
    # ======================================================
    def get_best_move(self):
        self.start_time = time.time()
        self.best_move = None

        legal_moves = self.board.get_legal_moves()
        if not legal_moves:
            return None

        # --- Time budgeting (safe & realistic) ---
        turns_remaining = max(15, 40 - len(self.board.move_log) // 2)
        self.time_limit = self.my_time / turns_remaining
        self.time_limit = min(2.0, max(0.05, self.time_limit))

        # Move ordering: captures first
        legal_moves.sort(
            key=lambda m: abs(PIECE_VALUES.get(m.piece_captured, 0)),
            reverse=True
        )
        random.shuffle(legal_moves[:min(3, len(legal_moves))])

        max_depth = 8
        depth = 1

        while depth <= max_depth:
            try:
                self.search_root(legal_moves, depth)
                depth += 1
            except TimeoutError:
                break

        elapsed = time.time() - self.start_time
        self.my_time -= elapsed
        self.my_time -= 0.02

        return self.best_move or legal_moves[0]

    # ======================================================
    # REQUIRED BY TEMPLATE
    # ======================================================
    def evaluate_board(self):
        return self.evaluate()

    # ======================================================
    # ROOT SEARCH
    # ======================================================
    def search_root(self, moves, depth):
        best_score = -INF
        local_best = None

        for move in moves:
            self.check_time()
            self.board.make_move(move)
            score = -self.negamax(depth - 1, -INF, INF)
            self.board.undo_move()

            if score > best_score:
                best_score = score
                local_best = move

        if local_best:
            self.best_move = local_best

    # ======================================================
    # NEGAMAX + ALPHA-BETA
    # ======================================================
    def negamax(self, depth, alpha, beta):
        self.check_time()

        state = self.board.get_game_state()
        if state == "checkmate":
            return -INF + depth
        if state == "stalemate":
            material = self.material_score()
            return -50 if material > 0 else 0

        if depth == 0:
            return self.quiescence(alpha, beta)

        moves = self.board.get_legal_moves()
        if not moves:
            return self.evaluate()

        moves.sort(
            key=lambda m: abs(PIECE_VALUES.get(m.piece_captured, 0)),
            reverse=True
        )

        value = -INF
        for move in moves:
            self.check_time()
            self.board.make_move(move)
            value = max(value, -self.negamax(depth - 1, -beta, -alpha))
            self.board.undo_move()

            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return value

    # ======================================================
    # QUIESCENCE SEARCH (PROPER)
    # ======================================================
    def quiescence(self, alpha, beta):
        self.check_time()

        # Stand-pat evaluation
        stand_pat = self.evaluate()

        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat

        # Only noisy moves: captures + checks
        moves = self.board.get_legal_moves()
        noisy_moves = [
            m for m in moves
            if m.piece_captured != EMPTY_SQUARE or self.is_check_after_move(m)
        ]

        noisy_moves.sort(
            key=lambda m: abs(PIECE_VALUES.get(m.piece_captured, 0)),
            reverse=True
        )

        for move in noisy_moves:
            self.check_time()
            self.board.make_move(move)
            score = -self.quiescence(-beta, -alpha)
            self.board.undo_move()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha

    # ======================================================
    # EVALUATION FUNCTION
    # ======================================================
    def evaluate(self):
        absolute_score = 0

        for r in range(BOARD_HEIGHT):
            for c in range(BOARD_WIDTH):
                piece = self.board.board[r][c]
                if piece == EMPTY_SQUARE:
                    continue

                absolute_score += PIECE_VALUES[piece]

                if piece[1] == 'P':
                    absolute_score += PAWN_PST[r][c] if piece[0] == 'w' else -PAWN_PST[7 - r][c]
                elif piece[1] == 'N':
                    absolute_score += KNIGHT_PST[r][c] if piece[0] == 'w' else -KNIGHT_PST[7 - r][c]
                elif piece[1] == 'B':
                    absolute_score += BISHOP_PST[r][c] if piece[0] == 'w' else -BISHOP_PST[7 - r][c]
                elif piece[1] == 'K':
                    absolute_score += KING_PST_LATE_GAME[r][c] if piece[0] == 'w' else -KING_PST_LATE_GAME[7 - r][c]

                # Capture safety
                if abs(PIECE_VALUES[piece]) >= 70:
                    absolute_score += 5 if piece[0] == 'w' else -5

        # King pressure
        wk = self.board._find_king('w')
        bk = self.board._find_king('b')
        if wk:
            absolute_score -= self.adjacent_threats(wk, 'w') * 5
        if bk:
            absolute_score += self.adjacent_threats(bk, 'b') * 5

        score = absolute_score if self.board.white_to_move else -absolute_score

        if self.board.is_in_check():
            score -= 15

        if self.board.get_repetition_count() >= 2:
            score -= 30

        return score

    # ======================================================
    # HELPERS
    # ======================================================
    def material_score(self):
        score = 0
        for r in range(BOARD_HEIGHT):
            for c in range(BOARD_WIDTH):
                piece = self.board.board[r][c]
                if piece != EMPTY_SQUARE:
                    score += PIECE_VALUES[piece]
        return score if self.board.white_to_move else -score

    def is_check_after_move(self, move):
        self.board.make_move(move)
        in_check = self.board.is_in_check()
        self.board.undo_move()
        return in_check

    def adjacent_threats(self, square, king_color):
        r, c = square
        count = 0
        for dr, dc in [
            (1,0),(-1,0),(0,1),(0,-1),
            (1,1),(1,-1),(-1,1),(-1,-1)
        ]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < BOARD_HEIGHT and 0 <= nc < BOARD_WIDTH:
                piece = self.board.board[nr][nc]
                if piece != EMPTY_SQUARE and piece[0] != king_color:
                    count += 1
        return count

    def check_time(self):
        if time.time() - self.start_time >= self.time_limit:
            raise TimeoutError
