import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def get_popular_neighborhoods(city):
    """
    Searches on Google for 'most popular tourist neighborhoods in {city}',
    clicks the 'Show more' button to reveal all neighborhoods,
    and extracts the neighborhood names from the <div class="B0jnne"> sections.
    Returns a list of neighborhood names.
    """

    # 1. Configure ChromeDriver and Chrome for Testing
    chrome_options = Options()
    # Update these paths for your environment
    chrome_options.binary_location = (
        "/Users/KennethXu/Downloads/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
    )
    
    service = Service("/Users/KennethXu/Downloads/chromedriver-mac-arm64/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # 2. Navigate to Google
        driver.get("https://www.google.com")
        time.sleep(2)  # Let the page load; handle any cookie popups if needed

        # 3. Perform Google Search
        query = f"most popular tourist neighborhoods in {city}"
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        # Wait a bit for Google to load the search results
        time.sleep(30)

        # 4. Click the "Show more" / "9 more" button if it exists
        #    This is the element with class "PBBEhf" in your screenshot.
        try:
            show_more_button = driver.find_element(By.CSS_SELECTOR, ".PBBEhf")
            show_more_button.click()
            # Give Google a moment to expand and load more items
            time.sleep(2)
        except Exception:
            # If the button isn't found or can't be clicked, ignore and proceed
            pass

        # 5. Find Neighborhood Elements (now that we've potentially expanded them)
        neighborhood_divs = driver.find_elements(By.CSS_SELECTOR, "div.B0jnne")
        neighborhoods = []
        for div in neighborhood_divs:
            try:
                # Extract the child div containing the neighborhood name
                name_div = div.find_element(By.CSS_SELECTOR, "div.FZPZX.q8U8x.tNxQIb.PZPZlf")
                neighborhood_name = name_div.text.strip()
                if neighborhood_name:
                    neighborhoods.append(neighborhood_name)
            except Exception:
                # If the structure isn't found, skip silently
                continue

        return neighborhoods

    finally:
        # 6. Clean Up
        driver.quit()


