import sys

from src.app import App
from src.parsing import ConfigParser


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Config files missing.")
        sys.exit(1)
    elif len(sys.argv) > 2:
        print("One config files is allowed.")
        sys.exit(1)
    config = ConfigParser(sys.argv[1])
    window = App(config.dico_game)
    window.run()
