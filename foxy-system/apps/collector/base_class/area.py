from dataclasses import dataclass


@dataclass
class Area:
    x: int
    y: int
    w: int
    h: int

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h
        }
    
    def from_dict(self, data:dict):
        return Area(**data)
    
@dataclass
class TriggerArea(Area):
    pass

@dataclass
class ComparisonArea(Area):
    pass