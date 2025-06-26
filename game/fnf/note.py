import game.fnf.conductor
import game.game
import game.sparrowatlas
import game.sprite

import game.fnf.strumline
import game.fnf.notesplash

class Note(game.sprite.Sprite):
    DIRECTIONS = ["left", "down", "up", "right"]

    def __init__(self, strumline, x: float = 0.0, y: float = 0.0, time: float = 0.0, direction: int = 0, length: float = 0.0, is_sustain_note: bool = False, is_end_piece: bool = False):
        super().__init__(x, y)

        self.strumline: game.fnf.strumline.StrumLine = strumline
        self.time = time
        self.direction = direction
        self.length = length
        self.is_sustain_note = is_sustain_note
        self.is_end_piece = is_end_piece
        self.was_hit = False
        self.step_length = 0.0
        
        self.atlas = game.sparrowatlas.SparrowAtlas("assets/notes", 24)
        self.scaleX = self.scaleY = 0.7

        if self.is_sustain_note:
            if not self.is_end_piece:
                cur_conductor = game.fnf.conductor.Conductor.current
                self.step_length = cur_conductor.get_step_length()

                cur_game = game.game.Game.current
                song_pos = cur_game.total_time * 1000.0
                
                self.scaleY = max((self.step_length / self.get_frame_height()) * 0.7 * self.strumline.scroll_speed, 0.0)
            
            self.x -= 16 # stupid hardcoded value, i don't care!
            self.play(f"{Note.DIRECTIONS[self.direction]} {"tail" if self.is_end_piece else "hold"}", True)
        else:
            self.play(f"{Note.DIRECTIONS[self.direction]} scroll", True)

    def update(self, dt):
        super().update(dt)

        cur_game = game.game.Game.current
        song_pos = cur_game.total_time * 1000.0

        strum = self.strumline.strums.children[self.direction]
        scroll_mult = -1.0 if self.strumline.downscroll else 1.0

        self.y = (self.time - song_pos) * self.strumline.scroll_speed * 0.45 * scroll_mult

        if cur_game.smooth_sustains:
            if self.is_sustain_note:
                sexo = max(0.45 * (song_pos - self.time), 0.0)
                self.y += sexo * scroll_mult * self.strumline.scroll_speed

                if not self.is_end_piece:
                    shit = (self.step_length / 100) * 1.05
                    self.scaleY = max(shit - (sexo / self.get_frame_height()), 0.0) * self.strumline.scroll_speed
                else:
                    shit = (self.get_frame_height() - (sexo * self.strumline.scroll_speed))
                    if shit >= self.get_frame_height():
                        shit = self.get_frame_height()
                    
                    self.scaleY = max((shit / self.get_frame_height()) * 0.7, 0.0)
        
        if self.is_sustain_note and scroll_mult < 0.0:
            self.y -= abs(self.get_current_height())
            if self.is_end_piece and self.scaleY > 0.0:
                self.scaleY = -self.scaleY

        if self.time <= song_pos and not self.was_hit:
            self.was_hit = True
            strum.confirm()

            if not cur_game.smooth_sustains or not self.is_sustain_note:
                self.strumline.notes.remove_child(self)

            if not self.strumline.cpu and not self.is_sustain_note:
                splash = game.fnf.notesplash.NoteSplash(strum.x, strum.y, self.direction)
                self.strumline.splashes.add_child(splash)
        
        if self.time <= song_pos - ((350 / self.strumline.scroll_speed) + self.step_length) and self.was_hit:
            self.strumline.notes.remove_child(self)

