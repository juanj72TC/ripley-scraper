from src.config import Config
from src.app.router.router_ripley import RouterRipley
from fastapi import FastAPI
from src.scraper.ripley.scraper import RipleyScraper
from src.utils.browser_manager import BrowserManager

# global_config = Config()
config = Config()
browser_manager = BrowserManager()
scraper_ripley = RipleyScraper(config, browser_manager)

router_ripley = RouterRipley(scraper_ripley)

app = FastAPI()

app.include_router(router_ripley.get_instance())

# TODO:
"""
1. check pass verifica si las credenciales son validas o invalidas
2. last update : retorne la ultima fecha de actualzacion del stock (HOME)
3. retorno de archivo
"""