from fastapi import APIRouter, HTTPException

from core.services.project_service import ProjectService


router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_service() -> ProjectService:
    return ProjectService()


@router.get("")
def list_projects() -> dict[str, object]:
    service = get_project_service()
    projects = service.list_projects()
    return {
        "total": len(projects),
        "projects": projects,
    }


@router.get("/{project_name}")
def get_project(project_name: str) -> dict[str, object]:
    service = get_project_service()
    try:
        return service.get_project_summary(project_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

