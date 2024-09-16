import random
import time
from typing import List


class SessionManager():

    def __init__(self, project_name:str) -> None: 
        self.project_name = project_name
        self.session_id = None
        self.counter_screenshot_per_session:int = 0
        self.current_session_id:str = None
        self.previous_session_id:str = None
        self.is_session_started:bool = False
        self._elapsed_time:float = 0
        self._start_time = None
        self.session_code:str = None


    def new_session(self):
        self._start_time = None
        self._elapsed_time = 0
        if self.is_session_started:
            self.stop_session()
        self.start_session()
    
    def stop_session(self):
        self.is_session_started = False
        self.previous_session_id = self.current_session_id
        self.current_session_id = None
        self.counter_screenshot_per_session = 0
        if self._start_time is None:
            raise RuntimeError("Stopwatch is not running.")
        self._elapsed_time += time.perf_counter() - self._start_time
        self._start_time = None
    
    def start_session(self):
        try:
            self.is_session_started = True
            if self._start_time is not None:
                raise RuntimeError("Stopwatch is already running.")
            self._start_time = time.perf_counter()
            self.current_session_id = self.create_session_id()
        except Exception as e:
            print(f"Error starting session: {e}")
            raise Exception(f"Error starting session: {e}")
        
    def elapsed(self):
        if self._start_time is not None:
            return  round(self._elapsed_time + (time.perf_counter() - self._start_time), 3)
        

    def __str__(self):
        return f"{self.elapsed():.3f} seconds"
    
    def create_session_id(self):
        timestamp = int(time.time()*1000)
        milliseconds = str(timestamp)[:-3]
        random_letters:List[str] = random.choices("QWERTYUIOPASDFGHJKLZXCVBNM", k=5)
        self.session_code:str = "".join(random_letters)
        return f"{timestamp}_{milliseconds}_{self.project_name}_{self.session_code}_session"
    