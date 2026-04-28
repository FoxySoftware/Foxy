import sys
import shutil
from pathlib import Path
from typing import BinaryIO

import cv2

from core.environment import OsEnvGeneral
from core.services.project_service import ProjectService
from core.source_mode import SourceMode


APPS_DIR = Path(__file__).resolve().parents[2]
COLLECTOR_DIR = APPS_DIR / "collector"
if str(COLLECTOR_DIR) not in sys.path:
    sys.path.append(str(COLLECTOR_DIR))

from base_class.config_sections import ConfigSections
from base_class.os_env_collector_folders import EnvFolders
from base_class.resolution_dataclass import Resolution
from config_manager import ConfigManager
from folder_manager import FolderManager
from virtual_screen import VirtualScreen


class CollectorService:
    VIDEO_SOURCE_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}
    IMAGE_RESOURCE_EXTENSIONS = {".png"}
    IMAGE_RESOURCE_FOLDERS = {
        "start-session-trigger": (
            EnvFolders.START_SESSION_TRIGGER_IMAGE,
            ConfigSections.START_SESSION_TRIGGER_IMAGE,
        ),
        "end-session-trigger": (
            EnvFolders.END_SESSION_TRIGGER_IMAGE,
            ConfigSections.END_SESSION_TRIGGER_IMAGE,
        ),
        "list-trigger-images": (
            EnvFolders.LIST_TRIGGER_IMAGES,
            ConfigSections.LIST_TRIGGER_IMAGES,
        ),
        "interest-trigger-area": (
            EnvFolders.INTEREST_TRIGGER_AREA,
            ConfigSections.INTEREST_TRIGGER_AREA,
        ),
        "comparison-area": (
            EnvFolders.COMPARISON_AREA,
            ConfigSections.COMPARISON_AREA,
        ),
        "hsv-color-area": (
            EnvFolders.HSV_COLOR_AREA,
            ConfigSections.HSV_COLOR_AREA,
        ),
    }

    def __init__(self):
        OsEnvGeneral.set_as_environment_variables_from_file()
        EnvFolders.set_as_environment_variables_from_file()
        self.project_service = ProjectService(projects_root=EnvFolders.MAIN_FOLDER.value)

    def get_project_status(self, project_name: str) -> dict[str, object]:
        config = self.load_project_config(project_name)
        project_section = self._get_project_section(config, project_name)
        current_screen_id = project_section.get("screen_id") or None
        project_path = self.project_service.get_project_path(project_name)

        capture_root = project_path / EnvFolders.CAPTURES.value
        screen_sessions = []
        if capture_root.is_dir():
            screen_sessions = [
                {
                    "screen_id": path.name,
                    "path": str(path),
                    "captures": self._count_files(path, ".png"),
                }
                for path in sorted(capture_root.iterdir(), key=lambda item: item.name.lower())
                if path.is_dir()
            ]

        return {
            "project": project_name,
            "mode": project_section.get("mode"),
            "current_screen_id": current_screen_id,
            "screen_sessions": screen_sessions,
            "config": config,
        }

    def get_setup_status(self, project_name: str) -> dict[str, object]:
        config = self.load_project_config(project_name)
        project_section = self._get_project_section(config, project_name)
        mode = SourceMode._from_name(project_section["mode"])
        project_path = self.project_service.get_project_path(project_name)

        checks = {
            "project_config": self._check_project_config(project_section),
            "video_source": self._check_file_resource(
                project_path,
                EnvFolders.VIDEO_SOURCE,
                self.VIDEO_SOURCE_EXTENSIONS,
            ),
            "web_source": self._check_web_source(project_section),
            "screen_recording": self._check_file_resource(
                project_path,
                EnvFolders.SCREEN_RECORDING,
                {".avi", ".mp4"},
            ),
            "start_session_trigger": self._check_file_resource(
                project_path,
                EnvFolders.START_SESSION_TRIGGER_IMAGE,
                self.IMAGE_RESOURCE_EXTENSIONS,
            ),
            "interest_trigger_area": self._check_file_resource(
                project_path,
                EnvFolders.INTEREST_TRIGGER_AREA,
                self.IMAGE_RESOURCE_EXTENSIONS,
            ),
            "hsv_color_area": self._check_file_resource(
                project_path,
                EnvFolders.HSV_COLOR_AREA,
                self.IMAGE_RESOURCE_EXTENSIONS,
            ),
            "end_session_trigger": self._check_file_resource(
                project_path,
                EnvFolders.END_SESSION_TRIGGER_IMAGE,
                self.IMAGE_RESOURCE_EXTENSIONS,
            ),
            "list_trigger_images": self._check_file_resource(
                project_path,
                EnvFolders.LIST_TRIGGER_IMAGES,
                self.IMAGE_RESOURCE_EXTENSIONS,
            ),
            "comparison_area": self._check_file_resource(
                project_path,
                EnvFolders.COMPARISON_AREA,
                self.IMAGE_RESOURCE_EXTENSIONS,
            ),
            "screen_session": self._check_screen_session(project_section, project_path),
        }

        if mode == SourceMode.VIDEO:
            required_keys = [
                "project_config",
                "video_source",
                "start_session_trigger",
                "interest_trigger_area",
            ]
        else:
            required_keys = [
                "project_config",
                "web_source",
                "screen_recording",
                "start_session_trigger",
                "interest_trigger_area",
            ]

        optional_keys = [
            "hsv_color_area",
            "end_session_trigger",
            "list_trigger_images",
            "comparison_area",
            "screen_session",
        ]

        required = {key: checks[key] for key in required_keys}
        optional = {key: checks[key] for key in optional_keys}
        missing_required = [
            key for key, check in required.items() if not check["ready"]
        ]

        return {
            "project": project_name,
            "mode": mode.value,
            "ready_to_capture": len(missing_required) == 0,
            "missing_required": missing_required,
            "required": required,
            "optional": optional,
        }

    def list_valid_projects(
        self,
        available_languages: list[str] | None = None,
    ) -> list[str]:
        available_languages = available_languages or ["EN", "ES", "PT"]
        valid_projects = []

        for project in self.project_service.list_projects():
            project_name = project["name"]
            try:
                config = self.load_project_config(project_name)
                project_section = self._get_project_section(config, project_name)
                language = project_section.get("language")
                mode = project_section.get("mode")
                screen_resolution = project_section.get("screen_resolution")

                if language not in available_languages:
                    continue

                SourceMode._from_name(mode)
                if screen_resolution:
                    Resolution.from_string(screen_resolution)

                valid_projects.append(project_name)
            except Exception:
                continue

        return valid_projects

    def create_screen_session(
        self,
        project_name: str,
        screen_resolution: str | None = None,
    ) -> dict[str, object]:
        config = self.load_project_config(project_name)
        project_section = self._get_project_section(config, project_name)
        current_mode = SourceMode._from_name(project_section["mode"])

        resolution_name = screen_resolution or project_section.get("screen_resolution")
        resolution = Resolution.from_string(resolution_name) if resolution_name else Resolution.FOUR_K

        virtual_screen = VirtualScreen(
            project_name=project_name,
            current_mode=current_mode,
            screen_resolution=resolution,
            screen_id=None,
        )
        screen_id = virtual_screen.screen_id

        folder_manager = FolderManager(
            project_name=project_name,
            screen_id=screen_id,
            mode=current_mode,
        )

        settings_path = folder_manager.get_file_path(
            folder=EnvFolders.MAIN_FOLDER,
            file_name=OsEnvGeneral.NAME_FILE_SETTINGS.value,
        )
        config_manager = ConfigManager(settings_path)
        config_manager.update_section(
            section=ConfigSections.PROJECT.value,
            options={
                "screen_id": screen_id,
                "screen_resolution": resolution.name,
            },
        )

        return {
            "project": project_name,
            "screen_id": screen_id,
            "mode": current_mode.value,
            "screen_resolution": resolution.name,
            "path": folder_manager.get_path(EnvFolders.CAPTURES),
        }

    def save_video_source(
        self,
        project_name: str,
        file_name: str,
        file_object: BinaryIO,
    ) -> dict[str, object]:
        project_path = self.project_service.get_project_path(project_name)
        if not project_path.is_dir():
            raise FileNotFoundError(f"Project '{project_name}' not found")

        config = self.load_project_config(project_name, allow_missing_settings=True)
        if ConfigSections.PROJECT.value in config:
            self._get_project_section(config, project_name)

        safe_file_name = self._sanitize_file_name(file_name)
        extension = Path(safe_file_name).suffix.lower()
        if extension not in self.VIDEO_SOURCE_EXTENSIONS:
            allowed = ", ".join(sorted(self.VIDEO_SOURCE_EXTENSIONS))
            raise ValueError(f"Invalid video extension '{extension}'. Allowed: {allowed}")

        folder_manager = FolderManager(
            project_name=project_name,
            screen_id=None,
            mode=SourceMode.VIDEO,
        )
        destination_folder = Path(folder_manager.get_path(EnvFolders.VIDEO_SOURCE))
        destination_folder.mkdir(parents=True, exist_ok=True)
        destination_path = destination_folder / safe_file_name

        with open(destination_path, "wb") as destination:
            shutil.copyfileobj(file_object, destination, length=1024 * 1024)

        try:
            video_metadata = self._detect_video_metadata(destination_path)
        except Exception:
            destination_path.unlink(missing_ok=True)
            raise

        FolderManager.change_permissions(str(destination_path))

        settings_path = folder_manager.get_file_path(
            folder=EnvFolders.MAIN_FOLDER,
            file_name=OsEnvGeneral.NAME_FILE_SETTINGS.value,
        )
        ConfigManager(settings_path).update_section(
            section=ConfigSections.PROJECT.value,
            options={
                "language": config.get(ConfigSections.PROJECT.value, {}).get("language", "EN"),
                "name": project_name,
                "mode": SourceMode.VIDEO.value,
                "screen_id": config.get(ConfigSections.PROJECT.value, {}).get("screen_id", ""),
                "screen_resolution": video_metadata["screen_resolution"],
                "process_fps": config.get(ConfigSections.PROJECT.value, {}).get("process_fps", ""),
                "video_name": safe_file_name,
            },
        )

        return {
            "project": project_name,
            "file_name": safe_file_name,
            "path": str(destination_path),
            "folder": str(destination_folder),
            "size_bytes": destination_path.stat().st_size,
            **video_metadata,
        }

    def save_image_resource(
        self,
        project_name: str,
        resource_type: str,
        file_name: str,
        file_object: BinaryIO,
    ) -> dict[str, object]:
        project_path = self.project_service.get_project_path(project_name)
        if not project_path.is_dir():
            raise FileNotFoundError(f"Project '{project_name}' not found")

        if resource_type not in self.IMAGE_RESOURCE_FOLDERS:
            allowed = ", ".join(sorted(self.IMAGE_RESOURCE_FOLDERS))
            raise ValueError(f"Invalid collector resource '{resource_type}'. Allowed: {allowed}")

        safe_file_name = self._sanitize_file_name(file_name)
        extension = Path(safe_file_name).suffix.lower()
        if extension not in self.IMAGE_RESOURCE_EXTENSIONS:
            allowed = ", ".join(sorted(self.IMAGE_RESOURCE_EXTENSIONS))
            raise ValueError(f"Invalid image extension '{extension}'. Allowed: {allowed}")

        config = self.load_project_config(project_name, allow_missing_settings=True)
        project_section = config.get(ConfigSections.PROJECT.value, {})
        current_mode = self._get_mode_or_default(project_section)
        env_folder, config_section = self.IMAGE_RESOURCE_FOLDERS[resource_type]

        folder_manager = FolderManager(
            project_name=project_name,
            screen_id=project_section.get("screen_id") or None,
            mode=current_mode,
        )
        destination_folder = Path(folder_manager.get_path(env_folder))
        destination_folder.mkdir(parents=True, exist_ok=True)
        destination_path = destination_folder / safe_file_name

        with open(destination_path, "wb") as destination:
            shutil.copyfileobj(file_object, destination, length=1024 * 1024)

        FolderManager.change_permissions(str(destination_path))

        settings_path = folder_manager.get_file_path(
            folder=EnvFolders.MAIN_FOLDER,
            file_name=OsEnvGeneral.NAME_FILE_SETTINGS.value,
        )
        ConfigManager(settings_path).update_section(
            section=config_section.value,
            options={
                "file_name": safe_file_name,
                "path": str(destination_path),
                "folder": str(destination_folder),
            },
        )

        return {
            "project": project_name,
            "resource_type": resource_type,
            "file_name": safe_file_name,
            "path": str(destination_path),
            "folder": str(destination_folder),
            "size_bytes": destination_path.stat().st_size,
        }

    def load_project_config(
        self,
        project_name: str,
        allow_missing_settings: bool = False,
    ) -> dict[str, dict[str, str]]:
        project_path = self.project_service.get_project_path(project_name)
        if not project_path.is_dir():
            raise FileNotFoundError(f"Project '{project_name}' not found")

        settings_path = project_path / OsEnvGeneral.NAME_FILE_SETTINGS.value
        if not settings_path.is_file():
            if allow_missing_settings:
                return {}
            raise FileNotFoundError(f"Settings file not found for project '{project_name}'")

        return ConfigManager(str(settings_path)).load_ini_to_dict()

    def _get_project_section(
        self,
        config: dict[str, dict[str, str]],
        project_name: str,
    ) -> dict[str, str]:
        project_section = config.get(ConfigSections.PROJECT.value)
        if not project_section:
            raise ValueError(f"Project '{project_name}' has no PROJECT config section")

        required_fields = {"name", "mode"}
        missing_fields = required_fields - set(project_section)
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(f"Project '{project_name}' is missing config fields: {missing}")

        return project_section

    @staticmethod
    def _count_files(path: Path, extension: str) -> int:
        if not path.is_dir():
            return 0
        extension = extension.lower()
        return len(
            [
                item
                for item in path.iterdir()
                if item.is_file() and item.suffix.lower() == extension
            ]
        )

    @staticmethod
    def _sanitize_file_name(file_name: str) -> str:
        name = Path(file_name).name.strip()
        if not name:
            raise ValueError("File name is required")
        return name

    @staticmethod
    def _get_mode_or_default(project_section: dict[str, str]) -> SourceMode:
        mode = project_section.get("mode")
        if not mode:
            return SourceMode.VIDEO
        return SourceMode._from_name(mode)

    @staticmethod
    def _check_project_config(project_section: dict[str, str]) -> dict[str, object]:
        missing_fields = [
            key
            for key in ["language", "name", "mode", "screen_resolution"]
            if not project_section.get(key)
        ]
        return {
            "ready": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "details": {
                "language": project_section.get("language"),
                "name": project_section.get("name"),
                "mode": project_section.get("mode"),
                "screen_resolution": project_section.get("screen_resolution"),
            },
        }

    @staticmethod
    def _check_web_source(project_section: dict[str, str]) -> dict[str, object]:
        url = project_section.get("url")
        return {
            "ready": bool(url),
            "url": url,
        }

    @staticmethod
    def _check_file_resource(
        project_path: Path,
        folder: EnvFolders,
        extensions: set[str],
    ) -> dict[str, object]:
        folder_path = project_path / folder.value
        files = []
        if folder_path.is_dir():
            files = [
                {
                    "file_name": item.name,
                    "path": str(item),
                    "size_bytes": item.stat().st_size,
                }
                for item in sorted(folder_path.iterdir(), key=lambda file: file.name.lower())
                if item.is_file() and item.suffix.lower() in extensions
            ]

        return {
            "ready": len(files) > 0,
            "folder": str(folder_path),
            "files": files,
        }

    @staticmethod
    def _check_screen_session(
        project_section: dict[str, str],
        project_path: Path,
    ) -> dict[str, object]:
        screen_id = project_section.get("screen_id") or None
        capture_root = project_path / EnvFolders.CAPTURES.value
        screen_path = capture_root / screen_id if screen_id else None
        return {
            "ready": bool(screen_id and screen_path and screen_path.is_dir()),
            "screen_id": screen_id,
            "path": str(screen_path) if screen_path else None,
        }

    @staticmethod
    def _detect_video_metadata(video_path: Path) -> dict[str, object]:
        video = cv2.VideoCapture(str(video_path))
        try:
            if not video.isOpened():
                raise ValueError(f"Could not open video file '{video_path.name}'")

            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = float(video.get(cv2.CAP_PROP_FPS) or 0)
            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

            if width <= 0 or height <= 0:
                raise ValueError(f"Could not detect video resolution for '{video_path.name}'")

            duration_seconds = None
            if fps > 0 and frame_count > 0:
                duration_seconds = round(frame_count / fps, 3)

            return {
                "width": width,
                "height": height,
                "fps": round(fps, 3) if fps else None,
                "frame_count": frame_count if frame_count else None,
                "duration_seconds": duration_seconds,
                "screen_resolution": f"{width} x {height}",
            }
        finally:
            video.release()
