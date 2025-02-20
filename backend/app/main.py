from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.api.main import api_router
from app.core.config import settings


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url="/openapi.json",
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if exc.args[0][0]["type"] == "enum":
        error_message = "Некорректный тип операции"
        status_code = 400
    else:
        error_message = "Невалидный json"
        status_code = 422

    return JSONResponse(
        status_code= status_code,
        content={"detail": error_message, "body": exc.body}
    )

