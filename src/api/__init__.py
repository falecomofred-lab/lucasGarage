"""
Rotas da API FastAPI.

Contém todos os endpoints REST da aplicação.
"""

from src.api.cars_api import router as cars_router

__all__ = ["cars_router"]
