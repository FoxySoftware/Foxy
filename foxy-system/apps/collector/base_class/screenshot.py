
from dataclasses import dataclass
import json


@dataclass
class ScreenShot:
    project_name:str
    screen_id: str
    session_id: str
    session_code: str
    unix_timestamp: int
    timer_start_session:float
    path_image: str
    trigger_name: str
    source: str
    threshold_trigger_image: float
    counter_screenshot_per_session: int = 0
    is_start_session_trigger: bool = None
    is_end_session_trigger: bool = None
    is_change_detected: bool = None


    def to_dict(self):
        return {
            "project_name":self.project_name,
            "screen_id": self.screen_id,
            "session_id": self.session_id,
            "session_code": self.session_code,
            "unix_timestamp": self.unix_timestamp,
            "timer_start_session":self.timer_start_session,
            "path_image": self.path_image,
            "trigger_name": self.trigger_name,
            "source": self.source,
            "threshold_trigger_image": self.threshold_trigger_image,
            "counter_screenshot_per_session": self.counter_screenshot_per_session,
            "is_start_session_trigger": self.is_start_session_trigger,
            "is_end_session_trigger": self.is_end_session_trigger,
            "is_change_detected": self.is_change_detected,
        }

    def to_json(self):
        return json.dumps(self.to_dict())