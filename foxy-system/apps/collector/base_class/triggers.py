from dataclasses import dataclass
from cv2.typing import MatLike
from PIL import Image

@dataclass
class TriggerImage:
    name: str
    path_image: str
    threshold_trigger_image: float # 0 to 100 %
    image:MatLike = None
    
    @property
    def get_size(self) -> tuple[int,int]:
        with Image.open(self.path_image) as img:
            return img.size
        
@dataclass
class StartSessionTriggerImage(TriggerImage):
    pass

@dataclass
class EndSessionTriggerImage(TriggerImage):
    pass


