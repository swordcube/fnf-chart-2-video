import game.game
import game.sprite

from PIL import Image, ImageDraw, ImageFont

class Text(game.sprite.Sprite):
    OVERSAMPLING = 2

    def __init__(self, x: float = 0.0, y: float = 0.0, text: str = "", size: int = 16):
        super().__init__(x, y)

        self.centered = False

        self._dirty = True
        self._font = "assets/vcr.ttf"

        self._size = size
        self._fontData = ImageFont.truetype(self._font, self._size * Text.OVERSAMPLING)

        self._color = (255, 255, 255)
        self._stroke_width = 0.0
        self._stroke_color = (0, 0, 0)

        self._align = "left"

        self._text = ""
        self.set_text(text)

    def get_font(self):
        return self._font

    def set_font(self, new_font: str):
        self._dirty = True
        self._font = new_font
        self._fontData = ImageFont.truetype(self._font, self._size * Text.OVERSAMPLING)

    def get_size(self):
        return self._size

    def set_size(self, new_size: int):
        self._dirty = True
        self._size = new_size
        self._fontData = ImageFont.truetype(self._font, self._size * Text.OVERSAMPLING)

    def get_color(self):
        return self._color

    def set_color(self, new_color: tuple[int, int, int]):
        self._dirty = True
        self._color = new_color

    def get_stroke_width(self):
        return self._stroke_width

    def set_stroke_width(self, new_width: float):
        self._dirty = True
        self._stroke_width = new_width

    def get_stroke_color(self):
        return self._stroke_color

    def set_stroke_color(self, new_color: tuple[int, int, int]):
        self._dirty = True
        self._stroke_color = new_color

    def get_align(self):
        return self._align
    
    def set_align(self, new_align: str):
        self._dirty = True
        self._align = new_align

    def get_text(self):
        return self._text

    def set_text(self, new_text: str):
        self._dirty = True
        self._text = new_text
    
    def get_frame_width(self):
        if self._dirty: self._regen_img()
        return super().get_frame_width()

    def get_frame_height(self):
        if self._dirty: self._regen_img()
        return super().get_frame_height()
    
    def draw(self, game_img):
        if self._dirty: self._regen_img()
        return super().draw(game_img)

    def _regen_img(self):
        self._dirty = False
        img = Image.new("RGBA", (10000, 10000))

        draw = ImageDraw.Draw(img)
        draw.fontmode = "1"
        draw.text((0, 0), self._text, font=self._fontData, fill=self._color, spacing=0, stroke_width=self._stroke_width * 2, stroke_fill=self._stroke_color, align=self._align)

        text_window = img.getbbox()
        img = img.crop(text_window)
        img = img.resize((int(img.width / Text.OVERSAMPLING), int(img.height / Text.OVERSAMPLING)), Image.Resampling.LANCZOS)

        self.atlas = game.sparrowatlas.SparrowAtlas.from_image(img)
        self.frame = 0
        self.animation = ""