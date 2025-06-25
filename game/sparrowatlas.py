import game.game
import os

from PIL import Image
from typing import Self

import xml.etree.ElementTree as XMLElementTree

# NOTE: doesn't support rotated frames!
class SparrowFrame:
    def __init__(self, x: float, y: float, offsetX: float, offsetY: float, width: float, height: float, frame_id: int):
        self.x = x
        self.y = y
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.width = width
        self.height = height
        self.frame_id = frame_id

class SparrowAtlas:
    def __init__(self, atlas_path: str, fps: int):
        self.img = game.game.Game.current.get_image(atlas_path + ".png") if len(atlas_path) > 0 else None
        self.fps = fps
        self.frames = {}

        # if no path is specified, then we are
        # manually doin this shit
        if len(atlas_path) > 0:
            xml = XMLElementTree.parse(open(atlas_path + ".xml"))
            xml_root = xml.getroot()

            for item in xml_root.findall("SubTexture"):
                raw_name = str(item.get("name"))

                name = raw_name[0:len(raw_name) - 4]
                frame_id = int(raw_name[len(raw_name) - 4:])

                if not name in self.frames:
                    self.frames[name] = []

                self.frames[name].append(SparrowFrame(
                    float(item.get("x")),
                    float(item.get("y")),
                    -float(item.get("frameX") if item.get("frameX") != None else 0),
                    -float(item.get("frameY") if item.get("frameY") != None else 0),
                    float(item.get("width")),
                    float(item.get("height")),
                    frame_id
                ))
            
            for key in self.frames.keys():
                frames: list[SparrowFrame] = self.frames[key]
                frames.sort(reverse=False, key=lambda x: x.frame_id)
    
    @staticmethod
    def from_image(img: Image):
        atlas = SparrowAtlas("", 0)
        atlas.img = img
        atlas.frames["img"] = [SparrowFrame(0, 0, 0, 0, img.width, img.height, 0)]
        return atlas