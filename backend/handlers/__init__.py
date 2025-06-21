from aiogram import Dispatcher
from handlers.start import router as start_router
from handlers.profile import router as profile_router
from handlers.battle import router as battle_router

def setup_handlers(dp: Dispatcher):
    """Setup all handlers"""
    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(battle_router)