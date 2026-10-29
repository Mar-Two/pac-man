import pygame

from .colors import WHITE, BLUE, YELLOW, RED
from .state_machine import State, StateMachine

BUTTON_RATIO = 6
BUTTON_WIDTH = 0.4
MARGIN_Y = 0.1
GAP = 0.8
CORNER_RADIUS = 0.25
OUTLINE_WIDTH = 0.05
KEYS_INFO_HEIGHT = 0.05


class Menu(State):
    """Menu générique : un en-tête, une colonne de boutons et une barre d'info.

    Les sous-classes définissent OPTIONS, HEADER_RATIO, HEADER_WIDTH,
    on_select() et draw_header().
    """

    OPTIONS: tuple[str, ...] = ()
    HEADER_RATIO: float
    HEADER_WIDTH: float

    def __init__(self, state_machine: StateMachine) -> None:
        """Initialise le menu avec le premier bouton sélectionné.

        Args:
            state_machine: machine à états qui possède ce menu.
        """
        super().__init__(state_machine)
        self.select: int = 0

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

    def draw_header(self, screen: pygame.Surface, header: pygame.Rect) -> None:
        """Dessine l'en-tête du menu, à redéfinir.

        Args:
            screen: surface de la fenêtre sur laquelle dessiner.
            header: zone réservée à l'en-tête.
        """
        pass

    def draw(self, screen: pygame.Surface) -> None:
        """Dessine le menu en adaptant sa taille à l'écran.

        Si le contenu ne tient pas en hauteur, tout est réduit
        dans la même proportion.

        Args:
            screen: surface de la fenêtre sur laquelle dessiner.
        """
        screen_rect = screen.get_rect()
        margin_y = int(screen_rect.height * MARGIN_Y)
        keys_info_height = int(screen_rect.height * KEYS_INFO_HEIGHT)

        header_width = screen_rect.width * self.HEADER_WIDTH
        header_height = header_width / self.HEADER_RATIO
        button_width = screen_rect.width * BUTTON_WIDTH
        button_height = button_width / BUTTON_RATIO

        gap_height = button_height * GAP
        content_height = header_height + len(self.OPTIONS) * (gap_height + button_height)
        available_height = screen_rect.height - keys_info_height - 2 * margin_y
        scale = min(1, available_height / content_height)

        header = pygame.Rect(0, 0, header_width * scale, header_height * scale)
        button = pygame.Rect(0, 0, button_width * scale, button_height * scale)
        keys_info = pygame.Rect(0, 0, screen_rect.width, keys_info_height)
        gap = int(button.height * GAP)
        step_y = button.height + gap
        radius = int(button.height * CORNER_RADIUS)
        outline = max(1, int(button.height * OUTLINE_WIDTH))

        header.midtop = (screen_rect.centerx, margin_y)
        button.midtop = (screen_rect.centerx, header.bottom + gap)
        keys_info.midbottom = (screen_rect.centerx, screen_rect.height)

        self.draw_header(screen, header)
        pygame.draw.rect(screen, RED, keys_info)
        for i in range(len(self.OPTIONS)):
            button_move = button.move(0, i * step_y)
            pygame.draw.rect(screen, WHITE, button_move, border_radius=radius)
            if i == self.select:
                pygame.draw.rect(screen, BLUE, button_move, outline, border_radius=radius)


class MainMenu(Menu):
    """Menu d'accueil : jouer, voir les scores ou quitter."""

    OPTIONS = ("play", "score", "quit")
    HEADER_RATIO = 4
    HEADER_WIDTH = 0.5

    def on_select(self, option: str) -> None:
        """Lance la partie, affiche les scores ou quitte le programme.

        Args:
            option: nom du bouton validé.
        """
        if option == "play":
            self.state_machine.change("game")
        elif option == "score":
            print("'Score' from MainMenu")
        elif option == "quit":
            self.state_machine.running = False

    def draw_header(self, screen: pygame.Surface, header: pygame.Rect) -> None:
        """Dessine le logo (pour l'instant un rectangle jaune).

        Args:
            screen: surface de la fenêtre sur laquelle dessiner.
            header: zone réservée au logo.
        """
        pygame.draw.rect(screen, YELLOW, header)


class PauseMenu(Menu):
    """Menu de pause : reprendre, tricher ou retourner au menu principal."""

    OPTIONS = ("resume", "cheat", "main_menu")
    HEADER_RATIO = 4
    HEADER_WIDTH = 0.5

    def on_select(self, option: str) -> None:
        """Reprend la partie, active la triche ou retourne au menu principal.

        Args:
            option: nom du bouton validé.
        """
        if option == "resume":
            self.state_machine.change("game")
        elif option == "cheat":
            print("'cheat' from PauseMenu")
        elif option == "main_menu":
            self.state_machine.change("main_menu")

    def draw_header(self, screen: pygame.Surface, header: pygame.Rect) -> None:
        """Dessine le titre « pause » (pour l'instant un rectangle bleu).

        Args:
            screen: surface de la fenêtre sur laquelle dessiner.
            header: zone réservée au titre.
        """
        pygame.draw.rect(screen, BLUE, header)
