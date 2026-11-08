"""Entités qui se déplacent dans le labyrinthe : Pac-Man et les fantômes."""
import random
from abc import ABC, abstractmethod

from .render import Screen, Image


class Entity(ABC):
    """Entité du labyrinthe : avance de case en case et glisse entre deux cases.

    Sa position logique (x, y) est toujours une case entière de la grille ;
    seul l'affichage la place entre deux cases pendant un pas.
    """

    MOVE_DELAY = 12
    WALLS = {(0, -1): 1,    # nord
             (1, 0): 2,     # est
             (0, 1): 4,     # sud
             (-1, 0): 8}    # ouest

    def __init__(self, pos: tuple[int, int], image: Image) -> None:
        """Place l'entité immobile sur une case.

        Args:
            pos: case de départ (x, y) dans la grille.
            image: sprite de l'entité, déjà agrandi à la taille du labyrinthe.
        """
        self.x = pos[0]
        self.y = pos[1]
        self.spawn_pos: tuple[int, int] = pos
        self.image = image
        self.moving = (0, 0)
        self.move_timer = 0

    def respawn(self) -> None:
        """Replace l'entité immobile sur sa case de départ."""
        self.x = self.spawn_pos[0]
        self.y = self.spawn_pos[1]
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

    @abstractmethod
    def choose_step(self, grid: list[list[int]]) -> None:
        """Décide de la direction du prochain pas (self.moving), à redéfinir.

        Appelée quand l'entité est immobile ou arrive sur une case.
        Doit mettre (0, 0) dans self.moving si l'entité ne bouge pas.

        Args:
            grid: grille du labyrinthe.
        """
        pass

    def update(self, grid: list[list[int]]) -> None:
        """Fait avancer le pas en cours, une fois par image.

        Un pas dure MOVE_DELAY images ; à la fin, l'entité arrive
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

    def current_image(self) -> Image:
        """Renvoie l'image à dessiner maintenant, à redéfinir si elle change.

        Returns:
            Le sprite de l'entité.
        """
        return self.image

    def draw(self, screen: Screen, cell_size: int, x_offset: int, y_offset: int) -> None:
        """Dessine le sprite de l'entité, centré dans sa case, entre deux cases selon l'avancement du pas.

        Args:
            screen: écran (tableau de pixels) sur lequel dessiner.
            cell_size: taille d'une case en pixels.
            x_offset: position horizontale du labyrinthe dans l'écran.
            y_offset: position verticale du labyrinthe dans l'écran.
        """
        image = self.current_image()
        progress = self.move_timer / self.MOVE_DELAY
        draw_x = self.x + self.moving[0] * progress
        draw_y = self.y + self.moving[1] * progress
        x_start = round((draw_x * cell_size) + x_offset)
        y_start = round((draw_y * cell_size) + y_offset)
        # la case est plus grande que le sprite : on répartit l'espace libre autour
        padding_x = (cell_size - image.width) // 2
        padding_y = (cell_size - image.height) // 2
        screen.draw_image(image, x_start + padding_x, y_start + padding_y)


class PacMan(Entity):
    """Pac-Man : entité pilotée au clavier.

    Il continue tout droit tant qu'aucun mur ne l'arrête et prend
    le virage en attente dès que le passage est libre.
    """

    DEFAULT_DIRECTION = (1, 0)   # regarde à droite tant qu'il n'a pas bougé

    def __init__(self, pos: tuple[int, int], images: dict[tuple[int, int], Image]) -> None:
        """Place Pac-Man immobile sur une case.

        Args:
            pos: case de départ (x, y) dans la grille.
            images: un sprite par direction (dx, dy), déjà à la taille du labyrinthe.
        """
        super().__init__(pos, images[self.DEFAULT_DIRECTION])
        self.images = images
        self.direction = (0, 0)
        self.next_direction = (0, 0)

    def respawn(self) -> None:
        """Replace Pac-Man sur sa case de départ et oublie ses directions."""
        super().respawn()
        self.direction = (0, 0)
        self.next_direction = (0, 0)

    def current_image(self) -> Image:
        """Renvoie le sprite tourné vers la direction de Pac-Man.

        Garde la dernière direction quand il est arrêté contre un mur,
        et regarde à droite tant qu'il n'a jamais bougé.

        Returns:
            Le sprite correspondant à self.direction.
        """
        if self.direction == (0, 0):
            return self.image
        return self.images[self.direction]

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


class Ghost(Entity):
    """Fantôme : va de case en case vers la case choisie par l'IA."""
    MOVE_DELAY = 14

    def __init__(self, pos: tuple[int, int], image: Image, pacman: PacMan) -> None:
        """Place le fantôme immobile sur une case.

        Args:
            pos: case de départ (x, y) dans la grille.
            image: sprite du fantôme, déjà agrandi à la taille du labyrinthe.
            pacman: Pac-Man, dont le fantôme lit la position.
        """
        super().__init__(pos, image)
        self.pacman: PacMan = pacman

    def choose_step(self, grid: list[list[int]]) -> None:
        """Décide de la direction du prochain pas (self.moving).

        TEMPORAIRE : choisit au hasard une direction sans mur,
        en attendant l'IA des fantômes.

        Args:
            grid: grille du labyrinthe.
        """
        free_directions = [direction for direction in self.WALLS
                           if self.can_move(direction[0], direction[1], grid)]
        if free_directions:
            self.moving = random.choice(free_directions)
        else:
            self.moving = (0, 0)
