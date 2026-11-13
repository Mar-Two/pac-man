# TO DO — Pac-Man

État au 2026-11-13, comparé au sujet (`pacman_subject.pdf`).

## Déjà fait

- [x] Rendu compatible MLX (`src/render.py`) : fenêtre 1280x768, place pour le HUD sur les côtés, sprites redimensionnés à la main
- [x] Machine à états, menu principal et menu pause (navigation au clavier)
- [x] Pac-Man : déplacements flèches / WASD, virage mis en attente, animation selon la direction
- [x] Fantômes : plus court chemin (BFS) vers une cible, `Chaser` (vise Pac-Man) et `Ambusher` (vise 3 cases devant lui)

## Gameplay

- [ ] Finir `Pincer` (pas de types, `choose_target` renvoie `None` → crash)
- [ ] Mettre les **4 fantômes** dans `Game` (seulement 2 pour l'instant)
- [ ] Mode fuite des fantômes quand ils sont mangeables
- [ ] Pac-gums dans la plupart des couloirs (`assets/other/dot.png`)
- [ ] Super-pac-gums dans les 4 coins
- [ ] Collision Pac-Man / fantôme : perte d'une vie (3 vies) puis retour au centre (`respawn()` existe déjà)
- [ ] Fantômes mangeables pendant un temps limité (`blue_ghost.png`)
- [ ] Fantôme mangé : réapparaît dans son coin après 5 à 10 s
- [ ] Score : +X pac-gum, +Y super-pac-gum, +Z fantôme (valeurs de la config), ne descend jamais
- [ ] Niveau gagné quand tous les pac-gums sont mangés
- [ ] Au moins 10 niveaux : le 1er avec une seed fixe, les suivants aléatoires
- [ ] Garder le score et les vies d'un niveau à l'autre
- [ ] Limite de temps par niveau (90 s), choisir ce qui se passe quand elle est atteinte
- [ ] Game over (plus de vies) et victoire (tous les niveaux finis)

## Interface

- [ ] HUD toujours visible : score, vies, niveau, temps restant (texte compatible MLX à trouver)
- [ ] Écran Game Over avec le score final
- [ ] Écran Victoire avec le score final et un message de félicitations
- [ ] Saisie du nom après la partie, puis retour au menu principal
- [ ] Écran Highscores (top 10), pour l'instant le bouton ne fait qu'un `print`
- [ ] Écran Instructions (contrôles et règles), pour l'instant le bouton ne fait qu'un `print`

## Mode triche

- [ ] Brancher le bouton du menu pause (il ne fait qu'un `print`)
- [ ] Invincibilité
- [ ] Passer le niveau
- [ ] Geler les fantômes
- [ ] Vies en plus
- [ ] Vitesse augmentée

## Config, robustesse, highscores

- [ ] Lancement avec `python3 pac-man.py config.json` : exactement un argument, message clair sinon
- [ ] Brancher le parser sur le jeu (`src/app.py` code en dur `MazeGenerator(size=(14, 10), seed=42)`)
- [ ] Config : commentaires `#`, valeurs ramenées dans les limites avec un message, clés inconnues ignorées, jamais de traceback
- [ ] Accorder les limites du parser avec le rendu : le parser accepte jusqu'à 60x40, le rendu s'arrête à 32x28 (min 14x10). Le niveau par défaut en 33x25 planterait
- [ ] Gérer proprement les erreurs du générateur de maze
- [ ] Highscores : chargés au démarrage, sauvegardés à la fin, top 10
- [ ] Highscores : noms de 10 caractères max (lettres, chiffres, espaces), scores entiers ≥ 0
- [ ] Highscores : ne pas planter si le fichier manque ou est invalide
- [ ] Aucun crash : chargement des images, `raise ValueError` dans `Game`

## Qualité du code

- [ ] flake8 : 66 erreurs dans `src/` (surtout des lignes trop longues)
- [ ] mypy : 3 erreurs (`Pincer` sans types, `self.ghosts: list[Chaser]` → `list[Ghost]`)
- [ ] Makefile : `install`, `run`, `debug`, `clean`, `lint` (+ `lint-strict` en option)
- [ ] Docstrings dans `parsing.py`
- [ ] Tests pytest (recommandés, pas notés)

## Livrables

- [ ] README en anglais : première ligne en italique (*This project has been created as part of the 42 curriculum by ...*)
- [ ] Sections du README : Description, Instructions, Resources (avec l'usage de l'IA), Configuration, Highscore, Maze Generation, Implementation, General Software Architecture, Project Management
- [ ] Dossier de gestion de projet : planning, suivi, répartition des tâches, risques, plan de tests, problèmes rencontrés
- [ ] Packaging + build privée / non listée sur itch.io
- [ ] Script / spec de build à la racine du repo, instructions dans le package

## Ordre conseillé

1. Finir `Pincer` et mettre les 4 fantômes
2. Pac-gums + score
3. Collisions + vies
4. HUD
5. Niveaux + limite de temps
6. Écrans de fin + saisie du nom + highscores
