"""Point d'entrée du jeu : fenêtre, machine à états et boucle principale."""
from mazegenerator import MazeGenerator
import pygame

from .render import Screen
from .colors import BLACK
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from .state_machine import StateMachine
from .menus import MainMenu, PauseMenu
from .game import Game


class App:
    """Programme principal : crée la fenêtre, les états et fait tourner la boucle."""

    def __init__(self, maze: MazeGenerator) -> None:
        """Prépare l'application, sans encore ouvrir la fenêtre.

        Args:
            maze: labyrinthe généré utilisé pour la partie.
        """
        self.maze = maze

    def run(self) -> None:
        """Ouvre la fenêtre et fait tourner la boucle principale à FPS images par seconde.

        Rend la main quand la machine à états s'arrête ou que la fenêtre est fermée.
        """
        pygame.init()
        window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        screen = Screen(SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.display.set_caption("PacMan")
        clock = pygame.time.Clock()

        machine = StateMachine()
        machine.add("main_menu", MainMenu(machine))
        machine.add("game", Game(machine, self.maze))
        machine.add("pause_menu", PauseMenu(machine))
        machine.change("main_menu")

        while machine.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    machine.running = False
                else:
                    machine.handle_event(event)

            machine.update()

            screen.fill(BLACK)

            machine.draw(screen)

            screen.put_to_window(window)
            clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    maze = MazeGenerator(size=(14, 10), seed=42)
    window = App(maze)
    window.run()
    # for line in maze.maze:
    #     print(line)
