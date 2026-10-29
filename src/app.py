from mazegenerator import MazeGenerator
import pygame

from .colors import BLACK
from .state_machine import StateMachine
from .menus import MainMenu, PauseMenu
from .game import Game


class App:
    """Programme principal : crée la fenêtre, les états et fait tourner la boucle."""

    def __init__(self, maze: MazeGenerator, screen_width: int = 1080, screen_height: int = 720) -> None:
        """Prépare l'application, sans encore ouvrir la fenêtre.

        Args:
            maze: labyrinthe généré utilisé pour la partie.
            screen_width: largeur de la fenêtre en pixels.
            screen_height: hauteur de la fenêtre en pixels.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.maze = maze

    def run(self) -> None:
        """Ouvre la fenêtre et fait tourner la boucle principale à 60 images par seconde.

        Rend la main quand la machine à états s'arrête ou que la fenêtre est fermée.
        """
        pygame.init()
        screen = pygame.display.set_mode((self.screen_width, self.screen_height))
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

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    maze = MazeGenerator(size=(20, 20), seed=42)
    window = App(maze, 1080, 720)
    window.run()
    # for line in maze.maze:
    #     print(line)
