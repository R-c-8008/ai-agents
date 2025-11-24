from typing import Any, Dict, List, Optional
import logging
from .base_agent import BaseAgent
import requests
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)


class WebScrapingAgent(BaseAgent):
    """Agent for web scraping tasks"""

    def __init__(self):
        super().__init__(
            name="WebScrapingAgent",
            description="Scrapes and extracts data from websites",
        )
        self.scraped_data = []
        self.session = requests.Session()

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute a web scraping task"""
        logger.info(f"Executing scraping task: {task}")

        try:
            url = kwargs.get("url")
            if not url:
                raise ValueError("URL is required for scraping")

            result = self._scrape_url(url, **kwargs)
            self.scraped_data.append({"url": url, "data": result})

            return {
                "status": "success",
                "task": task,
                "url": url,
                "result": result,
                "total_scraped": len(self.scraped_data),
            }

        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            return {"status": "failed", "task": task, "error": str(e)}

    def _scrape_url(self, url: str, **kwargs) -> Dict[str, Any]:
        """Scrape data from a URL"""
        headers = kwargs.get("headers", {"User-Agent": "Mozilla/5.0"})
        timeout = kwargs.get("timeout", 10)

        response = self.session.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Extract basic data
        data = {
            "title": soup.title.string if soup.title else None,
            "text": soup.get_text()[:1000],  # First 1000 chars
            "links": [a.get("href") for a in soup.find_all("a", href=True)][:10],
            "images": [img.get("src") for img in soup.find_all("img", src=True)][:10],
        }

        return data

    def scrape_multiple_urls(self, urls: List[str], delay: float = 1.0) -> List[Dict]:
        """Scrape multiple URLs with delay between requests"""
        results = []

        for url in urls:
            try:
                result = self.execute("Scrape URL", url=url)
                results.append(result)
                time.sleep(delay)  # Be respectful to servers
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {str(e)}")
                results.append({"url": url, "status": "failed", "error": str(e)})

        return results

    def get_scraped_data(self) -> List[Dict]:
        """Get all scraped data"""
        return self.scraped_data
