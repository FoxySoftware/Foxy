from typing import Union
import cv2
import numpy as np
from cv2.typing import MatLike
from base_class.area_ocr_model import AreaOcrModel
from PIL import Image, ImageChops
class AreasOcr():

    @staticmethod    
    def listed_green_box_in_image(image, rectangles_map_list:list[dict[str,int|np.ndarray]]) -> MatLike:
        """
        dict[str,int|np.ndarray] = {"number":number_area, "rect_area": cv2.contourArea()}

        Label the green box in the image with the index of the box, adding a white background behind the text
        that is smaller than the assigned area.
        """
        for dict_area_rect in rectangles_map_list:
            rect = dict_area_rect["rect_area"]
            x, y, w, h = cv2.boundingRect(rect)
            
            # Define the text
            text = str(dict_area_rect["number"])
            
            # Calculate the size of the text box
            text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 3)
            text_w, text_h = text_size
            
            # Define the position for the background rectangle
            text_x = (x + w // 2) - (text_w // 2)
            text_y = (y + h // 2) + (text_h // 2)
            
            # Define background rectangle dimensions with padding
            padding = 10
            background_x1 = text_x - padding
            background_y1 = text_y - text_h - padding
            background_x2 = text_x + text_w + padding
            background_y2 = text_y + padding
            
            # Ensure the rectangle is within the assigned area
            background_x1 = max(x, background_x1)
            background_y1 = max(y, background_y1)
            background_x2 = min(x + w, background_x2)
            background_y2 = min(y + h, background_y2)
            
            cv2.rectangle(image, (background_x1 -2, background_y1-2), (background_x2+2, background_y2+2), (0, 0, 0), -1)

            # Draw the white background rectangle
            cv2.rectangle(image, (background_x1, background_y1), (background_x2, background_y2), (255, 255, 255), -1)
            
            # Add the text on top of the white background
            cv2.putText(image, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            
        return image

    @staticmethod
    def save_image( image, file_name_path:str)-> bool:
        return cv2.imwrite(file_name_path, image)

    @staticmethod
    def get_list_map_areas_ocr(rectangles_map_list:list[dict[str,int|np.ndarray]]) -> list[AreaOcrModel] :
    
        list_areas = []
        """
        dict[str,int|np.ndarray] = {"number":number_area, "rect_area": cv2.contourArea()}
        Load the coordinate of the green box in the map_rectangle object """
        
        for dict_area_rect in rectangles_map_list:
            rect = dict_area_rect["rect_area"]
            x, y, w, h = cv2.boundingRect(rect)            
            number = dict_area_rect["number"]
            map_rectangle = AreaOcrModel()
            map_rectangle.key.set_value(number)
            map_rectangle.x.set_value(x)
            map_rectangle.y.set_value(y)
            map_rectangle.w.set_value(w)
            map_rectangle.h.set_value(h)
            list_areas.append(map_rectangle)

        return list_areas


    # @staticmethod
    # def identify_green_box(file_mask_path: str | None,
    #                        hsv_lower_color_area: np.ndarray,
    #                        hsv_upper_color_area: np.ndarray) -> tuple[list[dict[str, Union[int, np.ndarray]]], np.ndarray]:
    #     """Identifies green boxes in the given image based on HSV color thresholds and ignores areas smaller than 10 pixels.

    #     Args:
    #         file_mask_path (str): Path to the image file.
    #         hsv_lower_color_area (np.ndarray): Lower bound of the HSV color range.
    #         hsv_upper_color_area (np.ndarray): Upper bound of the HSV color range.

    #     Returns:
    #         Tuple[List[Dict[str, Union[int, np.ndarray]]], np.ndarray]: 
    #             - List of dictionaries where each dictionary contains:
    #                 - "number": an integer representing the area number
    #                 - "rect_area": a rectangle area in the form of a contour approximation (cv2.findContours).
    #             - The image with identified contours.
    #     """
    #     if file_mask_path is None:
    #         return [], None
        
    #     image = cv2.imread(file_mask_path)
    #     if image is None:
    #         raise ValueError(f"Image not found at path: {file_mask_path}")
        
    #     hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    #     mask = cv2.inRange(hsv, hsv_lower_color_area, hsv_upper_color_area)
    #     contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #     rectangles_map_list = []
    #     number_area = 0
    #     min_area_threshold = 100  # Minimum area threshold in pixels
        
    #     for contour in contours:
    #         if cv2.contourArea(contour) < min_area_threshold:
    #             continue
            
    #         perimeter = cv2.arcLength(contour, True)
    #         approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            
    #         if len(approx) == 4:
    #             # Calculate the convex hull to ensure the shape is closed
    #             hull = cv2.convexHull(approx)
    #             hull_area = cv2.contourArea(hull)
    #             contour_area = cv2.contourArea(approx)
                
    #             # Consider the contour only if it is fully enclosed and the areas match closely
    #             if abs(hull_area - contour_area) / hull_area < 0.05:
    #                 rectangles_map_list.append({"number": number_area, "rect_area": approx})
    #                 number_area += 1

    #     return rectangles_map_list, image

    @staticmethod
    def identify_green_box(file_mask_path: str | None,
                        hsv_lower_color_area: np.ndarray,
                        hsv_upper_color_area: np.ndarray,
                        tolerance_y: int = 20,  # Tolerancia para agrupar en filas
                        tolerance_x: int = 20   # Tolerancia para agrupar en columnas
                        ) -> tuple[list[dict[str, Union[int, np.ndarray]]], np.ndarray]:
      
        """Identifies green boxes in the given image based on HSV color thresholds and groups them by rows and columns,
        accounting for imperfect alignment.

        Args:
            file_mask_path (str): Path to the image file.
            hsv_lower_color_area (np.ndarray): Lower bound of the HSV color range.
            hsv_upper_color_area (np.ndarray): Upper bound of the HSV color range.
            tolerance_y (int): Tolerance for grouping areas into rows based on their y-coordinate proximity.
            tolerance_x (int): Tolerance for grouping areas into columns based on their x-coordinate proximity.

        Returns:
            Tuple[List[Dict[str, Union[int, np.ndarray]]], np.ndarray]: 
                - List of dictionaries where each dictionary contains:
                    - "number": an integer representing the area number.
                    - "rect_area": a rectangle area in the form of a contour approximation (cv2.findContours).
                - The image with identified contours.
        """
        if file_mask_path is None:
            return [], None
        
        image = cv2.imread(file_mask_path)
        if image is None:
            raise ValueError(f"Image not found at path: {file_mask_path}")
        
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, hsv_lower_color_area, hsv_upper_color_area)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        rectangles_map_list = []
        number_area = 0
        min_area_threshold = 100  # Minimum area threshold in pixels
        
        for contour in contours:
            if cv2.contourArea(contour) < min_area_threshold:
                continue
            
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            
            if len(approx) == 4:
                hull = cv2.convexHull(approx)
                hull_area = cv2.contourArea(hull)
                contour_area = cv2.contourArea(approx)
                
                if abs(hull_area - contour_area) / hull_area < 0.05:
                    rectangles_map_list.append({"number": number_area, "rect_area": approx})
                    number_area += 1

        bounding_boxes = [(cv2.boundingRect(r["rect_area"]), r) for r in rectangles_map_list]
        bounding_boxes.sort(key=lambda b: b[0][1])
        rows = []
        current_row = []
        for i, (bbox, rect) in enumerate(bounding_boxes):
            x, y, w, h = bbox

            if not current_row:
                current_row.append((bbox, rect))
            else:
                _, prev_y, _, prev_h = current_row[-1][0]
                if abs(y - prev_y) <= tolerance_y:
                    current_row.append((bbox, rect))
                else:
                    rows.append(current_row)
                    current_row = [(bbox, rect)]
        
        if current_row:
            rows.append(current_row)

        ordered_rectangles_map_list = []
        number_area = 0

        for row in rows:
            row.sort(key=lambda b: b[0][0])
            current_column_group = []
            columns = []

            for i, (bbox, rect) in enumerate(row):
                x, y, w, h = bbox

                if not current_column_group:
                    current_column_group.append((bbox, rect))
                else:
                    prev_x, _, prev_w, _ = current_column_group[-1][0]
                    if abs(x - prev_x) <= tolerance_x:
                        current_column_group.append((bbox, rect))
                    else:
                        columns.append(current_column_group)
                        current_column_group = [(bbox, rect)]

            if current_column_group:
                columns.append(current_column_group)

            for column_group in columns:
                for bbox, rect in column_group:
                    rect["number"] = number_area
                    ordered_rectangles_map_list.append(rect)
                    number_area += 1

        return ordered_rectangles_map_list, image
        
    
    @staticmethod
    def get_color_info_from_image(image_path: str) -> dict[str, any]:
        """"
        Return:
          hsv_lower_color:np.ndarray |
          hsv_upper_color:np.ndarray |
          hsv_color_str:str |
          rgb_color_str:str |
          hex_color_str:str |     
        """
        image: np.ndarray = cv2.imread(image_path)
       
        # Convert the image from BGR to HSV
        hsv_image: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        bgr_color: np.ndarray = image[0, 0]  # Color in BGR format
        hsv_color: np.ndarray = hsv_image[0, 0]  # Color in HSV format
        
        hue, saturation, value = hsv_color
        hue_standard: int = round(hue * 2)  # Convert from 0-179 to 0-360
        saturation_standard: int = round((saturation / 255) * 100)  # Convert from 0-255 to 0-100
        value_standard: int = round((value / 255) * 100)  # Convert from 0-255 to 0-100
        
        hsv_lower_color = hsv_color
        hsv_upper_color = hsv_color        
        hsv_color_str = f"({hue_standard}, {saturation_standard}, {value_standard})"    
        
        rgb_color_bgr: np.ndarray = cv2.cvtColor(np.uint8([[bgr_color]]), cv2.COLOR_BGR2RGB)[0, 0]
        rgb_color_standard: tuple[int, int, int] = tuple(map(int, rgb_color_bgr))  # RGB values en rango 0-255
        rgb_color_hex: str = '#{:02X}{:02X}{:02X}'.format(*rgb_color_standard)  # Hexadecimal format

        rgb_color_str = str(rgb_color_standard)
        hex_color_str = str(rgb_color_hex)
        
        return {"hsv_lower_color":hsv_lower_color,
                "hsv_upper_color":hsv_upper_color,
                "hsv_color_str":hsv_color_str,
                "rgb_color_str":rgb_color_str,
                "hex_color_str":hex_color_str      
                }
    
    def get_image(file_path:str)-> np.ndarray:
        return  cv2.imread(file_path)

    
    @staticmethod
    def get_image_resolution(image: np.ndarray) -> tuple[int, int]:
        height: int
        width: int
        height, width, _ = image.shape
        return width, height
    
    @staticmethod
    def replace_subimages_with_black_cv2(main_image, subimages):
        for subimage in subimages:
            sub_height, sub_width = subimage.shape[:2]
            
            result = cv2.matchTemplate(main_image, subimage, cv2.TM_SQDIFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if min_val < 1e-1:  
                top_left = min_loc
                bottom_right = (top_left[0] + sub_width, top_left[1] + sub_height)
                main_image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = np.zeros((sub_height, sub_width, 3), dtype=np.uint8)

        return main_image