import math

import game.game
import game.sprite
import game.sparrowatlas

import game.fnf.note

class HoldCover(game.sprite.Sprite):
    def __init__(self, cpu: bool, x: float = 0.0, y: float = 0.0, direction: int = 0):
        super().__init__(x, y)

        self.cpu = cpu
        self.centered = True
        self.direction = direction
        
        self.x -= 92
        self.y -= 97
        
        self.atlas = game.sparrowatlas.SparrowAtlas("assets/hold_covers", 24)
        self.scaleX = self.scaleY = 1

        self.holdTimer = 0.0

        self.play(f"start {game.fnf.note.Note.DIRECTIONS[self.direction]}")

    def update(self, dt):
        super().update(dt)

        self.holdTimer -= dt * 1000.0
        if self.holdTimer <= 0.0:
            self.holdTimer = math.inf
            if self.cpu:
                self.parent.remove_child(self)
            else:
                self.splurge()

        if not self.looped and self.is_animation_finished():
            if self.animation.startswith("start"):
                self.play(f"{game.fnf.note.Note.DIRECTIONS[self.direction]}", True)
            else:
                self.parent.remove_child(self)

    def splurge(self):
        anim = f"end {game.fnf.note.Note.DIRECTIONS[self.direction]}"
        self.play(anim)
        self.set_animation_offset(anim, (-30, -30))
