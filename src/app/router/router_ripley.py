from fastapi import APIRouter
from fastapi.responses import JSONResponse
from src.scraper.ripley.scraper import RipleyScraper


class RouterRipley:
    def __init__(self, ripley_scraper: RipleyScraper):
        self.scraper = ripley_scraper
        self.router = APIRouter(tags=["Ripley Scraper"])
        self.router.add_api_route("/scrape", self.scrape, methods=["GET"])

    def get_instance(self):
        return self.router

    def scrape(self, date_from: str = "01-07-2025", date_to: str = "31-07-2025"):
        result = self.scraper.run(date_from, date_to)
        return result
