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


@router.get("/projects/{project_name}/setup-status")
def get_setup_status(project_name: str) -> dict[str, object]:
    service = get_collector_service()
    try:
        return service.get_setup_status(project_name)
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


def _upload_image_resource(
    project_name: str,
    resource_type: str,
    file: UploadFile,
) -> dict[str, object]:
    service = get_collector_service()
    try:
        return service.save_image_resource(
            project_name=project_name,
            resource_type=resource_type,
            file_name=file.filename,
            file_object=file.file,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    finally:
        file.file.close()


@router.post("/projects/{project_name}/start-session-trigger")
def upload_start_session_trigger(
    project_name: str,
    file: UploadFile = File(...),
) -> dict[str, object]:
    return _upload_image_resource(project_name, "start-session-trigger", file)


@router.post("/projects/{project_name}/end-session-trigger")
def upload_end_session_trigger(
    project_name: str,
    file: UploadFile = File(...),
) -> dict[str, object]:
    return _upload_image_resource(project_name, "end-session-trigger", file)


@router.post("/projects/{project_name}/list-trigger-images")
def upload_list_trigger_image(
    project_name: str,
    file: UploadFile = File(...),
) -> dict[str, object]:
    return _upload_image_resource(project_name, "list-trigger-images", file)


@router.post("/projects/{project_name}/interest-trigger-area")
def upload_interest_trigger_area(
    project_name: str,
    file: UploadFile = File(...),
) -> dict[str, object]:
    return _upload_image_resource(project_name, "interest-trigger-area", file)


@router.post("/projects/{project_name}/comparison-area")
def upload_comparison_area(
    project_name: str,
    file: UploadFile = File(...),
) -> dict[str, object]:
    return _upload_image_resource(project_name, "comparison-area", file)


@router.post("/projects/{project_name}/hsv-color-area")
def upload_hsv_color_area(
    project_name: str,
    file: UploadFile = File(...),
) -> dict[str, object]:
    return _upload_image_resource(project_name, "hsv-color-area", file)
