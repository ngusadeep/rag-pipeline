from fastapi import APIRouter

from .health import router as health_router
from .index import router as index_router
from .retrieve import router as retrieve_router
from .generate import router as generate_router

router = APIRouter()
router.include_router(health_router)
router.include_router(index_router)
router.include_router(retrieve_router)
router.include_router(generate_router)
