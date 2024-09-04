from fastapi import APIRouter
from app.api.api_v1.endpoints import stores, login, product, article, token, wordpress, prompt

api_router = APIRouter()

api_router.include_router(stores.router, prefix="/stores", tags=["stores"])
api_router.include_router(product.router, prefix="/products", tags=["products"])
api_router.include_router(article.router, prefix="/articles", tags=["articles"])
api_router.include_router(prompt.router, prefix="/prompts", tags=["prompts"])
api_router.include_router(wordpress.router, prefix="/wordpress", tags=["wordpress"])
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(token.router, prefix="/token", tags=["token"])