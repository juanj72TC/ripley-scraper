from fastapi import APIRouter
from fastapi.responses import JSONResponse
from src.scraper.ripley import RipleyScraper


class RouterRipley:
    def __init__(self, ripley_scraper: RipleyScraper):
        self.scraper = ripley_scraper
        self.router = APIRouter(tags=["Ripley Scraper"])
        self.router.add_api_route("/scrape", self.scrape, methods=["POST"])

    def get_instance(self):
        return self.router

    def scrape(self, date_from: str, date_to: str):
        result = self.scraper.run(date_from, date_to)
        return result