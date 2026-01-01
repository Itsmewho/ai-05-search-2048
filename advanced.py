import random
import math
import copy


# Import the game engine
from intermediate import Game2048, SIZE


# --- Heuristics (How the AI knows a board is "Good") ---
def get_heuristic_score(board):
    """
    Returns a score representing how 'good' the board state is.
    """
    score = 0

    # 1. Empty Tiles (Survival is priority #1)
    empty_count = sum(row.count(0) for row in board)
    score += empty_count * 200

    # 2. Max Tile in Corner (Crucial for 2048+)
    max_tile = max(max(row) for row in board)
    if board[0][0] == max_tile:
        score += 2000  # Massive bonus for keeping the king in the corner

    # 3. Monotonicity (Snake Pattern)
    # We want the top row to be sorted: [128, 64, 32, 16]
    # This makes merging easy.
    if board[0][0] >= board[0][1] >= board[0][2] >= board[0][3]:
        score += 500

    # 4. Smoothness (Neighbors should be close in value)
    # Penalize large differences between neighbors (e.g., 1024 next to 2 is bad)
    penalty = 0
    for r in range(SIZE):
        for c in range(SIZE):
            if c < SIZE - 1:
                val = board[r][c]
                neighbor = board[r][c + 1]
                if val > 0 and neighbor > 0:
                    penalty -= abs(val - neighbor)
            if r < SIZE - 1:
                val = board[r][c]
                neighbor = board[r + 1][c]
                if val > 0 and neighbor > 0:
                    penalty -= abs(val - neighbor)

    return score + penalty


# --- THE BRAIN: EXPECTIMAX ---


def expectimax(game_state, depth, is_player_turn):
    # Base Case: Stop if depth reached or game over
    if depth == 0 or game_state.game_over:
        return get_heuristic_score(game_state.board)

    if is_player_turn:
        # MAX NODE: AI chooses the best move
        best_score = -math.inf
        possible_moves = ["w", "a", "s", "d"]

        for move in possible_moves:
            virtual_game = copy.deepcopy(game_state)
            if virtual_game.move(move):
                # After AI moves, it becomes the Game's turn (Chance)
                score = expectimax(virtual_game, depth - 1, False)
                best_score = max(best_score, score)

        if best_score == -math.inf:
            return -10000
        return best_score

    else:
        # CHANCE NODE: The Game spawns a tile
        # We calculate the WEIGHTED AVERAGE of outcomes
        empty_cells = [
            (r, c)
            for r in range(SIZE)
            for c in range(SIZE)
            if game_state.board[r][c] == 0
        ]

        if not empty_cells:
            return get_heuristic_score(game_state.board)

        # Optimization: Only check a few random spots to keep it fast
        num_checks = min(len(empty_cells), 4)
        cells_to_check = random.sample(empty_cells, num_checks)

        total_score = 0

        for r, c in cells_to_check:
            # Scenario 1: Spawns a 2 (90% likely)
            v_game_2 = copy.deepcopy(game_state)
            v_game_2.board[r][c] = 2
            score_2 = expectimax(v_game_2, depth - 1, True)

            # Scenario 2: Spawns a 4 (10% likely)
            v_game_4 = copy.deepcopy(game_state)
            v_game_4.board[r][c] = 4
            score_4 = expectimax(v_game_4, depth - 1, True)

            total_score += (0.9 * score_2) + (0.1 * score_4)

        return total_score / num_checks


def get_best_move(real_game):
    best_score = -math.inf
    best_move = None
    moves = ["w", "a", "s", "d"]

    # Depth 2 is fast. Depth 3 is smarter but slower.
    SEARCH_DEPTH = 3

    for move in moves:
        virtual_game = copy.deepcopy(real_game)
        if virtual_game.move(move):
            score = expectimax(virtual_game, SEARCH_DEPTH, False)
            if score > best_score:
                best_score = score
                best_move = move

    return best_move


# --- Loop ---
if __name__ == "__main__":
    game = Game2048()

    while not game.game_over:
        game.display()
        print("\nAI is Thinking...")

        move = get_best_move(game)

        if move:
            game.move(move)
        else:
            print("No valid moves!")
            break

    game.display()
    print("AI Finished!")
