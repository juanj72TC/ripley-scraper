from src.config import Config
from src.app.router import RouterRipley
from fastapi import FastAPI
from src.scraper.ripley import RipleyScraper

# global_config = Config()
config = Config()
scraper_ripley = RipleyScraper(config)

router_ripley = RouterRipley(scraper_ripley)

app = FastAPI()

app.include_router(router_ripley.get_instance())

# if __name__ == "__main__":
#     config = Config()
#     scraper = RipleyScraper(config)
#     print(scraper.run())
