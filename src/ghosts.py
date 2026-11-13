"""Les fantômes du jeu : chacun choisit sa cible à sa façon."""
from .entities import Ghost


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

    AHEAD = 3

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
    def __init__(self, pos, image, pacman, chaser: Chaser):
        super().__init__(pos, image, pacman)
        self.chaser = chaser

    def choose_target(self):
        pass
