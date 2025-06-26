import math

import game.game
import game.gameobject
import game.sparrowatlas

from PIL import Image

class Sprite(game.gameobject.GameObject):
    def __init__(self, x: float = 0.0, y: float = 0.0):
        super().__init__(x, y)

        self.atlas: game.sparrowatlas.SparrowAtlas = None
        self.frame = 0
        self.animation = ""
        self.looped = False
        self.centered = True

        self.scaleX = 1.0
        self.scaleY = 1.0
        
        self._frame_timer = 0.0
        self._animation_offsets = {}

    def get_frame_width(self) -> float:
        if not self.atlas: return 0.0
        
        key = self.animation
        if len(key) == 0:
            key = list(self.atlas.frames.keys())[0]

        frames = self.atlas.frames[key]
        if not frames: return 0.0
        return frames[self.frame].width
    
    def get_frame_height(self) -> float:
        if not self.atlas: return 0.0
        
        key = self.animation
        if len(key) == 0:
            key = list(self.atlas.frames.keys())[0]

        frames = self.atlas.frames[key]
        if not frames: return 0.0
        return frames[self.frame].height
    
    def get_current_width(self) -> float:
        return self.get_frame_width() * self.scaleX
    
    def get_current_height(self) -> float:
        return self.get_frame_height() * self.scaleY

    def set_animation_offset(self, animation: str, offset: tuple[float, float]):
        self._animation_offsets[animation] = offset

    def play(self, animation: str, looped: bool = False):
        self.frame = 0
        self.animation = animation
        self.looped = looped

    def update(self, dt: float):
        if not self.atlas:
            return
        
        if self.atlas.fps > 0.0:
            frame_time = 1.0 / self.atlas.fps
            self._frame_timer += dt

            while self._frame_timer >= frame_time:
                self.frame += 1
                total_frames = len(self.atlas.frames[self.animation]) 

                if self.frame >= total_frames:
                    if self.looped:
                        self.frame = 0
                    else:
                        self.frame = total_frames - 1

                self._frame_timer -= frame_time
    
    def is_animation_finished(self) -> bool:
        if not self.atlas: return True

        key = self.animation
        if len(key) == 0:
            key = list(self.atlas.frames.keys())[0]

        total_frames = len(self.atlas.frames[key]) 
        return self.frame >= total_frames - 1

    def draw(self, game_img: Image):
        if abs(self.scaleX) <= 0.001 or abs(self.scaleY) <= 0.001:
            return

        key = self.animation
        if len(key) == 0:
            key = list(self.atlas.frames.keys())[0]
        
        frames = self.atlas.frames[key]
        if not frames:
            return
        
        frame: game.sparrowatlas.SparrowFrame = frames[self.frame]
        scaled_img: Image = self.atlas.img
        
        is_scaled: bool = self.scaleX != 1.0 or self.scaleY != 1.0
        if is_scaled:
            scaled_img = game.game.Game.current.get_scaled_image(self.atlas.img.filename, math.floor(self.atlas.img.width * self.scaleX), math.floor(self.atlas.img.height * self.scaleY))
        
        anim_offset = self._animation_offsets[key] if key in self._animation_offsets else (0, 0)
        dest_x = self.get_global_x() + (anim_offset[0] * self.scaleX)
        dest_y = self.get_global_y() + (anim_offset[1] * self.scaleY)

        if self.centered:
            first_frame: game.sparrowatlas.SparrowFrame = frames[0]
            dest_x -= (first_frame.width * abs(self.scaleY)) / 2
            dest_y -= (first_frame.height * abs(self.scaleY)) / 2

        frame_x = int(frame.x * abs(self.scaleX))
        frame_y = int(frame.y * abs(self.scaleY))
        frame_width = int(frame.width * abs(self.scaleX))
        frame_height = int(frame.height * abs(self.scaleY))

        if self.scaleX < 0.0:
            frame_x = int((self.atlas.img.width - frame.x - frame.width) * abs(self.scaleX))

        if self.scaleY < 0.0:
            frame_y = int((self.atlas.img.height - frame.y - frame.height) * abs(self.scaleY))
        
        left = frame_x + frame_width
        top = frame_y + frame_height

        game_img.alpha_composite(
            scaled_img,
            (
                int(dest_x + (frame.offsetX * self.scaleX)), int(dest_y + (frame.offsetY * self.scaleY)),
            ),
            (
                frame_x, frame_y,
                left, top
            )
        )