from fastapi import FastAPI
from routers.first_page_module import router as first_page_router
from routers.second_page_module import router as second_page_router
from routers.third_page_module import router as third_page_router

app = FastAPI()

app.include_router(first_page_router, prefix="/first_page", tags=["First Page"])
app.include_router(second_page_router, prefix="/second_page", tags=["Second Page"])
app.include_router(third_page_router, prefix="/third_page", tags=["Third Page"])
