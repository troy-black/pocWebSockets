from fastapi import APIRouter
from pydantic import BaseModel
from starlette import status

router = APIRouter(
    prefix='/status',
    tags=['status'],
)


class HealthCheck(BaseModel):
    status: bool


@router.get(
    '/health',
    summary='Perform a Health Check',
    response_description='Return HTTP Status Code 200 (OK)',
    status_code=status.HTTP_200_OK,
)
def get_health() -> HealthCheck:
    return HealthCheck(status=True)
