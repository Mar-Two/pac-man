"""Lecture et validation du fichier de configuration du jeu."""
import json
import sys
from typing import Any


class ConfigParser:
    """Lit le fichier de configuration et valide chacune de ses valeurs.

    Une valeur manquante ou invalide est remplacée par sa valeur par
    défaut, avec un message sur stderr : le jeu démarre toujours. Le
    résultat est dans dico_game, prêt à être passé à la partie.
    """

    RULES: dict[str, tuple[type[int], int, int, int]] = {
        "lives": (int, 1, 9, 3),
        "seed": (int, 1, 2**31, 42),
        "pacgum": (int, 1, 500, 42),
        "points_per_pacgum": (int, 0, 10_000, 10),
        "points_per_super_pacgum": (int, 0, 100_000, 50),
        "points_per_ghost": (int, 0, 100_000, 200),
        "level_max_time": (int, 10, 600, 90),
    }
    LEVEL_RULES: dict[str, tuple[type[int], int, int]] = {
        "width": (int, 14, 29),
        "height": (int, 10, 29),
    }
    DEFAULT_LEVELS: list[dict[str, int]] = [
        {"width": 15, "height": 11},
        {"width": 17, "height": 13},
        {"width": 19, "height": 13},
        {"width": 21, "height": 15},
        {"width": 23, "height": 17},
        {"width": 25, "height": 17},
        {"width": 27, "height": 19},
        {"width": 23, "height": 21},
        {"width": 20, "height": 23},
        {"width": 19, "height": 25},
    ]

    def __init__(self, config_file: str) -> None:
        """Lit et valide le fichier de configuration.

        Args:
            config_file: chemin du fichier JSON (avec commentaires #).
        """
        self.config = config_file
        self.__data: dict[str, Any] = {}
        self.dico_game: dict[str, Any] = {}
        self.level_maze: list[dict[str, int]] = []
        self.read_file()
        self.data_recovery_game()
        self.data_recovery_maze()
        self.construct_level_maze()

    def read_file(self) -> None:
        """Lit le fichier, ignore les lignes # et décode le JSON.

        En cas d'erreur (fichier illisible, JSON invalide, racine qui
        n'est pas un objet), un message est affiché et les données
        restent vides : toutes les valeurs par défaut seront utilisées.
        """
        self.__data = {}
        try:
            with open(self.config, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except (OSError, UnicodeDecodeError) as e:
            print(f"Warning: cannot read '{self.config}' ({e}), "
                  "using default configuration", file=sys.stderr)
            return
        # ligne vide plutôt que supprimée : les numéros de ligne restent justes
        lines = ["\n" if line.lstrip().startswith('#') else line
                 for line in lines]
        try:
            data = json.loads(''.join(lines))
        except json.JSONDecodeError as e:
            print(f"Warning: '{self.config}' is not valid JSON (line "
                  f"{e.lineno}, column {e.colno}: {e.msg}), "
                  "using default configuration", file=sys.stderr)
            return
        if not isinstance(data, dict):
            print(f"Warning: '{self.config}' must contain a JSON object "
                  "{...}, using default configuration", file=sys.stderr)
            return
        self.__data = data

    def data_recovery_game(self) -> None:
        """Valide les clés globales et remplit dico_game.

        Une clé manquante, du mauvais type ou hors bornes prend sa valeur
        par défaut. Les clés inconnues sont ignorées.
        """
        for key, (expected, low, high, default) in self.RULES.items():
            if key not in self.__data:
                print(f"Warning: missing key '{key}', "
                      f"using default value {default}", file=sys.stderr)
                self.dico_game[key] = default
                continue
            value = self.__data[key]
            if not isinstance(value, expected) or isinstance(value, bool):
                print(f"Warning: '{key}' must be {expected.__name__}, "
                      f"got {value!r}, using default value {default}",
                      file=sys.stderr)
                self.dico_game[key] = default
            elif not low <= value <= high:
                print(f"Warning: '{key}' must be between {low} and {high}, "
                      f"got {value}, using default value {default}",
                      file=sys.stderr)
                self.dico_game[key] = default
            else:
                self.dico_game[key] = value

    def data_recovery_maze(self) -> None:
        """Valide chaque niveau de la clé 'level' et remplit level_maze.

        Un niveau invalide est ignoré. Si 'level' est absente ou n'est
        pas une liste, level_maze reste vide.
        """
        levels = self.__data.get('level')
        if levels is None:
            print("Warning: missing key 'level', using default levels",
                  file=sys.stderr)
            return
        if not isinstance(levels, list):
            print(f"Warning: 'level' must be a list, got {levels!r}, "
                  "using default levels", file=sys.stderr)
            return
        for i, level in enumerate(levels, start=1):
            if not isinstance(level, dict):
                print(f"Warning: level {i}: must be an object {{...}}, "
                      f"got {level!r}, level skipped", file=sys.stderr)
                continue
            tmp: dict[str, int] = {}
            for key, (expected, low, high) in self.LEVEL_RULES.items():
                value = level.get(key)
                if key not in level:
                    print(f"Warning: level {i}: missing key '{key}', "
                          "level skipped", file=sys.stderr)
                elif (not isinstance(value, expected)
                        or isinstance(value, bool)):
                    print(f"Warning: level {i}: '{key}' must be "
                          f"{expected.__name__}, got {value!r}, "
                          "level skipped", file=sys.stderr)
                elif not low <= value <= high:
                    print(f"Warning: level {i}: '{key}' must be between "
                          f"{low} and {high}, got {value}, level skipped",
                          file=sys.stderr)
                else:
                    tmp[key] = value
            if len(tmp) == len(self.LEVEL_RULES):
                self.level_maze.append(tmp)

    def construct_level_maze(self) -> None:
        """Construit la liste finale des niveaux dans dico_game['levels'].

        Les niveaux valides de la config viennent en premier, complétés
        par les niveaux par défaut pour en avoir au moins autant.
        """
        missing = self.DEFAULT_LEVELS[len(self.level_maze):]
        self.dico_game['levels'] = self.level_maze + [
            level.copy() for level in missing]