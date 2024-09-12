
import cv2
import time
import threading
import numpy as np
from cv2.typing import MatLike
from api.gateway.rabbitmq import RabbitMQ
from api.services.handler import Handler
from base_class.screenshot import ScreenShot
from resource_collector import text_general
from image_manager import ImageManager
from session_manager import SessionManager
from virtual_screen import VirtualScreen
from base_class.source_mode import SourceMode
from base_class.area import ComparisonArea, TriggerArea
from base_class.resolution_dataclass import Resolution
from folder_manager import FolderManager, EnvFolders
from base_class.triggers import EndSessionTriggerImage, StartSessionTriggerImage, TriggerImage
from base_class.os_env_geral import OsEnvGeneral as Env
from rich import print as rprint



class ImageCollector(VirtualScreen, SessionManager, ImageManager):

    def __init__(self, project_name, **kwargs ) -> None:
        self.project_name:str = project_name
        self.rabbit_handler:Handler = None
        self.stop_event:threading.Event = kwargs.get("stop_event",  threading.Event())
        self.pause_event:threading.Event = kwargs.get("pause_event",  threading.Event())
                
        self.current_language:str =  kwargs.get("current_language", "EN")
        self.screen_resolution:Resolution = kwargs.get("screen_resolution", Resolution.FOUR_K)
        self.current_mode:SourceMode = kwargs["current_mode"]
        self.video_source_name:str = kwargs.get("video_source_name", "")
        
        self.screen_id = VirtualScreen.__init__(self,
                               project_name=project_name,
                               screen_resolution=self.screen_resolution,
                               current_mode=self.current_mode,
                               screen_id=kwargs.get("screen_id", None))

        self.folder_manager:FolderManager = FolderManager(self.project_name, self.screen_id)
        SessionManager.__init__(self, self.project_name)
        ImageManager.__init__(self, 
                                screen_resolution=self.screen_resolution,
                                folder_manager = self.folder_manager,
                                current_mode = self.current_mode,
                                kwargs=kwargs)
        
        
        self.init_rabbit_handler()
        self.total_sub_session_int:int = None
    
    def init_rabbit_handler(self):
        if not self.screen_id:
            return
        
        rabbit_mq_instance = RabbitMQ(   queue=f"queue_collector_{self.screen_id}",
                                        host=Env.RABBITMQ_HOST.value,
                                        routing_key=f"routing_key_collector_{self.screen_id}",
                                        username=Env.RABBITMQ_USERNAME.value,
                                        password=Env.RABBITMQ_PASSSWORD.value,
                                        exchange=Env.RABBITMQ_EXCHANGE.value)
        
        self.rabbit_handler:Handler  = Handler(rabbit_mq_instance)
    
    def __notify_screen_shot(self,
                              is_start_session_trigger:bool,
                              is_end_session_trigger:bool,
                              is_change_detected:bool,
                              current_time_event:int,
                              path_screen_shot:str,
                              trigger_name:str|None = None,
                              threshold_trigger_image:float|None = None):
        
        if is_start_session_trigger:
            self.total_sub_session_int += 1
            self.total_sub_session = str(self.total_sub_session_int)
            process_name ="Main process"
            self.current_task = f"{process_name}: image start session detected."

        #MARK: Notify screen shot
        if self.current_mode == SourceMode.WEB:
            source = self.web_page
        elif self.current_mode == SourceMode.VIDEO:
            source = self.video_source_name
            
        screenshot = ScreenShot(
                        project_name= self.project_name,
                        screen_id=self.screen_id,
                        session_id=self.current_session_id,
                        session_code=self.session_code,
                        unix_timestamp=current_time_event,
                        timer_start_session=self.elapsed(),
                        path_image=path_screen_shot,
                        trigger_name=trigger_name,
                        source=source,
                        threshold_trigger_image=threshold_trigger_image,
                        counter_screenshot_per_session=self.counter_screenshot_per_session,
                        is_start_session_trigger=is_start_session_trigger,
                        is_end_session_trigger=is_end_session_trigger,
                        is_change_detected=is_change_detected,)
        
        self.__publish_screen_shot(screenshot)

    def __screen_shot_is_trigger_detected(  self,source_image:MatLike,
                                            source_image_interest_area:MatLike,
                                            trigger_image:TriggerImage,
                                            current_time_event:int,
                                            x:int,
                                            y:int,)-> bool:
        #MARK: Trigger detected
        if not self.is_session_started and not isinstance(trigger_image, StartSessionTriggerImage):
            return False
        
        if self.is_session_started and isinstance(trigger_image, StartSessionTriggerImage): 
            return False
        
        trigger_matlike = cv2.imread(trigger_image.path_image, 0)
        trigger_image.image = trigger_matlike
        threshold_trigger_image = trigger_image.threshold_trigger_image
        w, h = trigger_matlike.shape[::-1]
        similarity_threshold = threshold_trigger_image / 100.0
        
        res = cv2.matchTemplate(source_image_interest_area, trigger_matlike, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= similarity_threshold)
        loc_0 = loc[0].size
        is_match = loc_0 > 0
        shot_image:bool = is_match 

        if shot_image:
            self.draw_trigger_rectangle(source_image, x, y, w, h, loc)

            if isinstance(trigger_image, StartSessionTriggerImage):
                self.new_session()

            trigger_name = trigger_image.name
            path_screen_shot = self.save_screenshot(source_image, trigger_name, current_time_event)
            self.__notify_screen_shot(  is_start_session_trigger=isinstance(trigger_image, StartSessionTriggerImage),
                                        is_end_session_trigger=isinstance(trigger_image, EndSessionTriggerImage),
                                        is_change_detected=False,
                                        current_time_event=current_time_event,
                                        path_screen_shot=path_screen_shot,
                                        trigger_name=trigger_name,
                                        threshold_trigger_image=threshold_trigger_image)
                                                              
           
            if isinstance(trigger_image, EndSessionTriggerImage) and self.is_session_started:
                self.stop_session() 
        return shot_image

    def __screen_shot_is_change_detected(self,
                                         counter_screenshot_per_session:int,
                                         source_image,
                                         source_image_comparison_area:MatLike,
                                         previous_image_comparison_area:MatLike,
                                         comparison_area:ComparisonArea,
                                         current_time_event:int,
                                         threshold_difference:float=5.0,
                                         )-> tuple[MatLike, int]:
        #MARK: Change detected
        is_change_detected:bool = False

        if  self.is_session_started:
            if previous_image_comparison_area is not None:
                thresh = self.get_thresh_diff_images(source_image_comparison_area, previous_image_comparison_area)
                non_zero_count = cv2.countNonZero(thresh)
                total_pixels = thresh.size
                percentage_difference = (non_zero_count / total_pixels) * 100                
                if percentage_difference >= threshold_difference:
                    is_change_detected = True
                else:
                    is_change_detected = False
                previous_image_comparison_area = source_image_comparison_area 

            if is_change_detected :
                counter_screenshot_per_session += 1
                #self.draw_rectangle(source_image, comparison_area.x, comparison_area.y, comparison_area.w, comparison_area.h)
                path_screen_shot = self.save_screenshot(source_image, "change_detected", current_time_event)
                self.__notify_screen_shot(is_start_session_trigger=False,
                                          is_end_session_trigger=False,
                                          is_change_detected=True,
                                          current_time_event=current_time_event,
                                          path_screen_shot=path_screen_shot,
                                          trigger_name=None,
                                          threshold_trigger_image=threshold_difference)
        
        return previous_image_comparison_area, counter_screenshot_per_session

    def main_process(self, timer_process_seconds: float = 1e300, max_frame_diff: float = 1e300) -> tuple[str]:
        if self.current_mode not in [SourceMode.VIDEO, SourceMode.WEB]:
            raise ValueError("Invalid mode selected. Choose 'WEB' or 'VIDEO'.")

        process_name = "Main process"
        self.current_task = f"{process_name}: initialized."
        self.total_sub_session_int: int = 0

        # MARK: Capture screenshot
        interest_area: TriggerArea = self.get_indicators_trigger_area()
        comparison_area: ComparisonArea = self.get_area_of_comparison()
        previous_image_comparison_area: MatLike = None
        list_triggers: list[TriggerImage] = self.create_list_of_trigger_images()
        interest_x, interest_y, interest_w, interest_h = interest_area.x, interest_area.y, interest_area.w, interest_area.h

        def get_time():
            return time.time()

        time_start = get_time()
        time_end = time_start + timer_process_seconds

        counter_frame_sub_session_diff = 0
        count_frame = 0
        video_cap = None
        last_image_frame_not_null = None

        if self.current_mode == SourceMode.VIDEO:
            # MARK: Open video file
            video_path = self.folder_manager.get_the_recent_file_path(folder=EnvFolders.VIDEO_SOURCE, only_extension=".mp4")
            video_cap = cv2.VideoCapture(video_path)
            
            if not video_cap.isOpened():
                raise Exception("Error to open Video")
            
            ret, source_image_matlike = video_cap.read()
            last_image_frame_not_null = source_image_matlike
            current_time_event = get_time()
            total_frames = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))

        while get_time() - time_start < time_end and not self.stop_event.is_set():
            if self.pause_event.is_set():
                time.sleep(1)
                continue
            
            current_time_event = get_time()

            if self.current_mode == SourceMode.WEB:
                source_image = self.pyautogui_library.screenshot()
                source_image_matlike = cv2.cvtColor(np.array(source_image), cv2.COLOR_RGB2BGR)

                count_frame = self.calculate_fps_process(
                    current_time_event=current_time_event,
                    time_start=time_start,
                    count_frame=count_frame,
                    timer_process_seconds=timer_process_seconds
                )

            elif self.current_mode == SourceMode.VIDEO:
                ret, source_image_matlike = video_cap.read()
                current_frames = int(video_cap.get(cv2.CAP_PROP_POS_FRAMES))

                if not ret:
                    # End of video detected, trigger stop event
                    self.current_task = f"{process_name}: finished."
                    self.stop_event.set()
                    break

                count_frame = self.calculate_fps_process(
                    current_time_event=current_time_event,
                    time_start=time_start,
                    total_frames=total_frames,
                    current_frame=current_frames,
                    count_frame=count_frame,
                    timer_process_seconds=timer_process_seconds
                )

            if source_image_matlike is not None and source_image_matlike.any():
                last_image_frame_not_null = source_image_matlike

            if self.current_mode == SourceMode.WEB:
                self.current_task = f"{process_name}: snapshot n° ➔ {count_frame}."
            else:
                self.current_task = f"{process_name}: snapshot n° ➔ {count_frame} of {total_frames} aprox"

            source_image_interest_area = cv2.cvtColor(
                source_image_matlike[interest_y:interest_y + interest_h, interest_x:interest_x + interest_w],
                cv2.COLOR_BGR2GRAY
            )

            if count_frame == 1:
                self.save_screenshot(source_image_matlike, f"start_image_{self.screen_id}", current_time_event, EnvFolders.MAIN_FOLDER)

            if self.current_mode == SourceMode.WEB:
                self.current_task = f"{process_name}: processing snapshot n° ➔ {count_frame}"
            else:
                self.current_task = f"{process_name}: processing snapshot n° ➔ {count_frame} of {total_frames} aprox"

            jump = False
            # TRIGGER IMAGE DETECTION
            for trigger_image in list_triggers:
                if self.__screen_shot_is_trigger_detected(
                    source_image_matlike,
                    source_image_interest_area,
                    trigger_image,
                    current_time_event,
                    x=interest_x,
                    y=interest_y
                ):
                    self.current_task = f"{process_name}: image trigger detected."

                    if not isinstance(trigger_image, EndSessionTriggerImage):
                        previous_image_comparison_area = cv2.cvtColor(
                            source_image_matlike[comparison_area.y:comparison_area.y + comparison_area.h,
                                                comparison_area.x: comparison_area.x + comparison_area.w],
                            cv2.COLOR_BGR2GRAY
                        )
                    else:
                        counter_frame_sub_session_diff = 0

                    jump = True
                    break

            # COMPARISON AREA
            if self.is_session_started and not jump and counter_frame_sub_session_diff < max_frame_diff:
                source_image_comparison_area = cv2.cvtColor(
                    source_image_matlike[comparison_area.y:comparison_area.y + comparison_area.h,
                                        comparison_area.x: comparison_area.x + comparison_area.w],
                    cv2.COLOR_BGR2GRAY
                )

                previous_image_comparison_area, counter_frame_sub_session_diff = self.__screen_shot_is_change_detected(
                    counter_frame_sub_session_diff,
                    source_image_matlike,
                    source_image_comparison_area,
                    previous_image_comparison_area,
                    comparison_area,
                    current_time_event,
                    threshold_difference=self.threshold_difference_comparison_area_percent
                )

        if last_image_frame_not_null is not None and last_image_frame_not_null.any():
            self.save_screenshot(last_image_frame_not_null, f"end_image_{self.screen_id}", current_time_event, EnvFolders.MAIN_FOLDER)
            self.folder_manager.change_permissions(self.folder_manager.get_path(EnvFolders.MAIN_FOLDER))

        if self.current_mode == SourceMode.VIDEO:
            video_cap.release()
        
        self.current_task = f"{process_name}, finished "



            
    def calculate_fps_process(self, current_time_event: int,
                            time_start: int, 
                            count_frame: int,
                            timer_process_seconds: int,
                            total_frames: int = None,
                            current_frame: int = None,
                            process_name: str = "Main") -> int:
        
        elapsed_time = current_time_event - time_start
        total_seconds = elapsed_time
        count_frame += 1 
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        
        self.elapse_process_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        if total_seconds > 0:
            fps = count_frame / total_seconds
        else:
            fps = 0
        self.fps_process = f"{fps:.2f}"
        
        if timer_process_seconds != 1e300:
            percentage = (total_seconds / timer_process_seconds) * 100
            self.elapse_process_percent = f"{percentage:.2f}"
        elif total_frames and current_frame:
            percentage = (current_frame / total_frames) * 100  
            self.elapse_process_percent = f"{percentage:.2f}"
        else:
            self.elapse_process_percent = "Indeterminate"

        return count_frame

        
    def save_screenshot(self, image:MatLike, base_file_name:str, current_time_event:int, folder:EnvFolders = EnvFolders.CAPTURES )-> str:
        #MARK: Save screenshot
        
        if folder == EnvFolders.CAPTURES:
            if self.previous_session_id != self.current_session_id:
                self.counter_screenshot_per_session = 0
                self.previous_session_id = self.current_session_id  
            timestamp = int(current_time_event)
            self.counter_screenshot_per_session += 1    
            base_file_name:str = f"{self.session_code}_{self.counter_screenshot_per_session}_{timestamp}_{base_file_name}"
        
        file_name = f"{base_file_name}.png"
        path_image = self.folder_manager.get_file_path(folder, file_name)
        cv2.imwrite(path_image, image)
        return path_image
    
    def __publish_screen_shot(self, data_screenshot:ScreenShot):
        self.rabbit_handler.publish_data(data_screenshot.to_dict())

    def record_screen(self,
                    duration_seconds: int = 10,
                    area: TriggerArea = None,
                    desired_fps:float = 10,
                    test_mode:bool = False
                    ) -> float:
        """
        Returns str filename.
        """
        # MARK: Record screen
        folder:EnvFolders = EnvFolders.SCREEN_RECORDING
        file_extension = ".avi"
        file_name = f"{self.screen_id}{file_extension}"
        path_record = self.folder_manager.get_file_path(folder, file_name)
    
        def get_time():
            return time.perf_counter()

        capture = cv2.VideoWriter(path_record, self.fourcc, desired_fps, self.screen_resolution.value)
        time_start = get_time()
        time_end = time_start + duration_seconds

        count_frame = 0  
        if not test_mode:
            rprint(f"[white]{text_general.map[f'recording_started_{self.current_language}']}[white]")
        else:
            rprint(f"[white]Testing video recording to get the real FPS[white]")

        while get_time() < time_end:
            source_image = self.pyautogui_library.screenshot()
            frame = cv2.cvtColor(np.array(source_image), cv2.COLOR_RGB2BGR)
            if area is not None:
                x, y, w, h = area.x, area.y, area.w, area.h
                capture.write(frame[y:y+h, x:x+w])
            else:
                capture.write(frame)
            
            elapsed_time = get_time() - time_start
            count_frame += 1
            i = int(elapsed_time * 100 / duration_seconds)
            fps = count_frame / elapsed_time if elapsed_time > 0 else 0
            fps += fps / count_frame if fps > 0 else 0
            if not test_mode:
                print(f'\rRecording percent: [{i}%] FPS: {fps:.2f}', end="")
            else : 
                print(f'\rTesting percent: [{i}%] FPS: {fps:.2f}', end="")

        actual_duration = get_time() - time_start
        capture.release()
        if not test_mode:
            rprint(f"[white]{text_general.map[f'recording_finished_{self.current_language}']}[white]")
            rprint(f"[white]{text_general.map[f'duration_seconds_{self.current_language}']} {actual_duration:.2f}[white]")
            rprint(f"[white]{text_general.map[f'screen_resolution_{self.current_language}']} {self.screen_resolution.value}[white]")
            rprint(f"[white]{text_general.map[f'saving_video_{self.current_language}']} {path_record}[white]")
            rprint(f"[yellow]{text_general.map[f'video_saved_{self.current_language}']} {path_record}[yellow]")

        if not test_mode:
            self.folder_manager.change_permissions(path=path_record)
        else:
            
            self.folder_manager.delete_file(file_path=path_record)
        return round(fps,2)
