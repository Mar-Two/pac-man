"""Partie en cours : labyrinthe, entités, contrôles et affichage."""
import pygame
from mazegenerator import MazeGenerator

from .render import Screen, Image
from .colors import DARK_BLUE
from .state_machine import State, StateMachine
from .entities import PacMan, Ghost
from .constants import (SCREEN_WIDTH, SCREEN_HEIGHT, SPRITE_CELL_RATIO, MIN_CELL_SIZE,
                        MAZE_AREA_WIDTH, MAZE_AREA_HEIGHT, GHOSTS_DIR, PACMAN_DIR)


class Game(State):
    """Partie en cours : le labyrinthe, Pac-Man et les fantômes."""

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
    GHOST_SPRITES = ["pinky", "inky", "blinky", "clyde"]   # un fantôme par coin
    PACMAN_SPRITES = {(1, 0): "right",       # direction (dx, dy) -> suffixe du dossier
                      (-1, 0): "left",
                      (0, -1): "up",
                      (0, 1): "down"}

    def __init__(self, state_machine: StateMachine, maze: MazeGenerator) -> None:
        """Prépare la partie et place les entités sur des cases libres.

        Pac-Man part près du centre, chaque fantôme près d'un coin.

        Args:
            state_machine: machine à états qui possède cette partie.
            maze: labyrinthe généré dans lequel se joue la partie.
        """
        super().__init__(state_machine)
        self.maze = maze
        self.maze_grid = maze.maze
        self.maze_height = len(self.maze_grid)
        self.maze_width = len(self.maze_grid[0])

        # case : la plus grande taille entière qui fait tenir le labyrinthe dans la zone.
        # Le "- 1" réserve le pixel du dernier mur (sud / est), dessiné sur x_end / y_end.
        cell_size = min((MAZE_AREA_WIDTH - 1) // self.maze_width,
                        (MAZE_AREA_HEIGHT - 1) // self.maze_height)
        if cell_size < MIN_CELL_SIZE:
            raise ValueError(f"labyrinthe {self.maze_width}x{self.maze_height} trop grand pour l'écran")
        self.cell_size: int = cell_size
        # sprite : une part fixe de la case
        self.sprite_size: int = int(cell_size * SPRITE_CELL_RATIO)
        self.x_offset: int = (SCREEN_WIDTH - self.cell_size * self.maze_width) // 2
        self.y_offset: int = (SCREEN_HEIGHT - self.cell_size * self.maze_height) // 2

        ghosts_pos: list[tuple[int, int]] = [(0, 0),
                                             (0, self.maze_height - 1),
                                             (self.maze_width - 1, 0),
                                             (self.maze_width - 1, self.maze_height - 1)]
        pacman_spawn: tuple[int, int] = self.find_spawn((self.maze_width // 2, self.maze_height // 2))
        ghosts_spawn: list[tuple[int, int]] = [self.find_spawn(pos) for pos in ghosts_pos]
        # images chargées une seule fois, déjà à la taille des sprites de ce labyrinthe
        sprite_size = (self.sprite_size, self.sprite_size)
        # 3 images par direction : 1 = bouche ouverte, 2 = mi-ouverte, 3 = fermée
        pacman_images = {direction: [Image(f"{PACMAN_DIR}-{name}/{frame}.png", sprite_size)
                                     for frame in (1, 2, 3)]
                         for direction, name in self.PACMAN_SPRITES.items()}
        ghost_images = [Image(f"{GHOSTS_DIR}/{name}.png", sprite_size) for name in self.GHOST_SPRITES]
        self.pacman = PacMan(pacman_spawn, pacman_images)
        self.ghosts: list[Ghost] = [Ghost(spawn_pos, image, self.pacman)
                                    for spawn_pos, image in zip(ghosts_spawn, ghost_images)]

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
        for ghost in self.ghosts:
            ghost.update(self.maze_grid)

    def find_spawn(self, pos: tuple[int, int]) -> tuple[int, int]:
        """Cherche la case libre la plus proche d'un point du labyrinthe.

        Les cases fermées (celles du « 42 ») sont ignorées.

        Args:
            pos: case (x, y) d'où part la recherche.

        Returns:
            Coordonnées (x, y) de la case trouvée, dans la grille.

        Raises:
            ValueError: si aucune case du labyrinthe n'est libre.
        """
        for distance in range(max(self.maze_width, self.maze_height)):
            for dy in range(-distance, distance + 1):
                for dx in range(-distance, distance + 1):
                    x = pos[0] + dx
                    y = pos[1] + dy
                    if x < 0 or x >= self.maze_width or y < 0 or y >= self.maze_height:
                        continue
                    if self.maze_grid[y][x] != self.CLOSED_CELL:
                        return (x, y)
        raise ValueError("aucune case libre pour faire spawn une entité")

    def draw(self, screen: Screen) -> None:
        """Dessine les murs du labyrinthe, centré dans l'écran, puis les fantômes et Pac-Man.

        Args:
            screen: écran (tableau de pixels) sur lequel dessiner.
        """
        cell_size = self.cell_size
        x_offset = self.x_offset
        y_offset = self.y_offset

        for y in range(self.maze_height):
            for x in range(self.maze_width):
                x_start = (x * cell_size) + x_offset
                x_end = x_start + cell_size
                y_start = (y * cell_size) + y_offset
                y_end = y_start + cell_size
                grid_value = self.maze_grid[y][x]
                if (grid_value & 1):
                    # NORD
                    screen.draw_line((x_start, y_start), (x_end, y_start), DARK_BLUE)
                if (grid_value & 4):
                    # SUD
                    screen.draw_line((x_start, y_end), (x_end, y_end), DARK_BLUE)
                if (grid_value & 2):
                    # EST
                    screen.draw_line((x_end, y_start), (x_end, y_end), DARK_BLUE)
                if (grid_value & 8):
                    # OUEST
                    screen.draw_line((x_start, y_start), (x_start, y_end), DARK_BLUE)
        for ghost in self.ghosts:
            ghost.draw(screen, cell_size, x_offset, y_offset)
        self.pacman.draw(screen, cell_size, x_offset, y_offset)
