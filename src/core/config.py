import os
from fastapi.templating import Jinja2Templates

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)  # go up from core/ to src/
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")  # src/templates

templates = Jinja2Templates(directory=TEMPLATES_DIR)
