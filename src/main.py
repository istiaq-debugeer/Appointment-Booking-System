from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from core.settings import settings
import uvicorn
from api.user import user_route
from api.appointment import appointment_route
from api.report import report_router
from core.middleware import auth_middleware
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(title=settings.app_name, debug=settings.debug)


app.mount("/static", StaticFiles(directory="templates/static"), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/auth/login")
app.include_router(user_route)
app.include_router(appointment_route)
app.include_router(report_router)
app.add_middleware(
    SessionMiddleware,
    secret_key="a1b2c3d4e5f678901234567890abcdef1234567890abcdef1234567890abcdef",
)
app.middleware("http")(auth_middleware)

# @app.get("/")
# async def read_root(request: Request):
#     return templates.TemplateResponse(
#         "register.html", {"request": request, "message": ""}
#     )


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
