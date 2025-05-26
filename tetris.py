import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Constants
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
GRID_X_OFFSET = 50
GRID_Y_OFFSET = 50
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700

# Colors with vibrant, flashy palette
COLORS = {
    "I": (0, 255, 255),  # Cyan
    "O": (255, 255, 0),  # Yellow
    "T": (128, 0, 128),  # Purple
    "S": (0, 255, 0),  # Green
    "Z": (255, 0, 0),  # Red
    "J": (0, 0, 255),  # Blue
    "L": (255, 165, 0),  # Orange
    "EMPTY": (20, 20, 30),  # Dark background
    "GRID": (60, 60, 80),  # Grid lines
    "GHOST": (100, 100, 100, 100),  # Ghost piece
}

# Tetris pieces
PIECES = {
    "I": [["....", "IIII", "....", "...."], [".I..", ".I..", ".I..", ".I.."]],
    "O": [["OO", "OO"]],
    "T": [
        ["...", "TTT", ".T."],
        [".T.", "TT.", ".T."],
        [".T.", "TTT", "..."],
        [".T.", ".TT", ".T."],
    ],
    "S": [["...", ".SS", "SS."], ["S..", "SS.", ".S."]],
    "Z": [["...", "ZZ.", ".ZZ"], [".Z.", "ZZ.", "Z.."]],
    "J": [
        ["...", "JJJ", "..J"],
        ["JJ.", "J..", "J.."],
        ["J..", "JJJ", "..."],
        [".J.", ".J.", "JJ."],
    ],
    "L": [
        ["...", "LLL", "L.."],
        [".L.", ".L.", "LL."],
        ["..L", "LLL", "..."],
        ["LL.", ".L.", ".L."],
    ],
}


# Particle class for effects
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-8, -2)
        self.color = color
        self.life = 60
        self.max_life = 60

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # gravity
        self.life -= 1

    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            color = (*self.color[:3], alpha)
            size = int(4 * (self.life / self.max_life))
            if size > 0:
                pygame.draw.circle(
                    screen, self.color[:3], (int(self.x), int(self.y)), size
                )


class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Flashy Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.current_pos = [0, 0]
        self.current_rotation = 0
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500  # milliseconds
        self.particles = []
        self.line_clear_animation = 0
        self.cleared_lines = []

        self.spawn_piece()

    def spawn_piece(self):
        piece_type = random.choice(list(PIECES.keys()))
        self.current_piece = piece_type
        self.current_pos = [GRID_WIDTH // 2 - 1, 0]
        self.current_rotation = 0

        # Check game over
        if self.check_collision():
            self.game_over()

    def get_piece_shape(self):
        if self.current_piece:
            rotations = PIECES[self.current_piece]
            if len(rotations) == 1:
                return rotations[0]
            return rotations[self.current_rotation % len(rotations)]
        return []

    def check_collision(self, dx=0, dy=0, rotation=0):
        shape = PIECES[self.current_piece]
        if len(shape) > 1:
            test_rotation = (self.current_rotation + rotation) % len(shape)
            piece_shape = shape[test_rotation]
        else:
            piece_shape = shape[0]

        for y, row in enumerate(piece_shape):
            for x, cell in enumerate(row):
                if cell != ".":
                    new_x = self.current_pos[0] + x + dx
                    new_y = self.current_pos[1] + y + dy

                    if (
                        new_x < 0
                        or new_x >= GRID_WIDTH
                        or new_y >= GRID_HEIGHT
                        or (new_y >= 0 and self.grid[new_y][new_x] != 0)
                    ):
                        return True
        return False

    def place_piece(self):
        shape = self.get_piece_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell != ".":
                    grid_x = self.current_pos[0] + x
                    grid_y = self.current_pos[1] + y
                    if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                        self.grid[grid_y][grid_x] = self.current_piece

                        # Add particles
                        px = GRID_X_OFFSET + grid_x * CELL_SIZE + CELL_SIZE // 2
                        py = GRID_Y_OFFSET + grid_y * CELL_SIZE + CELL_SIZE // 2
                        for _ in range(3):
                            self.particles.append(
                                Particle(px, py, COLORS[self.current_piece])
                            )

        self.check_lines()
        self.spawn_piece()

    def check_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(cell != 0 for cell in self.grid[y]):
                lines_to_clear.append(y)

        if lines_to_clear:
            self.cleared_lines = lines_to_clear[:]
            self.line_clear_animation = 30

            # Add explosion particles
            for y in lines_to_clear:
                for x in range(GRID_WIDTH):
                    px = GRID_X_OFFSET + x * CELL_SIZE + CELL_SIZE // 2
                    py = GRID_Y_OFFSET + y * CELL_SIZE + CELL_SIZE // 2
                    color = COLORS[self.grid[y][x]]
                    for _ in range(8):
                        self.particles.append(Particle(px, py, color))

            # Clear lines and update score
            for y in sorted(lines_to_clear, reverse=True):
                del self.grid[y]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])

            lines_count = len(lines_to_clear)
            self.lines_cleared += lines_count
            # Score based on number of lines cleared simultaneously
            score_multiplier = [0, 100, 300, 500, 800][min(lines_count, 4)]
            self.score += score_multiplier * (self.level + 1)
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(50, 500 - (self.level - 1) * 50)

    def move_piece(self, dx, dy):
        if not self.check_collision(dx, dy):
            self.current_pos[0] += dx
            self.current_pos[1] += dy
            return True
        return False

    def rotate_piece(self, direction):
        if self.current_piece and len(PIECES[self.current_piece]) > 1:
            if not self.check_collision(rotation=direction):
                self.current_rotation = (self.current_rotation + direction) % len(
                    PIECES[self.current_piece]
                )

    def drop_piece(self):
        while self.move_piece(0, 1):
            pass
        self.place_piece()

    def get_ghost_position(self):
        ghost_y = self.current_pos[1]
        while not self.check_collision(0, ghost_y - self.current_pos[1] + 1):
            ghost_y += 1
        return ghost_y

    def draw_cell(self, x, y, color, alpha=255):
        rect = pygame.Rect(
            GRID_X_OFFSET + x * CELL_SIZE,
            GRID_Y_OFFSET + y * CELL_SIZE,
            CELL_SIZE - 1,
            CELL_SIZE - 1,
        )

        # Create gradient effect
        if alpha == 255:
            # Main color
            pygame.draw.rect(self.screen, color, rect)
            # Highlight
            highlight_rect = pygame.Rect(
                rect.x + 2, rect.y + 2, rect.width - 8, rect.height - 8
            )
            highlight_color = tuple(min(255, c + 40) for c in color)
            pygame.draw.rect(self.screen, highlight_color, highlight_rect)
            # Shadow
            shadow_rect = pygame.Rect(
                rect.x + 4, rect.y + 4, rect.width - 12, rect.height - 12
            )
            shadow_color = tuple(max(0, c - 40) for c in color)
            pygame.draw.rect(self.screen, shadow_color, shadow_rect)
        else:
            # Ghost piece - semi-transparent
            s = pygame.Surface((CELL_SIZE - 1, CELL_SIZE - 1))
            s.set_alpha(alpha)
            s.fill(color)
            self.screen.blit(s, (rect.x, rect.y))

    def draw_grid(self):
        # Draw background
        bg_rect = pygame.Rect(
            GRID_X_OFFSET,
            GRID_Y_OFFSET,
            GRID_WIDTH * CELL_SIZE,
            GRID_HEIGHT * CELL_SIZE,
        )
        pygame.draw.rect(self.screen, COLORS["EMPTY"], bg_rect)

        # Draw grid lines with glow effect
        for x in range(GRID_WIDTH + 1):
            start_pos = (GRID_X_OFFSET + x * CELL_SIZE, GRID_Y_OFFSET)
            end_pos = (
                GRID_X_OFFSET + x * CELL_SIZE,
                GRID_Y_OFFSET + GRID_HEIGHT * CELL_SIZE,
            )
            pygame.draw.line(self.screen, COLORS["GRID"], start_pos, end_pos)

        for y in range(GRID_HEIGHT + 1):
            start_pos = (GRID_X_OFFSET, GRID_Y_OFFSET + y * CELL_SIZE)
            end_pos = (
                GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE,
                GRID_Y_OFFSET + y * CELL_SIZE,
            )
            pygame.draw.line(self.screen, COLORS["GRID"], start_pos, end_pos)

    def draw_placed_pieces(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] != 0:
                    # Flash effect for cleared lines
                    if y in self.cleared_lines and self.line_clear_animation > 0:
                        flash_intensity = int(100 * (self.line_clear_animation / 30))
                        color = tuple(
                            min(255, c + flash_intensity)
                            for c in COLORS[self.grid[y][x]]
                        )
                    else:
                        color = COLORS[self.grid[y][x]]
                    self.draw_cell(x, y, color)

    def draw_current_piece(self):
        if self.current_piece:
            # Draw ghost piece
            ghost_y = self.get_ghost_position()
            shape = self.get_piece_shape()
            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell != ".":
                        grid_x = self.current_pos[0] + x
                        grid_y = ghost_y + y
                        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                            self.draw_cell(
                                grid_x, grid_y, COLORS[self.current_piece], 50
                            )

            # Draw current piece
            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell != ".":
                        grid_x = self.current_pos[0] + x
                        grid_y = self.current_pos[1] + y
                        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                            self.draw_cell(grid_x, grid_y, COLORS[self.current_piece])

    def draw_ui(self):
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 20, 50))

        # Level
        level_text = self.font.render(f"Level: {self.level}", True, (255, 255, 255))
        self.screen.blit(level_text, (GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 20, 90))

        # Lines
        lines_text = self.font.render(
            f"Lines: {self.lines_cleared}", True, (255, 255, 255)
        )
        self.screen.blit(lines_text, (GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 20, 130))

        # Controls
        controls = [
            "Controls:",
            "J - Move Left",
            "L - Move Right",
            "K - Rotate CW",
            "I - Rotate CCW",
            "Space - Drop",
        ]
        for i, text in enumerate(controls):
            color = (255, 255, 0) if i == 0 else (200, 200, 200)
            control_text = pygame.font.Font(None, 24).render(text, True, color)
            self.screen.blit(
                control_text,
                (GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 20, 200 + i * 25),
            )

    def draw_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
            else:
                particle.draw(self.screen)

    def game_over(self):
        # Game over screen with particles
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.big_font.render("GAME OVER", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)
        )
        self.screen.blit(game_over_text, text_rect)

        final_score_text = self.font.render(
            f"Final Score: {self.score}", True, (255, 255, 255)
        )
        score_rect = final_score_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)
        )
        self.screen.blit(final_score_text, score_rect)

        restart_text = self.font.render(
            "Press R to restart or Q to quit", True, (255, 255, 255)
        )
        restart_rect = restart_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60)
        )
        self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

        # Wait for input
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.__init__()  # Restart
                        return True
                    elif event.key == pygame.K_q:
                        return False
        return True

    def run(self):
        running = True

        while running:
            dt = self.clock.tick(60)
            self.fall_time += dt

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_j:  # Move left
                        self.move_piece(-1, 0)
                    elif event.key == pygame.K_l:  # Move right
                        self.move_piece(1, 0)
                    elif event.key == pygame.K_k:  # Rotate clockwise
                        self.rotate_piece(1)
                    elif event.key == pygame.K_i:  # Rotate counterclockwise
                        self.rotate_piece(-1)
                    elif event.key == pygame.K_SPACE:  # Drop
                        self.drop_piece()

            # Natural fall
            if self.fall_time >= self.fall_speed:
                if not self.move_piece(0, 1):
                    self.place_piece()
                self.fall_time = 0

            # Update animations
            if self.line_clear_animation > 0:
                self.line_clear_animation -= 1
                if self.line_clear_animation == 0:
                    self.cleared_lines = []

            # Draw everything
            self.screen.fill((10, 10, 20))  # Dark background
            self.draw_grid()
            self.draw_placed_pieces()
            self.draw_current_piece()
            self.draw_particles()
            self.draw_ui()

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    game = TetrisGame()
    game.run()
