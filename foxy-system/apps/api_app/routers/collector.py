from pydantic import BaseModel
from fastapi import APIRouter, File, HTTPException, UploadFile

from core.services.collector_service import CollectorService


router = APIRouter(prefix="/collector", tags=["collector"])


class CreateScreenSessionRequest(BaseModel):
    screen_resolution: str | None = None


def get_collector_service() -> CollectorService:
    return CollectorService()


@router.get("/projects/{project_name}/status")
def get_project_status(project_name: str) -> dict[str, object]:
    service = get_collector_service()
    try:
        return service.get_project_status(project_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/projects/{project_name}/screen-sessions")
def create_screen_session(
    project_name: str,
    request: CreateScreenSessionRequest | None = None,
) -> dict[str, object]:
    service = get_collector_service()
    try:
        return service.create_screen_session(
            project_name=project_name,
            screen_resolution=request.screen_resolution if request else None,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/projects/{project_name}/video-source")
def upload_video_source(
    project_name: str,
    file: UploadFile = File(...),
) -> dict[str, object]:
    service = get_collector_service()
    try:
        return service.save_video_source(
            project_name=project_name,
            file_name=file.filename,
            file_object=file.file,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    finally:
        file.file.close()
