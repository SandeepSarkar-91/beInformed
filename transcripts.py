import requests
from bs4 import BeautifulSoup
import time

class ScreenerScraper:
    def __init__(self):
        self.base_url = "https://www.screener.in/company/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def get_company_data(self, symbol):
        """
        Fetches the primary document links and con-call summaries from Screener.in
        """
        url = f"{self.base_url}{symbol.upper()}/"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                print(f"Failed to fetch data for {symbol}: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract Announcements
            announcements = []
            ann_section = soup.find("div", {"id": "documents"})
            if ann_section:
                # Announcements are typically in a list or div within the documents section
                items = ann_section.find_all("li", class_="announcement")
                for item in items[:5]: # Last 5
                    text = item.get_text(separator=" ", strip=True)
                    link = item.find("a")['href'] if item.find("a") else ""
                    announcements.append({"text": text, "link": link})

            # Extract Con-calls (AI Summary IDs)
            concalls = []
            concall_btns = soup.find_all("button", attrs={"data-url": True})
            for btn in concall_btns:
                if "summary" in btn['data-url']:
                    concalls.append({
                        "id": btn['data-url'].strip("/").split("/")[-1],
                        "url": f"https://www.screener.in{btn['data-url']}"
                    })
            
            return {
                "symbol": symbol,
                "announcements": announcements,
                "concall_summaries": concalls[:3] # Last 3
            }
            
        except Exception as e:
            print(f"Error scraping {symbol}: {e}")
            return None

    def get_ai_summary(self, summary_path):
        """
        Fetches the actual text of an AI summary given its internal path
        """
        url = f"https://www.screener.in{summary_path}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                # The response is usually a snippet of HTML or JSON depending on the endpoint
                # If it's the modal content, we parse the text
                soup = BeautifulSoup(response.content, "html.parser")
                return soup.get_text(separator="\n", strip=True)
        except Exception as e:
            print(f"Error fetching AI summary: {e}")
        return "Summary unavailable."

if __name__ == "__main__":
    # Test
    scraper = ScreenerScraper()
    data = scraper.get_company_data("WAAREERTL")
    print(data)
