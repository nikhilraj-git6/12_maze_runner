import pygame
import time
import json
import os

from game.maze import generate_maze, shortest_path, CELL
from game.player import Player


FPS = 60

BG = (240, 235, 220)
WALL_COLOR = (40, 40, 60)
EXIT_COLOR = (80, 200, 80)
PATH_COLOR = (255, 190, 60)
FOG_COLOR = (15, 15, 25)

# Task 2: Fog of War radius
FOG_RADIUS = 3

# Task 3: Leaderboard settings
LEADERBOARD_FILE = "leaderboard.json"
MAX_SCORES = 5

# Task 4: Difficulty settings
DIFFICULTIES = {
    "Easy": (10, 8),
    "Medium": (15, 13),
    "Hard": (20, 18)
}

DIFFICULTY_BUTTONS = {
    "Easy": pygame.Rect(0, 0, 300, 70),
    "Medium": pygame.Rect(0, 0, 300, 70),
    "Hard": pygame.Rect(0, 0, 300, 70)
}


class GameEngine:
    def __init__(self):
        pygame.init()

        # Task 4:
        # Start with a difficulty-selection screen.
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Maze Runner")

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(
            "monospace",
            22
        )

        self.big_font = pygame.font.SysFont(
            "monospace",
            36,
            bold=True
        )

        self.title_font = pygame.font.SysFont(
            "monospace",
            42,
            bold=True
        )

        # Current difficulty
        self.difficulty = None
        self.cols = 15
        self.rows = 13

        # Load leaderboard
        self.leaderboard = self.load_leaderboard()

        # Start at difficulty screen
        self.in_difficulty_screen = True

    # =========================================================
    # Task 3: Leaderboard
    # =========================================================

    def load_leaderboard(self):
        """
        Load the leaderboard from leaderboard.json.
        """

        if not os.path.exists(LEADERBOARD_FILE):
            return []

        try:
            with open(
                LEADERBOARD_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if isinstance(data, list):
                return sorted(
                    [float(score) for score in data]
                )[:MAX_SCORES]

        except (
            json.JSONDecodeError,
            OSError,
            ValueError
        ):
            pass

        return []

    def save_leaderboard(self):
        """
        Save the current top 5 scores.
        """

        with open(
            LEADERBOARD_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.leaderboard,
                file,
                indent=4
            )

    def add_score(self, completion_time):
        """
        Add completion time and keep
        only the fastest 5 times.
        """

        self.leaderboard.append(
            float(completion_time)
        )

        self.leaderboard.sort()

        self.leaderboard = self.leaderboard[:MAX_SCORES]

        self.save_leaderboard()

    # =========================================================
    # Task 4: Start selected difficulty
    # =========================================================

    def start_difficulty(self, difficulty):
        """
        Start the game using the selected difficulty.
        """

        self.difficulty = difficulty

        self.cols, self.rows = DIFFICULTIES[difficulty]

        # Calculate screen size from selected maze dimensions
        width = self.cols * CELL
        height = self.rows * CELL + 60

        self.screen = pygame.display.set_mode(
            (width, height)
        )

        pygame.display.set_caption(
            f"Maze Runner - {difficulty}"
        )

        self.in_difficulty_screen = False

        self.reset()

    # =========================================================
    # Game reset
    # =========================================================

    def reset(self):
        """
        Generate a fresh maze using the currently
        selected difficulty.
        """

        self.walls = generate_maze(
            self.cols,
            self.rows
        )

        self.player = Player(0, 0)

        self.exit_rect = pygame.Rect(
            (self.cols - 1) * CELL + 5,
            (self.rows - 1) * CELL + 5,
            CELL - 10,
            CELL - 10
        )

        self.start_time = time.time()

        self.elapsed = 0

        self.won = False

        # Prevent duplicate leaderboard entries
        self.score_saved = False

        # =====================================================
        # Task 1: Shortest Path Hint
        # =====================================================

        self.show_path = False
        self.path = []

    # =========================================================
    # Task 4: Difficulty Selection Screen
    # =========================================================

    def draw_difficulty_screen(self):
        """
        Draw the difficulty selection screen.
        """

        self.screen.fill(BG)

        title = self.title_font.render(
            "MAZE RUNNER",
            True,
            (30, 30, 50)
        )

        self.screen.blit(
            title,
            (
                self.screen.get_width() // 2 -
                title.get_width() // 2,
                70
            )
        )

        subtitle = self.font.render(
            "Select Difficulty",
            True,
            (60, 60, 70)
        )

        self.screen.blit(
            subtitle,
            (
                self.screen.get_width() // 2 -
                subtitle.get_width() // 2,
                130
            )
        )

        button_x = (
            self.screen.get_width() // 2 - 150
        )

        button_y = 200

        for index, (difficulty, dimensions) in enumerate(
            DIFFICULTIES.items()
        ):

            width, height = dimensions

            rect = pygame.Rect(
                button_x,
                button_y + index * 100,
                300,
                70
            )

            DIFFICULTY_BUTTONS[difficulty] = rect

            pygame.draw.rect(
                self.screen,
                (50, 70, 100),
                rect,
                border_radius=10
            )

            label = self.font.render(
                f"{difficulty}: {width}x{height}",
                True,
                (255, 255, 255)
            )

            self.screen.blit(
                label,
                (
                    rect.centerx - label.get_width() // 2,
                    rect.centery - label.get_height() // 2
                )
            )

        pygame.display.flip()

    # =========================================================
    # Events
    # =========================================================

    def handle_difficulty_events(self):
        """
        Handle clicks on the difficulty buttons.
        """

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:

                    for difficulty, rect in DIFFICULTY_BUTTONS.items():

                        if rect.collidepoint(event.pos):
                            self.start_difficulty(
                                difficulty
                            )

                            break

        return True

    def handle_events(self):
        """
        Handle normal game events.
        """

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            # =================================================
            # R = New maze
            # Keeps the current difficulty
            # =================================================

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_r
            ):
                self.reset()

            # =================================================
            # H = BFS shortest path hint
            # =================================================

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_h
            ):

                self.show_path = not self.show_path

                if self.show_path:

                    # Current player cell
                    start = (
                        self.player.rect.centery // CELL,
                        self.player.rect.centerx // CELL
                    )

                    # Current exit cell
                    goal = (
                        self.rows - 1,
                        self.cols - 1
                    )

                    # Task 1: BFS
                    self.path = shortest_path(
                        self.walls,
                        start,
                        goal
                    )

        return True

    # =========================================================
    # Update
    # =========================================================

    def update(self):

        if self.won:
            return

        keys = pygame.key.get_pressed()

        # Existing player movement
        self.player.move(
            keys,
            self.walls,
            self.rows,
            self.cols
        )

        # Timer
        self.elapsed = (
            time.time() -
            self.start_time
        )

        # Check exit
        if self.player.rect.colliderect(
            self.exit_rect
        ):

            self.won = True

            # Task 3:
            # Save score only once
            if not self.score_saved:

                self.add_score(
                    self.elapsed
                )

                self.score_saved = True

    # =========================================================
    # Draw Maze
    # =========================================================

    def draw_maze(self):

        wall_w = 3

        for r in range(self.rows):

            for c in range(self.cols):

                x = c * CELL
                y = r * CELL

                w = self.walls[r][c]

                # North
                if w[0]:

                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y),
                        (x + CELL, y),
                        wall_w
                    )

                # South
                if w[1]:

                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y + CELL),
                        (x + CELL, y + CELL),
                        wall_w
                    )

                # East
                if w[2]:

                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x + CELL, y),
                        (x + CELL, y + CELL),
                        wall_w
                    )

                # West
                if w[3]:

                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y),
                        (x, y + CELL),
                        wall_w
                    )

    # =========================================================
    # Task 2: Fog of War
    # =========================================================

    def draw_fog(self):

        width = self.cols * CELL
        height = self.rows * CELL

        fog = pygame.Surface(
            (width, height),
            pygame.SRCALPHA
        )

        # Dark overlay
        fog.fill(
            (*FOG_COLOR, 230)
        )

        # Player position
        player_x = self.player.rect.centerx
        player_y = self.player.rect.centery

        # Radius = 3 cells
        reveal_radius = FOG_RADIUS * CELL

        # Transparent circle around player
        pygame.draw.circle(
            fog,
            (0, 0, 0, 0),
            (player_x, player_y),
            reveal_radius
        )

        self.screen.blit(
            fog,
            (0, 0)
        )

    # =========================================================
    # Draw
    # =========================================================

    def draw(self):

        maze_width = self.cols * CELL
        maze_height = self.rows * CELL

        # Background
        self.screen.fill(BG)

        # Maze
        self.draw_maze()

        # Exit
        pygame.draw.rect(
            self.screen,
            EXIT_COLOR,
            self.exit_rect,
            border_radius=4
        )

        # =====================================================
        # Task 1: BFS Path
        # =====================================================

        if self.show_path:

            square_size = CELL // 2

            inset = (
                CELL - square_size
            ) // 2

            for row, col in self.path:

                pygame.draw.rect(
                    self.screen,
                    PATH_COLOR,
                    (
                        col * CELL + inset,
                        row * CELL + inset,
                        square_size,
                        square_size
                    )
                )

        # Exit label
        ex_label = self.font.render(
            "EXIT",
            True,
            (20, 80, 20)
        )

        self.screen.blit(
            ex_label,
            (
                self.exit_rect.x + 2,
                self.exit_rect.y + 4
            )
        )

        # Player
        self.player.draw(
            self.screen
        )

        # =====================================================
        # Task 2: Fog
        # =====================================================

        self.draw_fog()

        # Keep player visible
        self.player.draw(
            self.screen
        )

        # =====================================================
        # HUD
        # =====================================================

        hud = pygame.Rect(
            0,
            maze_height,
            maze_width,
            60
        )

        pygame.draw.rect(
            self.screen,
            (30, 30, 50),
            hud
        )

        time_surf = self.font.render(
            (
                f"Time: {self.elapsed:.1f}s   "
                f"H = Hint   R = New Maze"
            ),
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            time_surf,
            (
                10,
                maze_height + 18
            )
        )

        # =====================================================
        # Task 3: Win Screen + Leaderboard
        # =====================================================

        if self.won:

            overlay = pygame.Surface(
                (maze_width, maze_height),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 190)
            )

            self.screen.blit(
                overlay,
                (0, 0)
            )

            # Solved message
            msg = self.big_font.render(
                f"Solved in {self.elapsed:.1f}s!",
                True,
                (80, 240, 80)
            )

            self.screen.blit(
                msg,
                (
                    maze_width // 2 -
                    msg.get_width() // 2,
                    25
                )
            )

            # Leaderboard title
            leaderboard_title = self.font.render(
                "TOP 5 FASTEST TIMES",
                True,
                (255, 200, 60)
            )

            self.screen.blit(
                leaderboard_title,
                (
                    maze_width // 2 -
                    leaderboard_title.get_width() // 2,
                    80
                )
            )

            # Leaderboard entries
            if self.leaderboard:

                for index, score in enumerate(
                    self.leaderboard
                ):

                    score_text = self.font.render(
                        f"{index + 1}. {score:.1f}s",
                        True,
                        (230, 230, 230)
                    )

                    self.screen.blit(
                        score_text,
                        (
                            maze_width // 2 -
                            score_text.get_width() // 2,
                            120 + index * 35
                        )
                    )

            else:

                no_scores = self.font.render(
                    "No scores yet",
                    True,
                    (200, 200, 200)
                )

                self.screen.blit(
                    no_scores,
                    (
                        maze_width // 2 -
                        no_scores.get_width() // 2,
                        120
                    )
                )

            # Restart
            sub = self.font.render(
                "Press R for a new maze",
                True,
                (200, 200, 200)
            )

            self.screen.blit(
                sub,
                (
                    maze_width // 2 -
                    sub.get_width() // 2,
                    maze_height - 45
                )
            )

        pygame.display.flip()

    # =========================================================
    # Main Loop
    # =========================================================

    def run(self):

        running = True

        while running:

            # =================================================
            # Task 4: Difficulty Selection
            # =================================================

            if self.in_difficulty_screen:

                running = self.handle_difficulty_events()

                if self.in_difficulty_screen:
                    self.draw_difficulty_screen()

            # =================================================
            # Normal Game
            # =================================================

            else:

                running = self.handle_events()

                self.update()

                self.draw()

                self.clock.tick(FPS)

        pygame.quit()