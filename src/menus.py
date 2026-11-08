"""Menus du jeu (principal et pause) : en-tête, boutons et navigation au clavier."""
import pygame

from .colors import RED
from .state_machine import State, StateMachine
from .render import Screen, Image
from .constants import MENU_DIR

# tailles fixes en pixels (les largeurs viennent des images elles-mêmes)
HEADER_HEIGHT = 120
BUTTON_HEIGHT = 64
MARGIN_Y = 64
GAP = 48
KEYS_INFO_HEIGHT = 32


class Menu(State):
    """Menu générique : un en-tête, une colonne de boutons et une barre d'info.

    Les sous-classes définissent OPTIONS, HEADER_FILE et on_select().
    Les images sont lues dans MENU_DIR : HEADER_FILE pour l'en-tête,
    <option>.png et <option>_selected.png pour chaque bouton.
    """

    OPTIONS: tuple[str, ...] = ()
    HEADER_FILE: str

    def __init__(self, state_machine: StateMachine) -> None:
        """Charge les images du menu et sélectionne le premier bouton.

        Les images sont chargées une seule fois ici, et non à chaque image affichée.

        Args:
            state_machine: machine à états qui possède ce menu.
        """
        super().__init__(state_machine)
        self.select: int = 0
        self.header: Image = Image(f"{MENU_DIR}/{self.HEADER_FILE}")
        self.buttons = [Image(f"{MENU_DIR}/{option}.png") for option in self.OPTIONS]
        self.buttons_selected = [Image(f"{MENU_DIR}/{option}_selected.png") for option in self.OPTIONS]

    def on_enter(self) -> None:
        """Resélectionne le premier bouton à chaque ouverture du menu."""
        self.select = 0

    def on_select(self, option: str) -> None:
        """Action à faire quand un bouton est validé, à redéfinir.

        Args:
            option: nom du bouton validé, tiré de OPTIONS.
        """
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        """Navigue entre les boutons (haut/bas, W/S) et valide (espace, entrée).

        Args:
            event: événement reçu par la boucle principale.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.select = (self.select + 1) % len(self.OPTIONS)
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.select = (self.select - 1) % len(self.OPTIONS)
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.on_select(self.OPTIONS[self.select])

    def draw(self, screen: Screen) -> None:
        """Dessine le menu à tailles fixes, centré horizontalement.

        L'en-tête en haut, les boutons en colonne en dessous (le bouton
        sélectionné avec son image _selected) et la barre d'info en bas de l'écran.

        Args:
            screen: écran (tableau de pixels) sur lequel dessiner.
        """
        header_x = (screen.width - self.header.width) // 2
        header_y = MARGIN_Y
        first_button_y = header_y + HEADER_HEIGHT + GAP
        step_y = BUTTON_HEIGHT + GAP
        keys_info_y = screen.height - KEYS_INFO_HEIGHT
        screen.draw_image(self.header, header_x, header_y)
        screen.draw_rect(0, keys_info_y, screen.width, KEYS_INFO_HEIGHT, RED)
        for i in range(len(self.OPTIONS)):
            button_y = first_button_y + i * step_y
            image = self.buttons_selected[i] if i == self.select else self.buttons[i]
            button_x = (screen.width - image.width) // 2
            screen.draw_image(image, button_x, button_y)


class MainMenu(Menu):
    """Menu d'accueil : jouer, voir les scores, lire les instructions ou quitter."""

    OPTIONS = ("play", "scores", "instructions", "quit")
    HEADER_FILE = "header_main.png"

    def on_select(self, option: str) -> None:
        """Lance la partie, affiche les scores ou les instructions, ou quitte le programme.

        Args:
            option: nom du bouton validé.
        """
        if option == "play":
            self.state_machine.change("game")
        elif option == "scores":
            print("'Scores' from MainMenu")
        elif option == "instructions":
            print("'instructions' from MainMenu")
        elif option == "quit":
            self.state_machine.running = False


class PauseMenu(Menu):
    """Menu de pause : reprendre, tricher, retourner au menu principal ou quitter."""

    OPTIONS = ("resume", "cheat", "main_menu", "quit")
    HEADER_FILE = "header_pause.png"

    def on_select(self, option: str) -> None:
        """Reprend la partie, active la triche, retourne au menu principal ou quitte le programme.

        Args:
            option: nom du bouton validé.
        """
        if option == "resume":
            self.state_machine.change("game")
        elif option == "cheat":
            print("'cheat' from PauseMenu")
        elif option == "main_menu":
            self.state_machine.change("main_menu")
        elif option == "quit":
            self.state_machine.running = False
