"""Constantes partagées par plusieurs modules du jeu."""
import math

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 768
FPS = 60

SPRITE_SIZE = 16        # taille d'origine des sprites (pixels, carrés)
SPRITE_CELL_RATIO = 0.62  # part de la case occupée par un sprite (largeur sprite / largeur case)
HUD_PANEL_WIDTH = 200   # largeur d'un panneau HUD, un à gauche et un à droite (pixels)
MAZE_MARGIN = 16        # espace entre le labyrinthe et les panneaux / bords (pixels)

# zone disponible pour dessiner le labyrinthe (pixels)
MAZE_AREA_WIDTH = SCREEN_WIDTH - 2 * HUD_PANEL_WIDTH - 2 * MAZE_MARGIN
MAZE_AREA_HEIGHT = SCREEN_HEIGHT - 2 * MAZE_MARGIN

# plus petite case autorisée : en dessous, le sprite devrait être rétréci sous SPRITE_SIZE (pixels)
MIN_CELL_SIZE = math.ceil(SPRITE_SIZE / SPRITE_CELL_RATIO)

ASSETS_DIR = "assets"
MENU_DIR = f"{ASSETS_DIR}/menu"
GHOSTS_DIR = f"{ASSETS_DIR}/ghosts"
PACMAN_DIR = f"{ASSETS_DIR}/pacman"   # dossiers pacman-right, pacman-left, pacman-up, pacman-down
