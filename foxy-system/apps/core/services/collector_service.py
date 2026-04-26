import sys
import shutil
from pathlib import Path
from typing import BinaryIO

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
                "screen_resolution": config.get(ConfigSections.PROJECT.value, {}).get(
                    "screen_resolution",
                    Resolution.FOUR_K.name,
                ),
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
