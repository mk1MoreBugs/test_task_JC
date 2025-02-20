from fastapi import APIRouter
from app.api.routes import wallets

api_router = APIRouter()


api_router.include_router(wallets.router)
