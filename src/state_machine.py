from abc import ABC, abstractmethod

import pygame


class State(ABC):
    """Écran du jeu (menu, partie...) géré par une StateMachine.

    Chaque état reçoit les événements, se met à jour et se dessine
    uniquement quand il est l'état courant de la machine.
    """

    def __init__(self, state_machine: "StateMachine") -> None:
        """Initialise l'état.

        Args:
            state_machine: machine à états qui possède cet état,
                utilisée pour changer d'état ou quitter le programme.
        """
        self.state_machine = state_machine

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Traite un événement pygame (touche pressée, relâchée...).

        Args:
            event: événement reçu par la boucle principale.
        """
        pass

    def on_enter(self) -> None:
        """Appelée quand la machine passe sur cet état."""
        pass

    def on_exit(self) -> None:
        """Appelée quand la machine quitte cet état."""
        pass

    def update(self) -> None:
        """Met à jour la logique de l'état, une fois par image."""
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Dessine l'état sur l'écran, une fois par image.

        Args:
            screen: surface de la fenêtre sur laquelle dessiner.
        """
        pass


class StateMachine:
    """Gère les états du jeu et transmet tout à l'état courant."""

    def __init__(self) -> None:
        """Crée une machine vide, sans état courant, en cours d'exécution."""
        self.states: dict[str, State] = {}
        self.current_state: State | None = None
        self.running: bool = True

    def add(self, state_name: str, state: State) -> None:
        """Enregistre un état sous un nom.

        Args:
            state_name: nom utilisé ensuite avec change().
            state: état à enregistrer.
        """
        self.states[state_name] = state

    def change(self, state_name: str) -> None:
        """Passe à un autre état.

        Appelle on_exit() de l'état courant puis on_enter() du nouvel état.

        Args:
            state_name: nom de l'état, tel que donné à add().
        """
        if self.current_state is not None:
            self.current_state.on_exit()
        self.current_state = self.states[state_name]
        self.current_state.on_enter()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Transmet un événement à l'état courant.

        Args:
            event: événement reçu par la boucle principale.
        """
        if self.current_state is not None:
            self.current_state.handle_event(event)

    def update(self) -> None:
        """Met à jour l'état courant."""
        if self.current_state is not None:
            self.current_state.update()

    def draw(self, screen: pygame.Surface) -> None:
        """Dessine l'état courant.

        Args:
            screen: surface de la fenêtre sur laquelle dessiner.
        """
        if self.current_state is not None:
            self.current_state.draw(screen)
