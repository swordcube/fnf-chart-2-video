import random

import game.game
import game.sprite
import game.sparrowatlas

import game.fnf.conductor
import game.fnf.note

class NoteSplash(game.sprite.Sprite):
    def __init__(self, x: float = 0.0, y: float = 0.0, direction: int = 0):
        super().__init__(x, y)

        self.centered = False
        self.direction = direction
        
        self.x -= 136
        self.y -= 136
        
        self.atlas = game.sparrowatlas.SparrowAtlas("assets/splashes", 24)
        self.scaleX = self.scaleY = 1
        self.play(f"note splash {random.randint(1, 2)} {game.fnf.note.Note.DIRECTIONS[self.direction]}")

    def update(self, dt):
        super().update(dt)

        if self.frame >= len(self.atlas.frames[self.animation]) - 1:
            self.parent.remove_child(self)
