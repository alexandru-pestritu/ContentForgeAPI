from fastapi import APIRouter
from app.api.api_v1.endpoints import blog, stores, login, product, article, token, wordpress, prompt, ai, widgets, dashboard, stock_check_log, websocket, importer, exporter, settings, placeholder

api_router = APIRouter()

api_router.include_router(blog.router, prefix="/blogs", tags=["blogs"])
api_router.include_router(stores.router, prefix="/{blog_id}/stores", tags=["stores"])
api_router.include_router(product.router, prefix="/{blog_id}/products", tags=["products"])
api_router.include_router(article.router, prefix="/{blog_id}/articles", tags=["articles"])
api_router.include_router(prompt.router, prefix="/{blog_id}/prompts", tags=["prompts"])
api_router.include_router(wordpress.router, prefix="/{blog_id}/wordpress", tags=["wordpress"])
api_router.include_router(ai.router, prefix="/{blog_id}/ai", tags=["ai"])
api_router.include_router(widgets.router, prefix="/{blog_id}/widgets", tags=["widgets"])
api_router.include_router(dashboard.router, prefix="/{blog_id}/dashboard", tags=["dashboard"])
api_router.include_router(stock_check_log.router, prefix="/{blog_id}/stock-check-logs", tags=["stock_check_logs"])
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(token.router, prefix="/token", tags=["token"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websockets"])
api_router.include_router(importer.router, prefix="/{blog_id}/import", tags=["importer"])
api_router.include_router(exporter.router, prefix="/{blog_id}/export", tags=["exporter"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(placeholder.router, prefix="/placeholders", tags=["placeholders"])
