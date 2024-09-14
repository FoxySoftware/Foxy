from easyocr import Reader
from base_class.area_ocr_model import AreaType
from screenshot_model import CroppedImageArea, ScreenShotModel
import warnings
import torch

# Filter warnings 
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    message=r"You are using `torch.load` with `weights_only=False`"
)

class OcrProcessor:

    def __init__(self, **kwargs):
        self.lang_mode = kwargs.get("lang_area_model", "en")
        self.active_gpu:bool = kwargs.get("active_gpu", False)
        self.reader = Reader([self.lang_mode], gpu=self.active_gpu)
        
    
  
    def main_ocr_process(self, screenshot_model:ScreenShotModel) -> ScreenShotModel:
        cropped_images:list[CroppedImageArea] = screenshot_model.get_images_to_process()
        
        result:list[dict[str,any]] = []
        
        for  crp_img in cropped_images:

            result = self.reader.readtext(
                crp_img.image,
                output_format='dict',
                beamWidth=5,
                allowlist=crp_img.area_model.ocr_allow_list.value,
                blocklist=crp_img.area_model.ocr_block_list.value,
                text_threshold=crp_img.area_model.ocr_text_threshold.value,
                low_text=crp_img.area_model.ocr_low_text.value,
                detail=5
            )
            crp_img.area_model.path_image_cropped.set_value(crp_img.path)

            try:
                raw_text = result[0]['text']
                #confidence = result[0]['conf']
                crp_img.area_model.ocr_raw_value.set_value(raw_text)
                crp_img.area_model.normalize_space()
                if crp_img.area_model.type_final_value.value == AreaType.DECIMAL.value:
                    crp_img.area_model.change_final_value_to_decimal()
                if crp_img.area_model.type_final_value.value == AreaType.INTEGER.value:
                    crp_img.area_model.change_final_value_to_integer()
                
            except Exception as e:
                crp_img.area_model.ocr_raw_value.set_value(None)
                crp_img.area_model.final_value.set_value(None)
            
        
            
          
        return screenshot_model
       
            
if __name__ == "__main__":
    ocr = OcrProcessor()