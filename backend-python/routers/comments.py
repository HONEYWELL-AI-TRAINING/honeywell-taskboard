"""HTTP layer for task comments. Translates domain errors into status codes."""
from fastapi import APIRouter, Depends, HTTPException, Response, status

from dependencies import get_comment_service
from schemas.comment import CommentCount, CommentCreate, CommentRead
from services.comment_service import CommentService
from services.errors import CommentNotFound, TaskNotFound

router = APIRouter(prefix="/api/tasks/{task_id}/comments", tags=["comments"])


@router.get("", response_model=list[CommentRead])
async def list_comments(
    task_id: int,
    service: CommentService = Depends(get_comment_service),
) -> list[CommentRead]:
    try:
        comments = await service.list_comments(task_id)
    except TaskNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [CommentRead.model_validate(comment) for comment in comments]


@router.get("/count", response_model=CommentCount)
async def count_comments(
    task_id: int,
    service: CommentService = Depends(get_comment_service),
) -> CommentCount:
    try:
        return CommentCount(count=await service.count_comments(task_id))
    except TaskNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
async def create_comment(
    task_id: int,
    payload: CommentCreate,
    service: CommentService = Depends(get_comment_service),
) -> CommentRead:
    try:
        return CommentRead.model_validate(await service.create_comment(task_id, payload))
    except TaskNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    task_id: int,
    comment_id: int,
    service: CommentService = Depends(get_comment_service),
) -> Response:
    try:
        await service.delete_comment(task_id, comment_id)
    except (TaskNotFound, CommentNotFound) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)