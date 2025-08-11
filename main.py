from src.config import Config
from src.app.router.router_ripley import RouterRipley
from fastapi import FastAPI
from src.scraper.ripley import RipleyScraper

# global_config = Config()
config = Config()
scraper_ripley = RipleyScraper(config)

router_ripley = RouterRipley(scraper_ripley)

app = FastAPI()

app.include_router(router_ripley.get_instance())
