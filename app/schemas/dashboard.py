from pydantic import BaseModel

class DashboardStatsResponse(BaseModel):
    published_articles_count: int
    draft_articles_count: int
    total_products_count: int
    out_of_stock_products_count: int

    class Config:
        from_attibutes = True
