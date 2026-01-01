import random
import os


# ---- Config
SIZE = 4


class Game2048:
    def __init__(self):
        self.board = [[0] * SIZE for _ in range(SIZE)]
        self.score = 0
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self):
        """Adds a 2 (90%) or 4 (10%) to a random empty slot."""
        empty_cells = [
            (r, c) for r in range(SIZE) for c in range(SIZE) if self.board[r][c] == 0
        ]
        if not empty_cells:
            return
        r, c = random.choice(empty_cells)
        self.board[r][c] = 2 if random.random() < 0.9 else 4

    def compress(self, grid):
        """Slides all non-zero numbers to the left, removing zeros."""
        new_grid = [[0] * SIZE for _ in range(SIZE)]
        for r in range(SIZE):
            pos = 0
            for c in range(SIZE):
                if grid[r][c] != 0:
                    new_grid[r][pos] = grid[r][c]
                    pos += 1
        return new_grid

    def merge(self, grid):
        """Combines adjacent equal numbers (Left to Right)."""
        score_gain = 0
        for r in range(SIZE):
            for c in range(SIZE - 1):
                if grid[r][c] != 0 and grid[r][c] == grid[r][c + 1]:
                    grid[r][c] *= 2
                    score_gain += grid[r][c]
                    grid[r][c + 1] = 0
        return grid, score_gain

    def reverse(self, grid):
        """Mirrors the grid (for Right moves)."""
        new_grid = []
        for r in range(SIZE):
            new_grid.append(grid[r][::-1])
        return new_grid

    def transpose(self, grid):
        """Swaps Rows/Cols (for Up/Down moves)."""
        new_grid = [[0] * SIZE for _ in range(SIZE)]
        for r in range(SIZE):
            for c in range(SIZE):
                new_grid[r][c] = grid[c][r]
        return new_grid

    def move(self, direction):
        """
        Executes a move: 'w' (Up), 's' (Down), 'a' (Left), 'd' (Right).
        Returns True if the board changed (valid move).
        """
        temp_board = [row[:] for row in self.board]  # Copy
        moved = False  # noqa: F841
        score_gain = 0  # noqa: F841

        # 1. Orient board so we always "Slide Left"
        if direction == "w":
            temp_board = self.transpose(temp_board)
        elif direction == "s":
            temp_board = self.transpose(temp_board)
            temp_board = self.reverse(temp_board)
        elif direction == "d":
            temp_board = self.reverse(temp_board)

        # 2. Apply Logic: Compress -> Merge -> Compress
        temp_board = self.compress(temp_board)
        temp_board, gain = self.merge(temp_board)
        temp_board = self.compress(temp_board)
        self.score += gain

        # 3. Restore Orientation
        if direction == "w":
            temp_board = self.transpose(temp_board)
        elif direction == "s":
            temp_board = self.reverse(temp_board)
            temp_board = self.transpose(temp_board)
        elif direction == "d":
            temp_board = self.reverse(temp_board)

        # 4. Check if board actually changed
        if temp_board != self.board:
            self.board = temp_board
            self.add_new_tile()
            return True
        return False

    def is_game_over(self):
        # Check for empty spots
        for r in range(SIZE):
            for c in range(SIZE):
                if self.board[r][c] == 0:
                    return False
        # Check for possible merges
        for r in range(SIZE):
            for c in range(SIZE - 1):
                if self.board[r][c] == self.board[r][c + 1]:
                    return False
        for c in range(SIZE):
            for r in range(SIZE - 1):
                if self.board[r][c] == self.board[r + 1][c]:
                    return False
        return True

    def display(self):
        os.system("cls" if os.name == "nt" else "clear")
        print(f"\n--- 2048 (Score: {self.score}) ---")
        for row in self.board:
            print(f"{row}")
        print("Controls: w (Up), s (Down), a (Left), d (Right), q (Quit)")


if __name__ == "__main__":
    game = Game2048()
    game.display()

    while not game.is_game_over():
        move = input("Move: ").lower()
        if move == "q":
            break
        if move in ["w", "a", "s", "d"]:
            if game.move(move):
                game.display()
            else:
                print("Invalid Move (No change)")

    print("Game Over!")
