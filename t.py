from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_products(url):
    with sync_playwright() as p:
        # Launch browser (headless means it runs without opening a window)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # Wait for content to load
        page.wait_for_timeout(3000)

        # Get the rendered HTML content
        html = page.content()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        
        # Close browser BEFORE returning
        browser.close()
        return soup

# Example usage
if __name__ == "__main__":
    url = "https://www.betpawa.cm/virtual-sports?virtualTab=results"
    soup = scrape_products(url)
    print("Page Title:", soup.title.string if soup.title else "No title found")