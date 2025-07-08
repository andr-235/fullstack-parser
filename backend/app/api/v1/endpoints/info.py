from fastapi import APIRouter

router = APIRouter()


@router.get("/info", tags=["Health"])
async def api_info():
    """Возвращает информацию о API."""
    return {"name": "VK Comments Parser API", "version": "1.0"}
