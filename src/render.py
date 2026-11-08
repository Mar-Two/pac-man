"""Couche d'affichage : seul module autorisé à utiliser pygame pour dessiner."""
import pygame


class Image:
    """Image chargée depuis un fichier, prête à être dessinée sur un Screen.

    Garde ses pixels en RGB et, pour chaque ligne, les morceaux
    non transparents (spans) à recopier.
    """

    def __init__(self, path: str, size: tuple[int, int] | None = None) -> None:
        """Charge une image et la redimensionne si besoin.

        Args:
            path: chemin du fichier image (PNG).
            size: taille voulue (largeur, hauteur) en pixels,
                ou None pour garder la taille d'origine.
        """
        surface = pygame.image.load(path)
        self.width = surface.get_width()
        self.height = surface.get_height()
        self.bytes_per_pixel = 4
        self.pixels = pygame.image.tobytes(surface, "RGBA")
        self.rgb_pixels = pygame.image.tobytes(surface, "RGB")
        if size is not None and size != (self.width, self.height):
            # redimensionner AVANT de changer width / height : _resize_pixels lit la taille d'origine
            self.pixels = self._resize_pixels(self.pixels, 4, size[0], size[1])
            self.rgb_pixels = self._resize_pixels(self.rgb_pixels, 3, size[0], size[1])
            self.width = size[0]
            self.height = size[1]
        self.spans = []
        for y in range(self.height):
            row_spans = []
            start = None
            for x in range(self.width):
                alpha = self.pixels[(y * self.width + x) * self.bytes_per_pixel + 3]
                if alpha != 0 and start is None:
                    start = x
                elif alpha == 0 and start is not None:
                    row_spans.append((start, x))
                    start = None
            if start is not None:
                row_spans.append((start, self.width))
            self.spans.append(row_spans)

    def _resize_pixels(self, pixels: bytes, bytes_per_pixel: int,
                       new_width: int, new_height: int) -> bytes:
        """Redimensionne des pixels au plus proche voisin, à n'importe quelle taille.

        Chaque pixel de la nouvelle image recopie le pixel d'origine
        qui tombe au même endroit, en proportion.
        Utilise self.width et self.height, qui doivent encore être
        la taille d'origine au moment de l'appel.

        Args:
            pixels: pixels de l'image, rangés ligne par ligne.
            bytes_per_pixel: nombre d'octets par pixel (3 en RGB, 4 en RGBA).
            new_width: largeur voulue en pixels.
            new_height: hauteur voulue en pixels.

        Returns:
            Pixels de l'image redimensionnée, de taille new_width x new_height.
        """
        resized = bytearray()
        for new_y in range(new_height):
            y = new_y * self.height // new_height
            row = bytearray()
            for new_x in range(new_width):
                x = new_x * self.width // new_width
                start = (y * self.width + x) * bytes_per_pixel
                row += pixels[start:start + bytes_per_pixel]
            resized += row
        return bytes(resized)


class Screen:
    """Image de la taille de la fenêtre, sur laquelle tout le jeu dessine.

    Les pixels sont rangés ligne par ligne dans un bytearray, 3 octets
    (R, G, B) par pixel. On dessine dedans, puis put_to_window()
    l'affiche, comme une image MLX (mlx_new_image).
    """

    def __init__(self, width: int, height: int) -> None:
        """Crée un écran entièrement noir.

        Args:
            width: largeur en pixels.
            height: hauteur en pixels.
        """
        self.width = width
        self.height = height
        self.bytes_per_pixel = 3
        self.pixel_array = bytearray((width * height) * self.bytes_per_pixel)

    def fill(self, color: tuple[int, int, int]) -> None:
        """Remplit tout l'écran d'une couleur.

        Args:
            color: couleur (R, G, B).
        """
        pixel = bytes(color)
        self.pixel_array[:] = pixel * (self.width * self.height)

    def put_to_window(self, window: pygame.Surface) -> None:
        """Affiche l'écran dans la fenêtre (équivalent de mlx_put_image_to_window).

        Args:
            window: fenêtre pygame renvoyée par pygame.display.set_mode().
        """
        image = pygame.image.frombuffer(self.pixel_array, (self.width, self.height), "RGB")
        window.blit(image, (0, 0))
        pygame.display.flip()

    def draw_rect(self, x: int, y: int, width: int, height: int, color: tuple[int, int, int]) -> None:
        """Dessine un rectangle plein.

        La partie qui sort de l'écran est coupée ; un rectangle
        entièrement hors de l'écran n'est pas dessiné.

        Args:
            x: bord gauche, en pixels.
            y: bord haut, en pixels.
            width: largeur en pixels.
            height: hauteur en pixels.
            color: couleur (R, G, B).
        """
        left = max(0, x)
        right = min(x + width, self.width)
        top = max(0, y)
        bottom = min(y + height, self.height)
        if left >= right or top >= bottom:
            return
        pixel = bytes(color)
        for row in range(top, bottom):
            start = (row * self.width + left) * self.bytes_per_pixel
            end = start + (right - left) * self.bytes_per_pixel
            self.pixel_array[start:end] = pixel * (right - left)

    def draw_line(self, start: tuple[float, float], end: tuple[float, float], color: tuple[int, int, int]) -> None:
        """Dessine une ligne d'1 pixel, horizontale ou verticale.

        Les coordonnées sont arrondies au pixel le plus proche
        et les deux extrémités sont incluses.

        Args:
            start: point de départ (x, y).
            end: point d'arrivée (x, y).
            color: couleur (R, G, B).

        Raises:
            ValueError: si la ligne n'est ni horizontale ni verticale.
        """
        x_start = round(start[0])
        y_start = round(start[1])
        x_end = round(end[0])
        y_end = round(end[1])
        if y_start == y_end:
            self.draw_rect(min(x_start, x_end), y_start, abs(x_end - x_start) + 1, 1, color)
        elif x_start == x_end:
            self.draw_rect(x_start, min(y_start, y_end), 1, abs(y_end - y_start) + 1, color)
        else:
            raise ValueError("diagonal line not supported.")

    def draw_image(self, image: Image, x: int, y: int) -> None:
        """Recopie une image sur l'écran, sans ses pixels transparents.

        Seuls les morceaux non transparents de chaque ligne (image.spans)
        sont recopiés. La partie qui sort de l'écran est coupée.

        Args:
            image: image à dessiner.
            x: bord gauche de l'image, en pixels.
            y: bord haut de l'image, en pixels.
        """
        for row in range(image.height):
            if y + row < 0 or y + row >= self.height:
                continue
            for start, end in image.spans[row]:
                start = max(start, -x)
                end = min(end, self.width - x)
                if start >= end:
                    continue
                src = (row * image.width + start) * self.bytes_per_pixel
                dst = ((y + row) * self.width + (x + start)) * self.bytes_per_pixel
                length = (end - start) * self.bytes_per_pixel
                self.pixel_array[dst:dst + length] = image.rgb_pixels[src:src + length]
