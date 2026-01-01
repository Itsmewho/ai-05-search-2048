import random
import os


# ---- Config

SIZE = 4
WIN_SCORE = 2048


class Game2048:
    def __init__(self):
        self.board = [[0] * SIZE for _ in range(SIZE)]
        self.score = 0
        self.game_won = False
        self.game_over = False
        # Start with 2 tiles :D
        self.spawn_tile()
        self.spawn_tile()

    # --- Core logic
    def spawn_tile(self):
        empty_cells = [
            (r, c) for r in range(SIZE) for c in range(SIZE) if self.board[r][c] == 0
        ]
        if not empty_cells:
            return
        r, c = random.choice(empty_cells)
        self.board[r][c] = 2 if random.random() < 0.9 else 4

    def compress(self, row):
        """Slides all non-zero numbers to the left."""
        new_row = [i for i in row if i != 0]
        new_row += [0] * (SIZE - len(new_row))
        return new_row

    def merge(self, row):
        """Combines neighbors (Left to Right)."""
        for i in range(SIZE - 1):
            if row[i] != 0 and row[i] == row[i + 1]:
                row[i] *= 2
                self.score += row[i]
                row[i + 1] = 0
                if row[i] == WIN_SCORE:
                    self.game_won = True
        return row

    def move_row_left(self, row):
        """Helper: Performs Compress -> Merge -> Compress on a single row."""
        row = self.compress(row)
        row = self.merge(row)
        row = self.compress(row)
        return row

    def move(self, direction):
        """
        Executes the global move.
        Directions: 'w' (Up), 's' (Down), 'a' (Left), 'd' (Right)
        """
        if self.game_over:
            return False

        # Create a rotated copy of the board so we can always treat it as "Left"
        # This simplifies the math significantly.
        temp_board = [r[:] for r in self.board]
        rotated = False  # noqa: F841

        if direction == "w":  # Up (Rotate 270 deg or 90 CCW to make Up point Left)
            temp_board = [
                list(row) for row in zip(*temp_board[::-1])
            ]  # 90 deg rotation logic is tricky.
            temp_board = [
                [temp_board[c][r] for c in range(SIZE)] for r in range(SIZE)
            ]  # Transpose
        elif direction == "s":  # Down
            temp_board = [
                [temp_board[c][r] for c in range(SIZE)] for r in range(SIZE)
            ]  # Transpose
            temp_board = [
                row[::-1] for row in temp_board
            ]  # Reverse (effectively rotated)
        elif direction == "d":  # Right
            temp_board = [row[::-1] for row in temp_board]  # Just reverse rows

        # Apply Slide Left Logic to every row
        new_board = []
        for row in temp_board:
            new_board.append(self.move_row_left(row))

        # Rotate Back
        if direction == "w":
            new_board = [[new_board[c][r] for c in range(SIZE)] for r in range(SIZE)]
        elif direction == "s":
            new_board = [row[::-1] for row in new_board]
            new_board = [[new_board[c][r] for c in range(SIZE)] for r in range(SIZE)]
        elif direction == "d":
            new_board = [row[::-1] for row in new_board]

        # Check if anything changed
        if new_board != self.board:
            self.board = new_board
            self.spawn_tile()
            if not self.can_move():
                self.game_over = True
            return True
        return False

    def can_move(self):
        """Checks if any moves are possible (Empty spots or mergeable neighbors)."""
        for r in range(SIZE):
            for c in range(SIZE):
                if self.board[r][c] == 0:
                    return True
                if c < SIZE - 1 and self.board[r][c] == self.board[r][c + 1]:
                    return True
                if r < SIZE - 1 and self.board[r][c] == self.board[r + 1][c]:
                    return True
        return False

    # --- Visuals (The Interface) ---
    def display(self):
        os.system("cls" if os.name == "nt" else "clear")

        # Width Calculation: (4 cells * 6 chars) + 7 vertical bars = 31 chars

        print("╔═══════════════════════════════╗")
        print(f"║{f' 2048 - SCORE: {self.score} ':^31}║")
        print("╠═══════════════════════════════╣")

        # Top of the grid
        print("║ ┌──────┬──────┬──────┬──────┐ ║")

        for r, row in enumerate(self.board):
            # Formatted Row: Each number centered in 6 spaces
            line = "│".join([f"{num:^6}" if num > 0 else "      " for num in row])
            print(f"║ │{line}│ ║")

            # Print divider only if it's not the last row
            if r < SIZE - 1:
                print("║ ├──────┼──────┼──────┼──────┤ ║")

        # Bottom of the grid
        print("║ └──────┴──────┴──────┴──────┘ ║")
        print("╚═══════════════════════════════╝")
        print(" Controls: W(Up) A(Left) S(Down) D(Right)")
        if self.game_over:
            print("\n GAME OVER! No moves left.")


# --- Game Loop ---
if __name__ == "__main__":
    game = Game2048()

    while True:
        game.display()
        if game.game_over:
            break

        choice = input(" Move: ").lower()
        if choice == "q":
            break

        if choice in ["w", "a", "s", "d"]:
            game.move(choice)
