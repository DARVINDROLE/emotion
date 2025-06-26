from fastapi.templating import Jinja2Templates
from datetime import datetime

templates = Jinja2Templates(directory="templates")

def format_datetime(value, format="%Y-%m-%d %H:%M"):
    if value is None:
        return ""
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").strftime(format)

templates.env.filters["datetimeformat"] = format_datetime
