import pygame

from .colors import YELLOW


class PacMan:
    """Pac-Man : avance tout seul de case en case et glisse entre deux cases.

    Sa position logique (x, y) est toujours une case entière de la grille ;
    seul l'affichage le place entre deux cases pendant un pas.
    """

    MARGIN = 0.5
    MOVE_DELAY = 10
    WALLS = {(0, -1): 1,    # nord
             (1, 0): 2,     # est
             (0, 1): 4,     # sud
             (-1, 0): 8}    # ouest

    def __init__(self, x: int, y: int) -> None:
        """Place Pac-Man immobile sur une case.

        Args:
            x: colonne de départ dans la grille.
            y: ligne de départ dans la grille.
        """
        self.x = x
        self.y = y
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.moving = (0, 0)
        self.move_timer = 0

    def can_move(self, dx: int, dy: int, grid: list[list[int]]) -> bool:
        """Indique si aucun mur ne bloque la direction depuis la case actuelle.

        Args:
            dx: direction horizontale (-1, 0 ou 1).
            dy: direction verticale (-1, 0 ou 1).
            grid: grille du labyrinthe, un entier de murs par case.

        Returns:
            True si le passage est libre, False s'il y a un mur.
        """
        wall = self.WALLS[(dx, dy)]
        if (grid[self.y][self.x] & wall) == 0:
            return True
        return False

    def choose_step(self, grid: list[list[int]]) -> None:
        """Décide de la direction du prochain pas (self.moving).

        Essaie d'abord le virage en attente, sinon continue tout droit,
        sinon s'arrête.

        Args:
            grid: grille du labyrinthe.
        """
        if self.next_direction != (0, 0):
            if self.can_move(self.next_direction[0], self.next_direction[1], grid):
                self.direction = self.next_direction
                self.moving = self.next_direction
                return
        if self.direction != (0, 0):
            if self.can_move(self.direction[0], self.direction[1], grid):
                self.moving = self.direction
                return
        self.moving = (0, 0)

    def update(self, grid: list[list[int]]) -> None:
        """Fait avancer le pas en cours, une fois par image.

        Un pas dure MOVE_DELAY images ; à la fin, Pac-Man arrive
        sur la case suivante et décide aussitôt du pas suivant.

        Args:
            grid: grille du labyrinthe.
        """
        if self.moving == (0, 0):
            self.choose_step(grid)
            return
        self.move_timer += 1
        if self.move_timer == self.MOVE_DELAY:
            self.move_timer = 0
            self.x += self.moving[0]
            self.y += self.moving[1]
            self.choose_step(grid)

    def draw(self, screen, cell_size, x_offset, y_offset) -> None:
        """Dessine Pac-Man, entre deux cases selon l'avancement du pas.

        Args:
            screen: surface de la fenêtre sur laquelle dessiner.
            cell_size: taille d'une case en pixels.
            x_offset: position horizontale du labyrinthe dans l'écran.
            y_offset: position verticale du labyrinthe dans l'écran.
        """
        progress = self.move_timer / self.MOVE_DELAY
        draw_x = self.x + self.moving[0] * progress
        draw_y = self.y + self.moving[1] * progress
        x_start = round((draw_x * cell_size) + x_offset)
        y_start = round((draw_y * cell_size) + y_offset)
        pacman = pygame.Rect(x_start, y_start, cell_size, cell_size)
        pacman.inflate_ip(-(cell_size * self.MARGIN), -(cell_size * self.MARGIN))
        pygame.draw.rect(screen, YELLOW, pacman)


# TODO: class Ghost
