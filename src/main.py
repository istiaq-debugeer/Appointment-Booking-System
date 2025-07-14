from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from core.settings import settings
import uvicorn
from api.user import user_route

app = FastAPI(title=settings.app_name, debug=settings.debug)


# app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(user_route)


# @app.get("/")
# async def read_root(request: Request):
#     return templates.TemplateResponse(
#         "register.html", {"request": request, "message": ""}
#     )


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
