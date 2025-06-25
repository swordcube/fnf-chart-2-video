# my idea for this is to simulate the concept
# of a game window, but instead it's dumped onto a video

import math

import game.gameobject
import game.sprite
import game.text
import game.sparrowatlas

import game.fnf.strumline
import game.fnf.conductor
import game.fnf.timingpoint

from PIL import Image
from typing import Self

def lerp(a, b, t): return a + (b - a) * t

class Game:
    current: Self = None

    def __init__(self):
        Game.current = self

        self.chart = {}
        self.song_name = "unknown"
        self.song_mix = "default"
        self.difficulty = "normal"
        self.downscroll = False

        self.width = 1280
        self.height = 720

        self.total_time = 0.0
        self.last_total_time = 0.0
        self.tracked_dt = 0.0

        self.bg_color = (128, 128, 128, 255)
        self.children = []

        self.image_cache = {}
        self.scaled_image_cache = {}
        self.sparrow_cache = {}

        self.img: Image = None

    @staticmethod
    def beat_hit(args: tuple): 
        cur_beat = args[0]
        cur_game = Game.current
        cur_conductor: game.fnf.conductor.Conductor = game.fnf.conductor.Conductor.current

        # TODO: camera zooming
        # if cur_beat > 0.0 and math.floor(cur_beat - cur_conductor._latest_timing_point.beat) % cur_conductor._latest_timing_point.time_signature[1] == 0:
        #     cur_game.zoom += 0.03

    def create(self):
        # test = game.sprite.Sprite(30, 30)
        # test.atlas = game.sparrowatlas.SparrowAtlas("assets/notes", 24)
        # test.play("left confirm", True)
        # test.scaleX = test.scaleY = 0.7
        # self.add_child(test)

        strum_spacing = game.fnf.strumline.StrumLine.SPACING

        notes: list[dict] = self.chart["n"][self.difficulty]
        chart_meta: dict = self.chart["meta"]
        scroll_speed: float = chart_meta["game"]["scrollSpeed"][self.difficulty]

        opponent_notes = list(filter(lambda note: int(note["d"]) < 4, notes))
        opponent_notes.sort(reverse=False, key=lambda note: float(note["t"]))

        player_notes = list(filter(lambda note: int(note["d"]) > 3, notes))
        player_notes.sort(reverse=False, key=lambda note: float(note["t"]))

        conductor = game.fnf.conductor.Conductor()
        conductor.beat_hit.connect(Game.beat_hit)
        conductor.reset(chart_meta["song"]["timingPoints"][0]["b"])

        tp: list[game.fnf.timingpoint.TimingPoint] = []
        for timing_point in chart_meta["song"]["timingPoints"]:
            tp_ = game.fnf.timingpoint.TimingPoint.from_dict({
                "time": timing_point["t"],
                "bpm": timing_point["b"],
                "time_signature": timing_point["ts"]
            })
            tp.append(tp_)

        conductor.setup_timing_points(tp)
        game.fnf.conductor.Conductor.current = conductor
        self.add_child(conductor)

        self.opponent_strums = game.fnf.strumline.StrumLine(scroll_speed, (self.width * 0.25) - (strum_spacing * 2), 50, self.downscroll, opponent_notes)
        self.add_child(self.opponent_strums)

        self.player_strums = game.fnf.strumline.StrumLine(scroll_speed, (self.width * 0.75) - (strum_spacing * 2), 50, self.downscroll, player_notes)
        self.add_child(self.player_strums)

        self.song_watermark = game.text.Text(5, self.height, f"{self.song_name} [{self.song_mix.title()} - {self.difficulty.upper()}]")
        self.song_watermark.set_stroke_width(1.25)
        self.song_watermark.y -= self.song_watermark.get_current_height() + 5
        self.add_child(self.song_watermark)

        self.video_watermark = game.text.Text(self.width, self.height, "swordcube's fnf 2 video converter v0.1.0")
        self.video_watermark.set_align("right")
        self.video_watermark.set_stroke_width(1.25)
        self.video_watermark.x -= self.video_watermark.get_current_width() + 5
        self.video_watermark.y -= self.video_watermark.get_current_height() + 5
        self.add_child(self.video_watermark)

    def update(self, dt: float):
        for obj in self.children:
            obj._update(dt)

    def draw(self):
        self.img = Image.new("RGBA", (self.width, self.height), self.bg_color)

        for obj in self.children:
            obj._draw(self.img)
        
        return self.img.convert("RGB")


    def get_image(self, file_path: str):
        if not file_path in self.image_cache:
            self.image_cache[file_path] = Image.open(file_path)
        
        return self.image_cache[file_path]
    
    def get_scaled_image(self, file_path: str, width: int, height: int):
        key: str = file_path + "_" + str(width) + "x" + str(height)
        if not key in self.scaled_image_cache:
            self.scaled_image_cache[key] = self.get_image(file_path).resize((width, height), Image.Resampling.LANCZOS)
        
        return self.scaled_image_cache[key]
    
    def add_child(self, obj: game.gameobject.GameObject):
        if not obj in self.children:
            self.children.append(obj)

    def remove_child(self, obj: game.gameobject.GameObject):
        if obj in self.children:
            self.children.remove(obj)
    
    # this is all backend stuff!! (scary)

    def update_dt(self, total_time: float):
        self.last_total_time = self.total_time
        self.total_time = total_time
        self.tracked_dt = self.total_time - self.last_total_time