import json
import sys


class ConfigParser():
    RULES: dict[str, tuple[type, int, int, int]] = {
                        "lives": (int, 1, 9, 3),
                        "seed": (int, 1, 2**31, 42),
                        "pacgum": (int, 1, 500, 42),
                        "points_per_pacgum": (int, 0, 10_000, 10),
                        "points_per_super_pacgum": (int, 0, 100_000, 50),
                        "points_per_ghost": (int, 0, 100_000, 200),
                        "level_max_time": (int, 10, 600, 90),
                        }
    LEVEL_RULES: dict[str, tuple[type, int, int, int]] = {
                "width":  (int, 14, 60),
                "height": (int, 10, 40),
                }

    def __init__(self, config_file: str) -> None:
        self.config = config_file
        self.__data = {}
        self.dico_game = {}
        self.level_maze = []
        self.default_levels = [
            {"width": 15, "height": 11},
            {"width": 17, "height": 13},
            {"width": 19, "height": 13},
            {"width": 21, "height": 15},
            {"width": 23, "height": 17},
            {"width": 25, "height": 17},
            {"width": 27, "height": 19},
            {"width": 29, "height": 21},
            {"width": 31, "height": 23},
            {"width": 33, "height": 25}
            ]
        self.read_file()
        self.data_recovery_game()
        self.data_recovery_maze()
        self.construct_level_maze()

    def read_file(self) -> None:
        data = {}
        try:
            with open(self.config, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except (OSError, UnicodeDecodeError) as e:
            print(f"Warning: ({self.config}), {str(e)}.", file=sys.stderr)

        lines = ["\n" if line.lstrip().startswith('#') else line
                 for line in lines]
        try:
            data = json.loads(''.join(lines))
        except json.JSONDecodeError as e:
            print(f"Warning, ({self.config}), invalid JSON line {e.lineno}, "
                  f"column {e.colno}: {e.msg}.", file=sys.stderr)

        if not isinstance(data, dict):
            print(f"Warning: ({self.config}), root must be a JSON object "
                  "{...}", file=sys.stderr)
            data = {}

        self.__data = data

    def data_recovery_game(self) -> None:
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

    def construct_level_maze(self):
        if len(self.level_maze) == 0:
            self.dico_game['levels'] = self.default_levels
        elif len(self.level_maze) >= len(self.default_levels):
            self.dico_game['levels'] = self.level_maze
        else:
            i = 0
            while i < len(self.level_maze):
                self.default_levels[i] = self.level_maze[i]
                i += 1
            self.dico_game['levels'] = self.default_levels
