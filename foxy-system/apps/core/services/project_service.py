from pathlib import Path

from core.environment import OsEnvGeneral


class ProjectService:
    def __init__(self, projects_root: str | Path | None = None):
        OsEnvGeneral.set_as_environment_variables_from_file()
        self.projects_root = Path(projects_root or "Projects")

    def list_projects(self) -> list[dict[str, str]]:
        if not self.projects_root.exists():
            return []

        projects = []
        for path in sorted(self.projects_root.iterdir(), key=lambda item: item.name.lower()):
            if path.is_dir():
                projects.append(
                    {
                        "name": path.name,
                        "path": str(path),
                    }
                )
        return projects

    def project_exists(self, project_name: str) -> bool:
        return self.get_project_path(project_name).is_dir()

    def get_project_path(self, project_name: str) -> Path:
        return self.projects_root / project_name

    def get_project_summary(self, project_name: str) -> dict[str, object]:
        project_path = self.get_project_path(project_name)
        if not project_path.is_dir():
            raise FileNotFoundError(f"Project '{project_name}' not found")

        folders = [
            {
                "name": child.name,
                "path": str(child),
            }
            for child in sorted(project_path.iterdir(), key=lambda item: item.name.lower())
            if child.is_dir()
        ]

        settings_path = project_path / OsEnvGeneral.NAME_FILE_SETTINGS.value
        return {
            "name": project_name,
            "path": str(project_path),
            "settings_file": str(settings_path) if settings_path.is_file() else None,
            "folders": folders,
        }

