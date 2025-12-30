# Global definitions for pieces and board dimensions
BOARD_WIDTH = 4
BOARD_HEIGHT = 8

# Piece representation using single characters
WHITE_PAWN = 'wP'
BLACK_PAWN = 'bP'
WHITE_KNIGHT = 'wN'
BLACK_KNIGHT = 'bN'
WHITE_BISHOP = 'wB'
BLACK_BISHOP = 'bB'
WHITE_KING = 'wK'
BLACK_KING = 'bK'
EMPTY_SQUARE = '--'

# Piece values for the heuristic evaluation function as per new requirements.

PIECE_VALUES = {
    WHITE_PAWN: 20,
    BLACK_PAWN: -20,
    WHITE_KNIGHT: 70,
    BLACK_KNIGHT: -70,
    WHITE_BISHOP: 70,
    BLACK_BISHOP: -70,
    WHITE_KING: 600,
    BLACK_KING: -600
}

# Piece-Square Tables (PST) for positional evaluation
PAWN_PST = [
    [5, 5, 5, 5],
    [10, 10, 10, 10],
    [20, 20, 20, 20],
    [30, 30, 30, 30],
    [30, 30, 30, 30],
    [20, 20, 20, 20],
    [10, 10, 10, 10],
    [5, 5, 5, 5],
]

KNIGHT_PST = [
    [-5, 0, 0, -5],
    [0, 5, 5, 0],
    [5, 10, 10, 5],
    [0, 10, 10, 0],
    [0, 10, 10, 0],
    [5, 10, 10, 5],
    [0, 5, 5, 0],
    [-5, 0, 0, -5],
]

BISHOP_PST = [
    [-2, -1, -1, -2],
    [-1, 0, 0, -1],
    [-1, 0, 0, -1],
    [-1, 0, 0, -1],
    [-1, 0, 0, -1],
    [-1, 0, 0, -1],
    [-1, 0, 0, -1],
    [-2, -1, -1, -2],
]

KING_PST_LATE_GAME = [
    [-30, -20, -20, -30],
    [-10, -10, 0, 0],
    [20, 20, 20, 20],
    [30, 30, 30, 30],
    [30, 30, 30, 30],
    [20, 20, 20, 20],
    [-10, -10, 0, 0],
    [-30, -20, -20, -30]
]

PIECE_SYMBOLS = {
    'wP': '♙', 'bP': '♟', 'wN': '♘', 'bN': '♞',
    'wB': '♗', 'bB': '♝', 'wK': '♔', 'bK': '♚',
    '--': ' '
}