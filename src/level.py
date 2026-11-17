"""Niveau en cours : labyrinthe, Pac-Man, fantômes et contacts."""
import pygame
from mazegenerator import MazeGenerator

from .colors import DARK_BLUE
from .constants import (GHOSTS_DIR, MAZE_AREA_HEIGHT, MAZE_AREA_WIDTH,
                        MIN_CELL_SIZE, PACMAN_DIR, SCREEN_HEIGHT,
                        SCREEN_WIDTH, SPRITE_CELL_RATIO)
from .entities import Ghost, PacMan
from .ghosts import Ambusher, Chaser, Pincer, Shy
from .render import Image, Screen
from .state_machine import State, StateMachine


class Level(State):
    """Un niveau : son labyrinthe, Pac-Man et les quatre fantômes.

    Recréé par la partie (Game) à chaque nouveau niveau. Il fait
    avancer les entités, gère les contacts et compte les vies
    restantes, que la partie relit à chaque image.
    """

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
    GHOST_SPRITES = ["pinky", "inky", "blinky", "clyde"]
    PACMAN_SPRITES = {(1, 0): "right",
                      (-1, 0): "left",
                      (0, -1): "up",
                      (0, 1): "down"}

    def __init__(self, state_machine: StateMachine, pacgum: int,
                 points_per_pacgum: int, points_per_super_pacgum: int,
                 points_per_ghost: int, level_max_time: int, lives: int,
                 maze: MazeGenerator) -> None:
        """Prépare le niveau et place les entités sur des cases libres.

        Pac-Man part près du centre, chaque fantôme près d'un coin.

        Args:
            state_machine: machine à états du jeu (pour la pause).
            pacgum: nombre de pacgums du niveau.
            points_per_pacgum: points gagnés par pacgum.
            points_per_super_pacgum: points gagnés par super-pacgum.
            points_per_ghost: points gagnés par fantôme mangé.
            level_max_time: temps maximal du niveau, en secondes.
            lives: vies restantes de Pac-Man au début du niveau.
            maze: labyrinthe généré pour ce niveau.

        Raises:
            ValueError: si le labyrinthe est trop grand pour l'écran,
                ou si aucune case n'est libre pour placer une entité.
        """
        super().__init__(state_machine)
        self.pacgum = pacgum
        self.points_per_pacgum = points_per_pacgum
        self.points_per_super_pacgum = points_per_super_pacgum
        self.points_per_ghost = points_per_ghost
        self.level_max_time = level_max_time
        self.maze = maze
        self.maze_grid = maze.maze
        self.maze_height = len(self.maze_grid)
        self.maze_width = len(self.maze_grid[0])
        self.lives = lives

        cell_size = min((MAZE_AREA_WIDTH - 1) // self.maze_width,
                        (MAZE_AREA_HEIGHT - 1) // self.maze_height)
        if cell_size < MIN_CELL_SIZE:
            raise ValueError(f"labyrinthe {self.maze_width}x"
                             f"{self.maze_height} trop grand pour l'écran")
        self.cell_size: int = cell_size

        self.sprite_size: int = int(cell_size * SPRITE_CELL_RATIO)
        self.x_offset: int = (
            SCREEN_WIDTH - self.cell_size * self.maze_width) // 2
        self.y_offset: int = (
            SCREEN_HEIGHT - self.cell_size * self.maze_height) // 2

        ghosts_pos: list[tuple[int, int]] = [
            (0, 0),
            (0, self.maze_height - 1),
            (self.maze_width - 1, 0),
            (self.maze_width - 1, self.maze_height - 1)]
        pacman_spawn = self.find_spawn((self.maze_width // 2,
                                        self.maze_height // 2))
        ghosts_spawn = [self.find_spawn(pos) for pos in ghosts_pos]

        sprite_size = (self.sprite_size, self.sprite_size)
        pacman_images = {
            direction: [Image(f"{PACMAN_DIR}-{name}/{frame}.png",
                              sprite_size)
                        for frame in (1, 2, 3)]
            for direction, name in self.PACMAN_SPRITES.items()}
        ghost_images = [Image(f"{GHOSTS_DIR}/{name}.png", sprite_size)
                        for name in self.GHOST_SPRITES]
        self.pacman = PacMan(pacman_spawn, pacman_images)
        chaser = Chaser(ghosts_spawn[0], ghost_images[0], self.pacman)
        ambusher = Ambusher(ghosts_spawn[1], ghost_images[1], self.pacman)
        pincer = Pincer(ghosts_spawn[2], ghost_images[2], self.pacman,
                        chaser)
        shy = Shy(ghosts_spawn[3], ghost_images[3], self.pacman)
        self.ghosts: list[Ghost] = [chaser, ambusher, pincer, shy]

    def on_exit(self) -> None:
        """Annule le virage en attente quand on quitte le jeu (pause, menu)."""
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
                direction = self.KEY_DIRECTIONS[event.key]
                if direction == self.pacman.next_direction:
                    self.pacman.next_direction = (0, 0)

    def respawn_all_ghosts(self) -> None:
        """Replace tous les fantômes sur leur case de départ."""
        for ghost in self.ghosts:
            ghost.respawn()

    def update(self) -> None:
        """Fait avancer Pac-Man et les fantômes, puis gère les contacts.

        Un contact avec un fantôme retire une vie et replace tout le
        monde sur sa case de départ.
        """
        self.pacman.update(self.maze_grid)
        for ghost in self.ghosts:
            ghost.update(self.maze_grid)
        for ghost in self.ghosts:
            if self.pacman.touches(ghost):
                self.lives -= 1
                self.pacman.respawn()
                self.respawn_all_ghosts()
                break

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
                    if (x < 0 or x >= self.maze_width
                            or y < 0 or y >= self.maze_height):
                        continue
                    if self.maze_grid[y][x] != self.CLOSED_CELL:
                        return (x, y)
        raise ValueError("aucune case libre pour faire spawn une entité")

    def draw(self, screen: Screen) -> None:
        """Dessine les murs, centrés dans l'écran, puis les entités.

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
                if grid_value & 1:      # nord
                    screen.draw_line((x_start, y_start), (x_end, y_start),
                                     DARK_BLUE)
                if grid_value & 4:      # sud
                    screen.draw_line((x_start, y_end), (x_end, y_end),
                                     DARK_BLUE)
                if grid_value & 2:      # est
                    screen.draw_line((x_end, y_start), (x_end, y_end),
                                     DARK_BLUE)
                if grid_value & 8:      # ouest
                    screen.draw_line((x_start, y_start), (x_start, y_end),
                                     DARK_BLUE)
        for ghost in self.ghosts:
            ghost.draw(screen, cell_size, x_offset, y_offset)
        self.pacman.draw(screen, cell_size, x_offset, y_offset)