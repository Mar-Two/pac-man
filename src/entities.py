"""Entités qui se déplacent dans le labyrinthe : Pac-Man et les fantômes."""
import random
from abc import ABC, abstractmethod
from collections import deque
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
    # ordre des images pendant un pas (indices dans la liste) : 1 → 2 → 3 → 2, puis on recommence à 1
    ANIMATION = (0, 1, 2, 1)

    def __init__(self, pos: tuple[int, int], images: dict[tuple[int, int], list[Image]]) -> None:
        """Place Pac-Man immobile sur une case.

        Args:
            pos: case de départ (x, y) dans la grille.
            images: pour chaque direction (dx, dy), ses images d'animation,
                déjà à la taille du labyrinthe.
        """
        super().__init__(pos, images[self.DEFAULT_DIRECTION][0])
        self.images = images
        self.direction = (0, 0)
        self.next_direction = (0, 0)

    def respawn(self) -> None:
        """Replace Pac-Man sur sa case de départ et oublie ses directions."""
        super().respawn()
        self.direction = (0, 0)
        self.next_direction = (0, 0)

    def current_image(self) -> Image:
        """Renvoie l'image d'animation tournée vers la direction de Pac-Man.

        L'image suit l'avancement du pas en cours (move_timer) : la bouche
        s'ouvre et se ferme une fois par case. À l'arrêt, move_timer vaut 0,
        donc il garde la première image. Il garde aussi la dernière direction
        contre un mur, et regarde à droite tant qu'il n'a jamais bougé.

        Returns:
            L'image correspondant à self.direction et au moment du pas.
        """
        if self.direction == (0, 0):
            return self.image
        step = self.move_timer * len(self.ANIMATION) // self.MOVE_DELAY
        return self.images[self.direction][self.ANIMATION[step]]

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
    """Fantôme : va de case en case vers la case choisie par l'IA.

    Classe abstraite : chaque sous-classe définit seulement sa cible
    (choose_target). Le reste (correction de la cible, plus court
    chemin, choix du pas) est commun à tous les fantômes.
    """

    MOVE_DELAY = 16
    CLOSED_CELL = 15

    def __init__(self, pos: tuple[int, int], image: Image,
                 pacman: PacMan) -> None:
        """Place le fantôme immobile sur une case.

        Args:
            pos: case de départ (x, y) dans la grille.
            image: sprite du fantôme, déjà agrandi à la taille du labyrinthe.
            pacman: Pac-Man, dont le fantôme lit la position.
        """
        super().__init__(pos, image)
        self.pacman: PacMan = pacman

    @abstractmethod
    def choose_target(self) -> tuple[int, int]:
        """Renvoie la case visée par le fantôme, à redéfinir.

        La case peut être hors de la grille ou fermée :
        remind_target la corrige ensuite.

        Returns:
            Coordonnées (x, y) de la case visée.
        """

    def remind_target(self, target: tuple[int, int],
                      grid: list[list[int]]) -> tuple[int, int]:
        """Transforme une cible brute en case accessible du labyrinthe.

        La cible est d'abord ramenée dans la grille. Si elle tombe sur
        une case fermée (le motif « 42 »), on prend la case libre
        la plus proche.

        Args:
            target: case (x, y) choisie par choose_target, peut-être invalide.
            grid: grille du labyrinthe, un entier de murs par case.

        Returns:
            Une case (x, y) dans la grille et non fermée.
        """
        height = len(grid)
        width = len(grid[0])
        x, y = target
        x = max(0, min(x, width - 1))
        y = max(0, min(y, height - 1))
        if grid[y][x] != self.CLOSED_CELL:
            return (x, y)
        for distance in range(1, max(width, height)):
            for dy in range(-distance, distance + 1):
                for dx in range(-distance, distance + 1):
                    nx = x + dx
                    ny = y + dy
                    if (0 <= nx < width and 0 <= ny < height
                            and grid[ny][nx] != self.CLOSED_CELL):
                        return (nx, ny)
        return (self.pacman.x, self.pacman.y)

    @staticmethod
    def is_valid_cell(x: int, y: int, width: int, height: int) -> bool:
        """Indique si une case est dans la grille.

        Args:
            x: colonne de la case.
            y: ligne de la case.
            width: largeur de la grille (nombre de colonnes).
            height: hauteur de la grille (nombre de lignes).

        Returns:
            True si la case existe dans la grille, False sinon.
        """
        return (0 <= x < width) and (0 <= y < height)

    def is_open(self, x: int, y: int,
                grid: list[list[int]]) -> list[tuple[int, int]]:
        """Liste les cases voisines accessibles depuis une case.

        Une voisine est accessible si elle est dans la grille et
        qu'aucun mur ne sépare les deux cases.

        Args:
            x: colonne de la case de départ.
            y: ligne de la case de départ.
            grid: grille du labyrinthe.

        Returns:
            Les cases voisines (x, y) atteignables en un pas.
        """
        result: list[tuple[int, int]] = []
        w = len(grid[0])
        h = len(grid)
        for k, v in self.WALLS.items():
            dx, dy = k
            if (self.is_valid_cell(x + dx, y + dy, w, h)
                    and not grid[y][x] & v):
                result.append((x + dx, y + dy))
        return result

    def path_target(self, grid: list[list[int]],
                    target: tuple[int, int]) -> list[tuple[int, int]]:
        """Cherche le plus court chemin du fantôme jusqu'à la cible (BFS).

        Args:
            grid: grille du labyrinthe.
            target: case (x, y) à atteindre.

        Returns:
            Les cases du chemin, de la case du fantôme à la cible
            incluses ; une liste vide si la cible est inaccessible.
        """
        start = (self.x, self.y)
        queue: deque[tuple[int, int]] = deque([start])
        previous: dict[tuple[int, int], tuple[int, int] | None] = {
            start: None}
        while queue:
            current = queue.popleft()
            if current == target:
                break
            x, y = current
            for cell in self.is_open(x, y, grid):
                if cell not in previous:
                    previous[cell] = current
                    queue.append(cell)
        if target not in previous:
            return []
        res: list[tuple[int, int]] = []
        end = target
        parent = previous[end]
        while parent is not None:
            res.append(end)
            end = parent
            parent = previous[end]
        res.append(end)
        return res[::-1]

    def choose_step(self, grid: list[list[int]]) -> None:
        """Décide de la direction du prochain pas (self.moving).

        Le fantôme suit le premier pas du plus court chemin vers sa
        cible. Sans chemin, il prend une direction libre au hasard ;
        déjà sur sa cible, il reste immobile.

        Args:
            grid: grille du labyrinthe.
        """
        target = self.choose_target()
        target = self.remind_target(target, grid)
        path = self.path_target(grid, target)

        if not path:
            free_directions = [direction for direction in self.WALLS
                               if self.can_move(direction[0], direction[1],
                                                grid)]
            if free_directions:
                self.moving = random.choice(free_directions)
            else:
                self.moving = (0, 0)
        elif len(path) == 1:
            self.moving = (0, 0)
        else:
            self.moving = (path[1][0] - self.x, path[1][1] - self.y)