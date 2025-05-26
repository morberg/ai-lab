import pygame
import random

# --- Constants ---
# Screen dimensions
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 620
PLAY_WIDTH = 300  # 10 blocks * 30 pixels
PLAY_HEIGHT = 600  # 20 blocks * 30 pixels
BLOCK_SIZE = 30

GRID_WIDTH = PLAY_WIDTH // BLOCK_SIZE  # 10
GRID_HEIGHT = PLAY_HEIGHT // BLOCK_SIZE  # 20

# Top-left corner of the play area
TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH - 150) // 2 + 150  # Shift right for score/next
TOP_LEFT_Y = (SCREEN_HEIGHT - PLAY_HEIGHT) // 2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)  # Empty cell color
GRID_COLOR = (40, 40, 40)  # Dark grey for grid lines
BG_COLOR = (10, 10, 25)  # Dark blue/purple background

# Tetromino shapes and their colors (pivot is (0,0) in local coords (row, col))
TETROMINOES = {
    "I": {"shape": [(0, -1), (0, 0), (0, 1), (0, 2)], "color": (0, 220, 220)},  # Cyan
    "O": {"shape": [(0, 0), (1, 0), (0, 1), (1, 1)], "color": (220, 220, 0)},  # Yellow
    "T": {
        "shape": [(0, 0), (-1, 0), (1, 0), (0, -1)],
        "color": (160, 0, 220),
    },  # Purple
    "S": {"shape": [(0, 0), (1, 0), (0, 1), (-1, 1)], "color": (0, 220, 0)},  # Green
    "Z": {"shape": [(0, 0), (-1, 0), (0, 1), (1, 1)], "color": (220, 0, 0)},  # Red
    "J": {"shape": [(0, 0), (-1, 0), (0, -1), (0, -2)], "color": (0, 0, 220)},  # Blue
    "L": {
        "shape": [(0, 0), (1, 0), (0, -1), (0, -2)],
        "color": (220, 120, 0),
    },  # Orange
}


# --- Piece Class ---
class Piece:
    def __init__(self, x, y, shape_name):
        self.x = x  # Grid column for pivot
        self.y = y  # Grid row for pivot
        self.shape_name = shape_name
        self.shape_template = TETROMINOES[shape_name]["shape"]
        self.color = TETROMINOES[shape_name]["color"]
        self.current_shape_coords = list(
            self.shape_template
        )  # Rotated (row_offset, col_offset)

    def get_rotated_coords(self, shape_coords, direction):
        rotated = []
        for r_offset, c_offset in shape_coords:
            if direction == "clockwise":  # (r, c) -> (c, -r)
                rotated.append((c_offset, -r_offset))
            elif direction == "counter_clockwise":  # (r, c) -> (-c, r)
                rotated.append((-c_offset, r_offset))
        return rotated

    def rotate(self, direction, grid):
        prospective_coords = self.get_rotated_coords(
            self.current_shape_coords, direction
        )
        if self.is_valid_position(prospective_coords, self.x, self.y, grid):
            self.current_shape_coords = prospective_coords
            return True

        # Basic wall kick: try moving 1 unit left/right if rotation failed
        # This is a very simplified wall kick, not full SRS
        for dx_kick in [-1, 1, -2, 2]:  # Try moving horizontally
            if self.is_valid_position(
                prospective_coords, self.x + dx_kick, self.y, grid
            ):
                self.x += dx_kick
                self.current_shape_coords = prospective_coords
                return True
        return False

    def is_valid_position(self, shape_coords_to_check, piece_x, piece_y, grid):
        for r_offset, c_offset in shape_coords_to_check:
            r_world, c_world = piece_y + r_offset, piece_x + c_offset

            if not (0 <= c_world < GRID_WIDTH):  # Check horizontal bounds
                return False
            if r_world >= GRID_HEIGHT:  # Check vertical bottom bound
                return False
            if (
                r_world >= 0 and grid[r_world][c_world] != BLACK
            ):  # Check collision with locked pieces
                return False
        return True


# --- Game Functions ---
def create_grid():
    return [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]


def new_piece():
    shape_name = random.choice(list(TETROMINOES.keys()))
    # Start piece with its pivot at y=1 (second row from top, index 1)
    # x is middle of the grid
    return Piece(x=GRID_WIDTH // 2, y=1, shape_name=shape_name)


def lock_piece(grid, piece):
    for r_offset, c_offset in piece.current_shape_coords:
        r, c = piece.y + r_offset, piece.x + c_offset
        if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
            grid[r][c] = piece.color


def clear_lines(grid):
    lines_cleared = 0
    new_grid_rows = []  # Store rows that are not cleared from bottom up

    for r in range(GRID_HEIGHT - 1, -1, -1):  # Iterate from bottom row upwards
        is_full = True
        for c in range(GRID_WIDTH):
            if grid[r][c] == BLACK:
                is_full = False
                break

        if is_full:
            lines_cleared += 1
            # This row will not be added to new_grid_rows, effectively removing it
        else:
            new_grid_rows.append(list(grid[r]))  # Keep the non-full row

    # Add empty rows at the top for each cleared line
    num_new_empty_rows = GRID_HEIGHT - len(new_grid_rows)
    for _ in range(num_new_empty_rows):
        new_grid_rows.append([BLACK for _ in range(GRID_WIDTH)])

    # Update the grid with the new arrangement (new_grid_rows is bottom-up, so reverse it)
    for r_idx, row_content in enumerate(reversed(new_grid_rows)):
        grid[r_idx] = row_content

    return lines_cleared


def calculate_score(lines):
    if lines == 1:
        return 100
    if lines == 2:
        return 300
    if lines == 3:
        return 500
    if lines == 4:
        return 800  # Tetris!
    return 0


# --- Drawing Functions ---
def draw_grid_lines(surface):
    for r in range(GRID_HEIGHT + 1):
        pygame.draw.line(
            surface,
            GRID_COLOR,
            (TOP_LEFT_X, TOP_LEFT_Y + r * BLOCK_SIZE),
            (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + r * BLOCK_SIZE),
        )
    for c in range(GRID_WIDTH + 1):
        pygame.draw.line(
            surface,
            GRID_COLOR,
            (TOP_LEFT_X + c * BLOCK_SIZE, TOP_LEFT_Y),
            (TOP_LEFT_X + c * BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT),
        )


def draw_locked_blocks(surface, grid):
    for r in range(GRID_HEIGHT):
        for c in range(GRID_WIDTH):
            if grid[r][c] != BLACK:
                block_color = grid[r][c]
                rect = (
                    TOP_LEFT_X + c * BLOCK_SIZE,
                    TOP_LEFT_Y + r * BLOCK_SIZE,
                    BLOCK_SIZE,
                    BLOCK_SIZE,
                )
                pygame.draw.rect(surface, block_color, rect)
                # Darker border for 3D effect
                border_color = (
                    max(0, block_color[0] - 50),
                    max(0, block_color[1] - 50),
                    max(0, block_color[2] - 50),
                )
                pygame.draw.rect(surface, border_color, rect, 3)


def draw_piece(
    surface, piece, offset_x=0, offset_y=0, custom_color=None, is_ghost=False
):
    actual_color = custom_color if custom_color else piece.color
    if is_ghost:
        # Ghost piece is semi-transparent main color
        ghost_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
        ghost_surface.fill(
            (actual_color[0], actual_color[1], actual_color[2], 80)
        )  # Alpha = 80

    for r_offset, c_offset in piece.current_shape_coords:
        # piece.y and piece.x are grid coordinates of the pivot
        # r_offset and c_offset are relative to the pivot
        r_world_grid = piece.y + r_offset
        c_world_grid = piece.x + c_offset

        # Only draw blocks that are within the visible play area (r_world_grid >= 0)
        if r_world_grid >= 0:
            block_render_x = TOP_LEFT_X + c_world_grid * BLOCK_SIZE + offset_x
            block_render_y = TOP_LEFT_Y + r_world_grid * BLOCK_SIZE + offset_y

            rect = (block_render_x, block_render_y, BLOCK_SIZE, BLOCK_SIZE)

            if is_ghost:
                surface.blit(ghost_surface, (block_render_x, block_render_y))
                # Optionally, draw a faint border for the ghost
                pygame.draw.rect(
                    surface,
                    (
                        actual_color[0] // 2,
                        actual_color[1] // 2,
                        actual_color[2] // 2,
                        100,
                    ),
                    rect,
                    1,
                )

            else:
                pygame.draw.rect(surface, actual_color, rect)
                border_color = (
                    max(0, actual_color[0] - 50),
                    max(0, actual_color[1] - 50),
                    max(0, actual_color[2] - 50),
                )
                pygame.draw.rect(surface, border_color, rect, 3)


def draw_ghost_piece(surface, piece, grid):
    ghost = Piece(piece.x, piece.y, piece.shape_name)
    ghost.current_shape_coords = list(
        piece.current_shape_coords
    )  # Match current piece's rotation

    # Move ghost down until it hits something or bottom
    while ghost.is_valid_position(
        ghost.current_shape_coords, ghost.x, ghost.y + 1, grid
    ):
        ghost.y += 1

    draw_piece(surface, ghost, is_ghost=True)


def draw_ui(surface, score, next_piece_obj):
    # Score
    font_score = pygame.font.SysFont("Consolas", 30, bold=True)
    score_label = font_score.render(f"Score: {score}", 1, WHITE)
    surface.blit(score_label, (TOP_LEFT_X + PLAY_WIDTH + 20, TOP_LEFT_Y + 50))

    # Next Piece
    font_next = pygame.font.SysFont("Consolas", 24, bold=True)
    next_label = font_next.render("Next:", 1, WHITE)
    next_area_x = TOP_LEFT_X + PLAY_WIDTH + 20
    next_area_y = TOP_LEFT_Y + 120
    surface.blit(next_label, (next_area_x, next_area_y - 30))

    # Draw the next_piece centered in a small box
    # For drawing, treat its pivot as (0,0) locally and offset the whole shape
    # Find min/max r/c offsets to help center it in the preview box (approx 4x4 blocks)

    preview_block_size = BLOCK_SIZE * 0.7
    shape_coords = next_piece_obj.current_shape_coords  # Use current rotation

    # Calculate bounding box of the shape to center it
    if not shape_coords:
        return
    min_r = min(r for r, c in shape_coords)
    max_r = max(r for r, c in shape_coords)
    min_c = min(c for r, c in shape_coords)
    max_c = max(c for r, c in shape_coords)

    shape_block_width = (max_c - min_c + 1) * preview_block_size
    shape_block_height = (max_r - min_r + 1) * preview_block_size

    # Center of the preview area (e.g., 5x4 blocks wide/high)
    preview_box_center_x = next_area_x + (5 * preview_block_size) / 2
    preview_box_center_y = next_area_y + (4 * preview_block_size) / 2

    # Offset to draw the shape so its center aligns with preview_box_center
    # Shape's own center (relative to its pivot, in block units):
    shape_center_c_offset = (min_c + max_c) / 2.0
    shape_center_r_offset = (min_r + max_r) / 2.0

    for r_off, c_off in shape_coords:
        # Position each block relative to the shape's calculated center, then place that at preview_box_center
        draw_x = (
            preview_box_center_x + (c_off - shape_center_c_offset) * preview_block_size
        )
        draw_y = (
            preview_box_center_y + (r_off - shape_center_r_offset) * preview_block_size
        )

        rect = (draw_x, draw_y, preview_block_size, preview_block_size)
        pygame.draw.rect(surface, next_piece_obj.color, rect)
        darker_color = (
            max(0, next_piece_obj.color[0] - 50),
            max(0, next_piece_obj.color[1] - 50),
            max(0, next_piece_obj.color[2] - 50),
        )
        pygame.draw.rect(surface, darker_color, rect, 2)


def draw_game_over(surface):
    font_large = pygame.font.SysFont("Impact", 70)
    font_small = pygame.font.SysFont("Arial", 30)

    game_text = font_large.render("GAME", 1, (200, 0, 0))
    over_text = font_large.render("OVER", 1, (200, 0, 0))
    restart_text = font_small.render("Press R to Restart", 1, WHITE)

    # Create a semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Black with alpha
    surface.blit(overlay, (0, 0))

    surface.blit(
        game_text,
        (
            SCREEN_WIDTH / 2 - game_text.get_width() / 2,
            SCREEN_HEIGHT / 2 - game_text.get_height() - 10,
        ),
    )
    surface.blit(
        over_text,
        (SCREEN_WIDTH / 2 - over_text.get_width() / 2, SCREEN_HEIGHT / 2 + 10),
    )
    surface.blit(
        restart_text,
        (
            SCREEN_WIDTH / 2 - restart_text.get_width() / 2,
            SCREEN_HEIGHT / 2 + over_text.get_height() + 30,
        ),
    )


# --- Main Game Loop ---
def main():
    pygame.init()
    pygame.font.init()  # Initialize font module
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flashy Tetris")
    clock = pygame.time.Clock()

    grid = create_grid()
    current_piece = new_piece()
    next_piece = new_piece()
    score = 0
    game_over = False

    fall_timer = 0
    fall_speed = 0.4  # Seconds per automatic drop
    level_threshold = 500  # Score to increase speed

    flash_alpha = 0  # For line clear screen flash

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds, target 60 FPS

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:  # Restart game
                        grid = create_grid()
                        current_piece = new_piece()
                        next_piece = new_piece()
                        score = 0
                        game_over = False
                        fall_timer = 0
                        fall_speed = 0.4
                        flash_alpha = 0
                else:  # Game is active
                    if event.key == pygame.K_j:  # Move Left
                        if current_piece.is_valid_position(
                            current_piece.current_shape_coords,
                            current_piece.x - 1,
                            current_piece.y,
                            grid,
                        ):
                            current_piece.x -= 1
                    elif event.key == pygame.K_l:  # Move Right
                        if current_piece.is_valid_position(
                            current_piece.current_shape_coords,
                            current_piece.x + 1,
                            current_piece.y,
                            grid,
                        ):
                            current_piece.x += 1
                    elif event.key == pygame.K_k:  # Rotate Clockwise
                        current_piece.rotate("clockwise", grid)
                    elif event.key == pygame.K_i:  # Rotate Counter-Clockwise
                        current_piece.rotate("counter_clockwise", grid)
                    elif (
                        event.key == pygame.K_DOWN
                    ):  # Soft drop (optional, or make automatic faster)
                        if current_piece.is_valid_position(
                            current_piece.current_shape_coords,
                            current_piece.x,
                            current_piece.y + 1,
                            grid,
                        ):
                            current_piece.y += 1
                            fall_timer = 0  # Reset auto-fall timer
                    elif event.key == pygame.K_SPACE:  # Hard Drop
                        while current_piece.is_valid_position(
                            current_piece.current_shape_coords,
                            current_piece.x,
                            current_piece.y + 1,
                            grid,
                        ):
                            current_piece.y += 1
                        # Lock piece immediately after hard drop
                        lock_piece(grid, current_piece)
                        lines_cleared = clear_lines(grid)
                        if lines_cleared > 0:
                            score += calculate_score(lines_cleared)
                            flash_alpha = 180  # Trigger screen flash
                        current_piece = next_piece
                        next_piece = new_piece()
                        if not current_piece.is_valid_position(
                            current_piece.current_shape_coords,
                            current_piece.x,
                            current_piece.y,
                            grid,
                        ):
                            game_over = True
                        fall_timer = 0  # Reset fall timer

        # --- Game Logic ---
        if not game_over:
            fall_timer += dt
            if fall_timer >= fall_speed:
                fall_timer = 0
                if current_piece.is_valid_position(
                    current_piece.current_shape_coords,
                    current_piece.x,
                    current_piece.y + 1,
                    grid,
                ):
                    current_piece.y += 1
                else:  # Piece has landed
                    lock_piece(grid, current_piece)
                    lines_cleared = clear_lines(grid)
                    if lines_cleared > 0:
                        score += calculate_score(lines_cleared)
                        flash_alpha = 180  # Trigger screen flash

                        # Increase speed based on score (simple leveling)
                        if (
                            score // level_threshold
                            > (score - calculate_score(lines_cleared))
                            // level_threshold
                        ):
                            fall_speed = max(
                                0.1, fall_speed * 0.9
                            )  # Decrease fall speed by 10%, min 0.1s

                    current_piece = next_piece
                    next_piece = new_piece()
                    if not current_piece.is_valid_position(
                        current_piece.current_shape_coords,
                        current_piece.x,
                        current_piece.y,
                        grid,
                    ):
                        game_over = True

        # --- Drawing ---
        screen.fill(BG_COLOR)
        draw_grid_lines(screen)
        draw_locked_blocks(screen, grid)

        if not game_over:
            draw_ghost_piece(screen, current_piece, grid)
            draw_piece(screen, current_piece)

        draw_ui(screen, score, next_piece)

        # Screen flash effect
        if flash_alpha > 0:
            flash_surface = pygame.Surface(
                (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
            )
            flash_surface.fill((255, 255, 255, flash_alpha))  # White flash
            screen.blit(flash_surface, (0, 0))
            flash_alpha -= (
                250 * dt
            )  # Fade out speed (adjust based on FPS, e.g. 250 units per sec)
            if flash_alpha < 0:
                flash_alpha = 0

        if game_over:
            draw_game_over(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
