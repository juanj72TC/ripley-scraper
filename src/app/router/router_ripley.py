from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from src.scraper.ripley.scraper import RipleyScraper
from src.models.ripley import RipleyCredentials
from src.models.ripley import RipleyRequestCredentials
from src.scraper.ripley.checkpass import RipleyCheckPass
import io


class RouterRipley:
    def __init__(
        self, ripley_scraper: RipleyScraper, ripley_check_pass: RipleyCheckPass
    ):
        self.scraper = ripley_scraper
        self.check_pass = ripley_check_pass
        self.router = APIRouter(tags=["Ripley Scraper"])
        self.router.add_api_route("/scrape", self.scrape, methods=["POST"])
        self.router.add_api_route("/checkpass", self.check_pass_, methods=["POST"])

    def get_instance(self):
        return self.router

    async def scrape(
        self,
        ripley_credentials: RipleyCredentials,
        date_from: str = "01-07-2025",
        date_to: str = "31-07-2025",
    ):
        try:
            result = await self.scraper.run(ripley_credentials, date_from, date_to)
            stream = io.StringIO()
            result.to_csv(stream, index=False)
            response = StreamingResponse(
                iter([stream.getvalue()]), media_type="text/csv"
            )
            response.headers["Content-Disposition"] = "attachment; filename=data.csv"

            return response
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))

    async def check_pass_(self, ripley_credentials: RipleyRequestCredentials):
        try:
            if await self.check_pass.run(ripley_credentials):
                return JSONResponse(
                    status_code=200, content={"message": "Credentials are valid"}
                )
            else:
                return JSONResponse(
                    status_code=500, content={"message": "error in platform"}
                )
        except Exception as e:
            return JSONResponse(status_code=401, content={"message": str(e)})
