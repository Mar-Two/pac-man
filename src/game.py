import pygame
from mazegenerator import MazeGenerator

from .colors import DARK_BLUE
from .state_machine import State, StateMachine
from .entities import PacMan #, Ghost


class Game(State):
    """Partie en cours : le labyrinthe et Pac-Man."""

    MAZE_SCALE = 0.9
    CLOSED_CELL = 15
    KEY_DIRECTIONS = {
          pygame.K_UP: (0, -1),
          pygame.K_w: (0, -1),
          pygame.K_DOWN: (0, 1),
          pygame.K_s: (0, 1),
          pygame.K_LEFT: (-1, 0),
          pygame.K_a: (-1, 0),
          pygame.K_RIGHT: (1, 0),
          pygame.K_d: (1, 0)}

    def __init__(self, state_machine: StateMachine, maze: MazeGenerator) -> None:
        """Prépare la partie et place Pac-Man sur une case libre près du centre.

        Args:
            state_machine: machine à états qui possède cette partie.
            maze: labyrinthe généré dans lequel se joue la partie.
        """
        super().__init__(state_machine)
        self.maze = maze
        self.maze_grid = maze.maze
        self.maze_height = len(self.maze_grid)
        self.maze_width = len(self.maze_grid[0])
        x, y = self.find_spawn()
        self.pacman = PacMan(x, y)

    def on_exit(self) -> None:
        """Annule le virage en attente quand on quitte la partie (pause, menu...)."""
        self.pacman.next_direction = (0, 0)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Gère la pause (Échap) et les virages de Pac-Man.

        Un virage reste en attente tant que sa touche est enfoncée.

        Args:
            event: événement reçu par la boucle principale.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state_machine.change("pause_menu")
            elif event.key in self.KEY_DIRECTIONS:
                self.pacman.next_direction = self.KEY_DIRECTIONS[event.key]
        elif event.type == pygame.KEYUP:
            if event.key in self.KEY_DIRECTIONS:
                if self.KEY_DIRECTIONS[event.key] == self.pacman.next_direction:
                    self.pacman.next_direction = (0, 0)

    def update(self) -> None:
        """Fait avancer Pac-Man, une fois par image."""
        self.pacman.update(self.maze_grid)

    def find_spawn(self) -> tuple[int, int]:
        """Cherche la case libre la plus proche du centre du labyrinthe.

        Les cases fermées (celles du « 42 ») sont ignorées.

        Returns:
            Coordonnées (x, y) de la case trouvée, dans la grille.

        Raises:
            ValueError: si aucune case du labyrinthe n'est libre.
        """
        center_x = self.maze_width // 2
        center_y = self.maze_height // 2
        for distance in range(max(self.maze_width, self.maze_height)):
            for dy in range(-distance, distance + 1):
                for dx in range(-distance, distance + 1):
                    x = center_x + dx
                    y = center_y + dy
                    if x < 0 or x >= self.maze_width or y < 0 or y >= self.maze_height:
                        continue
                    if self.maze_grid[y][x] != self.CLOSED_CELL:
                        return (x, y)
        raise ValueError("aucune case libre pour faire spawn Pac-Man")

    def draw(self, screen: pygame.Surface) -> None:
        """Dessine les murs du labyrinthe, centré dans l'écran, puis Pac-Man.

        Args:
            screen: surface de la fenêtre sur laquelle dessiner.
        """
        screen_rect = screen.get_rect()
        width_max = (screen_rect.width * self.MAZE_SCALE) // self.maze_width
        height_max = (screen_rect.height * self.MAZE_SCALE) // self.maze_height
        cell_size = min(width_max, height_max)
        x_offset = (screen_rect.width / 2) - ((cell_size * self.maze_width) / 2)
        y_offset = (screen_rect.height / 2) - ((cell_size * self.maze_height) / 2)

        for y in range(self.maze_height):
            for x in range(self.maze_width):
                x_start = (x * cell_size) + x_offset
                x_end = x_start + cell_size
                y_start = (y * cell_size) + y_offset
                y_end = y_start + cell_size
                grid_value = self.maze_grid[y][x]
                if (grid_value & 1):
                    # NORD
                    pygame.draw.line(screen, DARK_BLUE, (x_start, y_start), (x_end, y_start), width=1)
                if (grid_value & 4):
                    # SUD
                    pygame.draw.line(screen, DARK_BLUE, (x_start, y_end), (x_end, y_end), width=1)
                if (grid_value & 2):
                    # EST
                    pygame.draw.line(screen, DARK_BLUE, (x_end, y_start), (x_end, y_end), width=1)
                if (grid_value & 8):
                    # OUEST
                    pygame.draw.line(screen, DARK_BLUE, (x_start, y_start), (x_start, y_end), width=1)
        self.pacman.draw(screen, cell_size, x_offset, y_offset)
