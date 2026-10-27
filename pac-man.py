import sys
from parsing import ConfigParser
from game import Game


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Arguments allowed")
    config_parser = ConfigParser(sys.argv[1])
    game = Game(**config_parser.dico_game)
    print(game.levels)
