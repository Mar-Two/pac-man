"""Partie en cours : enchaînement des niveaux, vies et contrôles."""
import sys
from typing import Any

import pygame
from mazegenerator import MazeGenerator

from .level import Level
from .render import Screen
from .state_machine import State, StateMachine


class Game(State):
    """Partie en cours : garde ce qui dure toute la partie.

    Les vies et l'index du niveau restent ici d'un niveau à l'autre ;
    le labyrinthe, Pac-Man et les fantômes appartiennent au niveau en
    cours (self.level), recréé à chaque nouveau niveau.
    """

    def __init__(self, state_machine: StateMachine,
                 param_game: dict[str, Any]) -> None:
        """Prépare la partie à partir de la configuration validée.

        Aucun niveau n'est encore créé : new_game() s'en charge quand le
        joueur lance une partie.

        Args:
            state_machine: machine à états qui possède cette partie.
            param_game: configuration validée (dico_game du parsing).
        """
        super().__init__(state_machine)
        self.param_game = param_game
        self.index = 0
        self.levels: list[tuple[int, int]] = []
        self.level: Level | None = None
        self.lives: int = self.param_game["lives"]
        self.create_levels()

    def create_levels(self) -> None:
        """Remplit self.levels avec la taille (largeur, hauteur) des niveaux.

        À n'appeler qu'une fois : chaque appel ajoute tous les niveaux.
        """
        for level in self.param_game['levels']:
            self.levels.append((level['width'], level['height']))

    def load_level(self) -> bool:
        """Génère le labyrinthe du niveau self.index et crée ce niveau.

        Le premier niveau utilise la seed de la config, les suivants
        un labyrinthe aléatoire (seed=0). Si la génération ou la
        création du niveau échoue, un message est affiché et le jeu
        revient au menu principal, sans traceback.

        L'appelant doit vérifier avant que self.index désigne bien un
        niveau existant (sinon, la partie est gagnée).

        Returns:
            True si le niveau est prêt, False s'il n'a pas pu être créé.
        """
        seed = self.param_game["seed"] if self.index == 0 else 0
        try:
            maze = MazeGenerator(self.levels[self.index], seed=seed)
            self.level = Level(self.state_machine,
                               self.param_game["pacgum"],
                               self.param_game["points_per_pacgum"],
                               self.param_game["points_per_super_pacgum"],
                               self.param_game["points_per_ghost"],
                               self.param_game["level_max_time"],
                               self.lives,
                               maze)
        except Exception as e:
            print(f"Error: level {self.index + 1} could not be generated "
                  f"({type(e).__name__}: {e}), back to main menu",
                  file=sys.stderr)
            self.state_machine.change("main_menu")
            return False
        return True

    def new_game(self) -> bool:
        """Remet la partie à zéro et charge le premier niveau.

        Returns:
            True si le premier niveau est prêt, False sinon : la partie
            ne doit alors pas démarrer.
        """
        self.index = 0
        self.lives = self.param_game["lives"]
        return self.load_level()

    def on_exit(self) -> None:
        """Transmet la sortie de l'état au niveau en cours (pause, menu)."""
        assert self.level is not None
        self.level.on_exit()

    def update(self) -> None:
        """Fait avancer le niveau en cours et gère la fin de partie.

        Les vies sont recopiées depuis le niveau ; à 0, la partie est
        perdue et le jeu revient au menu principal.
        """
        assert self.level is not None
        self.level.update()
        self.lives = self.level.lives
        if self.lives <= 0:
            print("Game over", file=sys.stderr)
            self.state_machine.change("main_menu")
            return

    def draw(self, screen: Screen) -> None:
        """Dessine le niveau en cours.

        Args:
            screen: écran (tableau de pixels) sur lequel dessiner.
        """
        assert self.level is not None
        self.level.draw(screen)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Transmet un événement clavier au niveau en cours.

        Args:
            event: événement reçu par la boucle principale.
        """
        assert self.level is not None
        self.level.handle_event(event)