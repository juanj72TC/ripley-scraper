from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from src.scraper.ripley.scraper import RipleyScraper
from src.models.ripley import RipleyCredentials
import io


class RouterRipley:
    def __init__(self, ripley_scraper: RipleyScraper):
        self.scraper = ripley_scraper
        self.router = APIRouter(tags=["Ripley Scraper"])
        self.router.add_api_route("/scrape", self.scrape, methods=["POST"])

    def get_instance(self):
        return self.router

    async def scrape(
        self,
        ripley_credentials: RipleyCredentials,
        date_from: str = "01-07-2025",
        date_to: str = "31-07-2025",
    ):
        result = await self.scraper.run(ripley_credentials, date_from, date_to)
        stream = io.StringIO()
        result.to_csv(stream, index=False)
        response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=data.csv"

        return response
