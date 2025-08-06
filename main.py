from src.config import Config
from src.scraper.ripley import RipleyScraper

if __name__ == "__main__":
    config = Config()
    scraper = RipleyScraper(config)
    scraper.run()
