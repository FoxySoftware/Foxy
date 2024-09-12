from enum import Enum



class SharedKeys(Enum):
    
    T1_NAME = "PROJECT"
    T2_NAME = "COLLECTOR"
    """ TABLE DATABASE NAMES ."""
    
    #
    KEYS_TO_UNPACK_IN_TX = "KEYS_TO_UNPACK_IN_TX"
    """ USED THIS TO SHARED BETWEEN Main and DataProcessor"""

    TX_THIRD_INDEX_DIMENSION = "TX_THIRD_INDEX_DIMENSION"
    """ USED THIS TO SHARED BETWEEN Main and DataProcessor"""

    """
    ScreenShotModel
    """
    KEY_SCREEN_ID = "screen_id"
    KEY_AREAS_OCR = "areas_ocr"
    KEY_COLLECTOR_DATA = "image_capture_data"
    KEY_AREA_VALUE = "value"
    KEY_AREA_RAW_VALUE = "raw_value"
    KEY_AREA_GROUP = "group"
    KEY_AREA_NAME = "name"
    KEY_AREA_NUMBER = "area_number"
    KEY_AREA_PATH_IMAGE = "path_image"
    KEY_AREA_LINK_IMAGE = "link_image"
    KEY_IMAGE_SCREENSHOT_NAME = "image_name"
    KEY_IMAGE_SCREENSHOT_LINK = "link_source_image"
    """
    ScreenShotModel: PropertyCaptureSession
    """
    KEY_SESSION_ID = "session_id"
    KEY_SESSION_CODE = "session_code"
    KEY_IS_START_SESSION = "is_start_session"
    KEY_IS_END_SESSION = "is_end_session"
    KEY_IS_CHANGE_DETECTED = "is_change_detected"
    KEY_TIMESTAMP_SECONDS = "timestamp_seconds"
    KEY_SESSION_CAPTURES_NUMBER = "session_captures_number"
    KEY_DATE = "date"
    
class PropertyCaptureSession(Enum):
    """
    ScreenShotModel: PropertyCaptureSession
    """
    KEY_SESSION_ID = "session_id"
    KEY_SESSION_CODE = "session_code"
    KEY_IS_START_SESSION = "is_start_session"
    KEY_IS_END_SESSION = "is_end_session"
    KEY_IS_CHANGE_DETECTED = "is_change_detected"
    KEY_TIMESTAMP_SECONDS = "timestamp_seconds"
    KEY_SESSION_CAPTURES_NUMBER = "session_captures_number"
    KEY_DATE = "date"
 