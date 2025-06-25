import game.game

from PIL import Image
from typing import Self

class GameObject:
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y
        self.parent = None

        self.children = []
        self._children_to_remove = []

    def get_parent_x(self) -> float:
        x: float = 0.0
        parent: Self = self.parent

        while parent:
            x += parent.x
            parent = parent.parent

        return x
    
    def get_parent_y(self) -> float:
        y: float = 0.0
        parent: Self = self.parent

        while parent:
            y += parent.y
            parent = parent.parent

        return y

    def get_global_x(self) -> float:
        return self.get_parent_x() + self.x
    
    def get_global_y(self) -> float:
        return self.get_parent_y() + self.y

    def set_global_x(self, x: float):
        self.x = x - self.get_parent_x()

    def set_global_y(self, y: float):
        self.y = y - self.get_parent_y()

    def add_child(self, obj: Self):
        if not obj in self.children:
            obj.parent = self
            self.children.append(obj)

    def remove_child(self, obj: Self):
        if obj in self.children:
            obj.parent = None
            self._children_to_remove.append(obj)
    
    def _update(self, dt: float):
        for child in self.children:
            child._update(dt)

        self.update(dt)

        for obj in self._children_to_remove:
            self.children.remove(obj)

        self._children_to_remove.clear()

    def update(self, dt: float):
        pass

    def _draw(self, raw_img: Image):
        for child in self.children:
            child._draw(raw_img)
        
        self.draw(raw_img)

    def draw(self, raw_img: Image):
        pass