from fastapi import FastAPI
from routers.first_page_module import router as first_page_router
from routers.second_page_module import router as second_page_router
from routers.third_page_module import router as third_page_router
import logging
from fastapi import FastAPI, status, HTTPException, Header, APIRouter

# Setup logging
log_info = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(
      title="Streamlit Unified Survey Web Application API",
      summary="A collection of endpoints for Streamlit Unified Survey Web Application",
      version="0.1.0",
      docs_url="/docs",
      openapi_url="/openapi.json",

)

main_router = APIRouter()

log_info = logging.getLogger(__name__)

@main_router.get("/", status_code=status.HTTP_200_OK, tags=["test"])
def root():
    log_info.info("Root endpoint accessed")
    return {"status": "ok"}

app.include_router(first_page_router, prefix="/first_page", tags=["Data_Cleaner_Pre_Processor"])
app.include_router(second_page_router, prefix="/second_page", tags=["Questionnaire_Definer"])
app.include_router(third_page_router, prefix="/third_page", tags=["Keypress_Decoder"])

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)