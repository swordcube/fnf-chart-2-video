import math

import game.fnf.conductor
import game.gameobject
import game.sparrowatlas
import game.sprite
import game.fnf.note

class Strum(game.sprite.Sprite):
    def __init__(self, x: float = 0.0, y: float = 0.0, direction: int = 0):
        super().__init__(x, y)

        self.direction = direction
        directions = game.fnf.note.Note.DIRECTIONS

        self.atlas = game.sparrowatlas.SparrowAtlas("assets/notes", 24)
        self.play(f"{directions[self.direction]} static", True)
        self.scaleX = self.scaleY = 0.7

        # hardcoded offsets!! grah!!
        match self.direction:
            case 2:
                anim = f"{directions[self.direction]} confirm"
                self.set_animation_offset(anim, (-5, 0))

            case 3:
                anim = f"{directions[self.direction]} confirm"
                self.set_animation_offset(anim, (-5, 0))

        self.confirmTimer = math.inf

    def update(self, dt):
        self.confirmTimer -= dt
        if self.confirmTimer <= 0.0:
            self.confirmTimer = math.inf
            self.play(f"{game.fnf.note.Note.DIRECTIONS[self.direction]} static", True)
        
        super().update(dt)

    def confirm(self):
        self.play(f"{game.fnf.note.Note.DIRECTIONS[self.direction]} confirm", False)
        self.confirmTimer = 0.15

class StrumLine(game.gameobject.GameObject):
    SPACING = 160 * 0.7

    def __init__(self, scroll_speed:float, x: float = 0.0, y: float = 0.0, downscroll: bool = False, notes: list[dict] = []):
        super().__init__(x, y)

        self.cpu = False
        self.scroll_speed = scroll_speed
        self.downscroll = downscroll

        if self.downscroll:
            cur_game = game.game.Game.current
            self.y = cur_game.height - self.y - StrumLine.SPACING

        self.x += StrumLine.SPACING / 2.0
        self.y += StrumLine.SPACING / 2.0
        
        self.raw_notes = notes
        self.raw_note_index = 0

        self.strums = game.gameobject.GameObject()
        self.add_child(self.strums)

        for i in range(0, 4):
            strum = Strum(i * StrumLine.SPACING, 0, i)
            self.strums.add_child(strum)

        self.notes = game.gameobject.GameObject()
        self.add_child(self.notes)

        self.holdcovers = game.gameobject.GameObject()
        self.add_child(self.holdcovers)

        self.splashes = game.gameobject.GameObject()
        self.add_child(self.splashes)
    
    def update(self, dt):
        song_pos = game.game.Game.current.total_time * 1000.0

        while self.raw_note_index < len(self.raw_notes):
            raw_note = self.raw_notes[self.raw_note_index]
            if song_pos < float(raw_note["t"]) - (2500 / self.scroll_speed):
                break

            time = float(raw_note["t"])
            direction = int(raw_note["d"]) % 4
            length = float(raw_note["l"])

            # sustain
            step_length = game.fnf.conductor.Conductor.current.get_step_length()
            
            raw_sustain_pieces = math.floor(length / step_length)
            sustain_pieces = raw_sustain_pieces + 1 if raw_sustain_pieces > 0 else 0 

            for i in range(sustain_pieces):
                note = game.fnf.note.Note(self, self.strums.children[direction].x, -9999, time + (i * step_length), direction, 0, True, i >= sustain_pieces - 1)
                note.centered = False
                self.notes.add_child(note)
            
            # main note
            note = game.fnf.note.Note(self, self.strums.children[direction].x, -9999, time, direction, length)
            self.notes.add_child(note)

            self.raw_note_index += 1
        
        super().update(dt)