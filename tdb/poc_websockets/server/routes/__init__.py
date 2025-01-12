from starlette.templating import Jinja2Templates

from tdb.poc_websockets.server import config

templates = Jinja2Templates(directory=config.settings.TEMPLATES)
