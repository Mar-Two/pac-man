"""Les fantômes du jeu : chacun choisit sa cible à sa façon."""
from .entities import Ghost, PacMan
from .render import Image


class Chaser(Ghost):
    """Chasseur : poursuit Pac-Man directement par l'arrière."""

    def choose_target(self) -> tuple[int, int]:
        """Vise la case de Pac-Man.

        Returns:
            Coordonnées (x, y) de Pac-Man.
        """
        return (self.pacman.x, self.pacman.y)


class Ambusher(Ghost):
    """Embuscade : vise devant Pac-Man pour lui couper la route."""

    AHEAD = 4   # nombre de cases visées devant Pac-Man

    def choose_target(self) -> tuple[int, int]:
        """Vise AHEAD cases devant Pac-Man, dans sa direction.

        Si Pac-Man n'a pas encore bougé, sa direction vaut (0, 0)
        et la cible est sa propre case.

        Returns:
            Coordonnées (x, y) de la case visée, peut-être hors de la
            grille : remind_target la corrige ensuite.
        """
        dx, dy = self.pacman.direction
        return (self.pacman.x + dx * self.AHEAD,
                self.pacman.y + dy * self.AHEAD)


class Pincer(Ghost):
    """Tenaille : vise le côté de Pac-Man opposé au chasseur.

    Avec le chasseur, il prend Pac-Man en étau : l'un arrive par
    derrière, l'autre par le côté opposé.
    """

    def __init__(self, pos: tuple[int, int], image: Image, pacman: PacMan,
                 chaser: Chaser) -> None:
        """Place le fantôme immobile sur une case et retient le chasseur.

        Args:
            pos: case de départ (x, y) dans la grille.
            image: sprite du fantôme, déjà agrandi à la taille du labyrinthe.
            pacman: Pac-Man, dont le fantôme lit la position.
            chaser: le chasseur, dont la position sert à calculer la cible.
        """
        super().__init__(pos, image, pacman)
        self.chaser = chaser

    def choose_target(self) -> tuple[int, int]:
        """Vise le symétrique du chasseur par rapport à Pac-Man.

        Le déplacement qui va du chasseur à Pac-Man est appliqué une
        seconde fois à partir de Pac-Man.

        Returns:
            Coordonnées (x, y) de la case visée, peut-être hors de la
            grille : remind_target la corrige ensuite.
        """
        pos_x = (self.pacman.x - self.chaser.x) + self.pacman.x
        pos_y = (self.pacman.y - self.chaser.y) + self.pacman.y
        return (pos_x, pos_y)


class Shy(Ghost):
    """Timide : poursuit Pac-Man de loin et recule quand il est proche.

    Deux seuils évitent les allers-retours : il ne recule que sous
    RETREAT_DISTANCE, et ne reprend la poursuite qu'au-delà de
    CHASE_DISTANCE. Entre les deux, il garde sa décision précédente.
    """

    CHASE_DISTANCE = 10    # plus loin que ça : reprise de la poursuite
    RETREAT_DISTANCE = 6   # plus proche que ça : retour au coin

    def __init__(self, pos: tuple[int, int], image: Image,
                 pacman: PacMan) -> None:
        """Place le fantôme immobile sur une case, en mode poursuite.

        Args:
            pos: case de départ (x, y) dans la grille, aussi son coin.
            image: sprite du fantôme, déjà agrandi à la taille du labyrinthe.
            pacman: Pac-Man, dont le fantôme lit la position.
        """
        super().__init__(pos, image, pacman)
        self.retreating = False

    def respawn(self) -> None:
        """Replace le fantôme sur sa case de départ, en mode poursuite."""
        super().respawn()
        self.retreating = False

    def choose_target(self) -> tuple[int, int]:
        """Vise Pac-Man ou le coin de départ, selon la distance.

        La distance est celle de Manhattan : écart en x plus écart en y,
        sans tenir compte des murs.

        Returns:
            Coordonnées (x, y) de Pac-Man en poursuite, ou de la case
            de départ du fantôme en retraite.
        """
        distance = (abs(self.pacman.x - self.x)
                    + abs(self.pacman.y - self.y))
        if distance < self.RETREAT_DISTANCE:
            self.retreating = True
        elif distance > self.CHASE_DISTANCE:
            self.retreating = False
        if self.retreating:
            return self.spawn_pos
        return (self.pacman.x, self.pacman.y)