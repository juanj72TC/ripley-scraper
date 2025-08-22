from src.models.ripley import RipleyRequestCredentials, RipleyCredentials
from src.scraper.ripley.scraper import RipleyScraper
from playwright.async_api import async_playwright, TimeoutError


class RipleyCheckPass:
    def __init__(self, ripley_scraper: RipleyScraper):
        self.ripley_scraper = ripley_scraper

    async def run(self, credentials: RipleyRequestCredentials):
        credentials = RipleyCredentials(
            username=credentials.username,
            password=credentials.password,
            type_report=RipleyCredentials.TypeReport.sales,
        )
        try:
            async with async_playwright() as p:
                connect_url = "http://localhost:9222"
                browser = await p.chromium.connect_over_cdp(connect_url)
                version = browser.version
                print(f"Connected to browser version: {version}")
                context = await browser.new_context()
                page = await context.new_page()

                await self.ripley_scraper._do_login(page, credentials)

                frame, message = await self.ripley_scraper._search_menu_frame(page)
                if message:
                    return True
                else:
                    raise ValueError("Invalid credentials or unable to access the menu frame.")
        except Exception as e:
            raise ValueError(e)
