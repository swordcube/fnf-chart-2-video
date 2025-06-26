import math
import json

import game.game
import game.sprite
import game.sparrowatlas
import game.fnf.conductor

class Character(game.sprite.Sprite):
    def __init__(self, x: float = 0.0, y: float = 0.0, name: str = "bf-scs"):
        self.character_data = json.load(open(f'assets/characters/{name}/config.json', 'r'))

        super().__init__(x + self.character_data['position'][0] or 0.0, y + self.character_data['position'][1] or 0.0)

        self.name = name
        self.atlas = game.sparrowatlas.SparrowAtlas(f"assets/characters/{name}/sprite", 24)
        self.anims = {} # {name: "blah", "xOffset": 0, "yOffset": 0"}

        for anim in self.character_data['animations']:
            anim_data = self.character_data['animations'][anim]
            self.anims[anim] = {
                'prefix': anim_data['prefix'],
                'fps': anim_data['fps'],
                'x': anim_data['offset'][0],
                'y': anim_data['offset'][1]
            }
        
        self.sing_timer = 0.0
        self.play(self.anims['idle']['prefix'])

        self.centered = False
        self.scaleX = self.scaleY = self.character_data["scale"]

        cur_conductor = game.fnf.conductor.Conductor.current
        cur_conductor.beat_hit.connect(lambda args: self.beat_hit(args[0]))
    
    def update(self, dt):
        super().update(dt)

        self.sing_timer -= dt
    
    def sing(self, direction: int = 0, prefix: str = ""):
        self.sing_timer = 0.5

        anim = self.anims.get(f'sing{["LEFT", "DOWN", "UP", "RIGHT"][direction]}{prefix}', None)
        if anim:
            self.play(anim['prefix'])
            self.atlas.fps = anim['fps']
            self.set_animation_offset(anim['prefix'], (-anim['x'], -anim['y']))
    
    def beat_hit(self, beat: int):
        if self.sing_timer < 0 and self.is_animation_finished():
            self.play(self.anims.get("idle")['prefix'])
            self.atlas.fps = self.anims.get("idle")['fps']
            self.set_animation_offset("idle", (-self.anims['idle']['x'], -self.anims['idle']['y']))