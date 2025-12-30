from Neural_Wars import Neural_Wars

import time
from board import GameEngine, Move
from config import *

# ==============================================================================
# TODO: Import your AI agent class here.
# Ensure your file is named [TEAM NAME].py and class is [TEAM NAME] (uppercase).
# Example: from TEAM_EXCALIBUR import TEAM_EXCALIBUR
# ==============================================================================

PIECE_SYMBOLS = {
    'wP': '♟', 'bP': '♙', 'wN': '♞', 'bN': '♘',
    'wB': '♝', 'bB': '♗', 'wK': '♚', 'bK': '♔',
    EMPTY_SQUARE: ' '
}

class PlayerClock:
    """Manages the cumulative 60-second time budget per game[cite: 7]."""
    def __init__(self, white_time, black_time):
        self.white_time = white_time
        self.black_time = black_time

    def get_time_str(self, time_in_seconds):
        minutes = int(time_in_seconds // 60)
        seconds = int(max(0, time_in_seconds % 60))
        return f"{minutes:02d}:{seconds:02d}"

def display_board(engine, clock, white_player, black_player):
    """Displays the 4x8 board and player clocks."""
    print("\n     a   b   c   d")
    print("   ┌───┬───┬───┬───┐")
    for r in range(BOARD_HEIGHT):
        rank = 8 - r
        row_str = f" {rank} │"
        for c in range(BOARD_WIDTH):
            piece = engine.board[r][c]
            symbol = PIECE_SYMBOLS.get(piece, ' ')
            row_str += f" {symbol} │"
        row_str += f" {rank}"
        
        if r == 2:
            row_str += f"   Black ({black_player.__class__.__name__}): {clock.get_time_str(clock.black_time)}"
        if r == 5:
             row_str += f"   White ({white_player.__class__.__name__}): {clock.get_time_str(clock.white_time)}"

        print(row_str)
        if r < BOARD_HEIGHT - 1:
            print("   ├───┼───┼───┼───┤")
    print("   └───┴───┴───┴───┘")
    print("     a   b   c   d")

def run_game(white_player_type, black_player_type, total_time_seconds=60):
    """
    Executes a match between two agents with a 150-turn limit and 
    scoring based on captures, checks, and checkmate[cite: 7].
    """
    white_points, black_points = 0, 0
    white_log, black_log = [], []
    
    engine = GameEngine()
    white_player = white_player_type(engine)
    black_player = black_player_type(engine)
    
    clock = PlayerClock(total_time_seconds, total_time_seconds)
    turn_counter = 0 # Max 150 total turns [cite: 7]

    print("-" * 50)
    print(f"Match: {white_player.__class__.__name__} vs {black_player.__class__.__name__}")
    print("-" * 50)
    
    display_board(engine, clock, white_player, black_player)

    file_map = {0: 'a', 1: 'b', 2: 'c', 3: 'd'}
    rank_map = {i: str(8 - i) for i in range(BOARD_HEIGHT)}

    winner = None
    reason = ""

    while turn_counter < 150:
        game_state = engine.get_game_state()
        if game_state != "ongoing":
            break

        player = white_player if engine.white_to_move else black_player
        color_str = "White" if engine.white_to_move else "Black"
        
        start_time = time.time()
        try:
            move = player.get_best_move()
        except Exception as e:
            print(f"Error from {color_str}: {e}")
            move = None
        
        time_taken = time.time() - start_time

        # Update clocks and check for time violations [cite: 7]
        if engine.white_to_move:
            clock.white_time -= time_taken
            if clock.white_time <= 0:
                winner, reason = "Black", "Time Limit Exceeded"
                break
        else:
            clock.black_time -= time_taken
            if clock.black_time <= 0:
                winner, reason = "White", "Time Limit Exceeded"
                break

        if move:
            # Score Captures: Knight/Bishop (70), Pawn (20) [cite: 7]
            if move.piece_captured != EMPTY_SQUARE:
                pts = abs(PIECE_VALUES.get(move.piece_captured, 0))
                msg = f"Captured {move.piece_captured[1]} (+{pts})"
                if engine.white_to_move:
                    white_points += pts
                    white_log.append(msg)
                else:
                    black_points += pts
                    black_log.append(msg)

            engine.make_move(move)

            # Score Checks: 2 points [cite: 7]
            if engine.is_in_check():
                if not engine.white_to_move: # White just moved and gave check
                    white_points += 2
                    white_log.append("Delivered Check (+2)")
                else:
                    black_points += 2
                    black_log.append("Delivered Check (+2)")
            
            # turn output and board display logic omitted for brevity...
        else:
            # If no move returned, current player loses
            winner = "Black" if engine.white_to_move else "White"
            reason = "No move returned"
            break

        turn_counter += 1

    # Final Scoring Evaluation [cite: 7]
    print("\n" + "="*15, "GAME OVER", "="*15)
    final_state = engine.get_game_state()

    if winner or final_state == "checkmate":
        if not winner: # Natural checkmate
            winner = "Black" if engine.white_to_move else "White"
            reason = "Checkmate"
        
        print(f"Winner: {winner} ({reason})")
        
        # Rule: A loss results in a score of 0 [cite: 7]
        # Rule: Checkmate is 600 points, overriding others [cite: 7]
        if winner == "White":
            white_points = 600 if reason == "Checkmate" else (white_points if white_points > 0 else 1)
            black_points = 0
        else:
            black_points = 600 if reason == "Checkmate" else (black_points if black_points > 0 else 1)
            white_points = 0
    elif final_state == "stalemate" or turn_counter >= 150:
        print("Draw/Stalemate: Scoring based on captures/checks.")

    print(f"\nFinal Points - White: {white_points} | Black: {black_points}")

if __name__ == "__main__":
    run_game(
        white_player_type=Neural_Wars,
        black_player_type=Neural_Wars
    )
