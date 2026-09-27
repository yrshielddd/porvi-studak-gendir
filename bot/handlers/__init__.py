from aiogram import Router
from .start import router as start_router
from .posts import router as posts_router
from .generate import router as generate_router
from .brief import router as brief_router

def setup_routers() -> Router:
    root = Router()
    root.include_router(start_router)
    root.include_router(posts_router)
    root.include_router(generate_router)
    root.include_router(brief_router)
    return root