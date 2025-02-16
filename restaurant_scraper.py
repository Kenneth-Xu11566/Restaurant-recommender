import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 1. Import the function from neighborhoods_scrape.py
from neighborhoods_scrape import get_popular_neighborhoods

def scrape_restaurants_in_neighborhoods(city):
    """
    1. Gets the list of popular neighborhoods for the given city.
    2. Navigates to Google Maps.
    3. For each neighborhood, searches for "local restaurants in {neighborhood}, {city}",
       then applies the 4.5-star filter by modifying the URL (optional).
    4. Scrolls through the results and extracts:
       - Name (<div class="qBF1Pd.fontHeadlineSmall">)
       - Rating & Reviews (<span class="ZkP5Je" aria-label="4.9 stars 94 Reviews">)
       - Cuisine/Type & Address (<div class="W4Efsd">)
       - Category (text under star rating)
    5. Stores ALL restaurants found (no skipping if <4.5).
    """

    # --- A. Get Neighborhoods ---
    neighborhoods = get_popular_neighborhoods(city)
    print(f"Found neighborhoods in {city}: {neighborhoods}")

    # --- B. Set Up ChromeDriver (New Session) ---
    chrome_options = Options()
    chrome_options.binary_location = (
        "/Users/KennethXu/Downloads/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
    )
    service = Service("/Users/KennethXu/Downloads/chromedriver-mac-arm64/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Dictionary: neighborhood -> list of restaurant data
    neighborhood_restaurants = {}

    try:
        # --- C. Navigate to Google Maps ---
        driver.get("https://maps.google.com")
        time.sleep(5)  # Let Maps load

        # --- D. Loop through neighborhoods ---
        for nb in neighborhoods:
            # 1. Perform the Search
            search_box = driver.find_element(By.ID, "searchboxinput")
            search_box.clear()
            search_query = f"local restaurants in {nb}, {city}"
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.RETURN)
            time.sleep(5)  # Wait for results to load

            # 2. Apply filter if present
            current_url = driver.current_url
            if "data=!3m1!4b1?" in current_url:
                filtered_url = current_url.replace(
                    "data=!3m1!4b1?", 
                    "data=!3m1!4b1!4m4!2m3!5m1!4e9!6e5?"
                )
                driver.get(filtered_url)
                time.sleep(5)

            print(f"\nNeighborhood: {nb} | Query: {search_query} | Filtered URL loaded.")

            # --- E. Scroll & Extract Restaurant Data ---
            print(f"Loading & scrolling for neighborhood: {nb}")

            restaurants_data = []

            scrollable_selector = "div[role='feed']"  # The main scrollable results area
            last_height = 0
            new_height = 1
            attempts = 0
            max_attempts = 20

            # Locate the scrollable div
            try:
                scrollable_div = driver.find_element(By.CSS_SELECTOR, scrollable_selector)
            except:
                print("Could not find scrollable element")
                continue

            # Keep scrolling until heights match or we exceed attempts
            while (new_height != last_height) and (attempts < max_attempts):
                # 1. Store current scroll height
                last_height = driver.execute_script(
                    "return arguments[0].scrollHeight", scrollable_div
                )

                # 2. Scroll to bottom
                driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight",
                    scrollable_div
                )
                time.sleep(random.uniform(1.5, 2.5))

                # 3. Get new scroll height
                new_height = driver.execute_script(
                    "return arguments[0].scrollHeight", scrollable_div
                )

                # 4. Process any newly visible cards
                current_cards = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
                for card in current_cards:
                    # Skip if we've already processed
                    if card.get_attribute("data-processed"):
                        continue

                    # Mark card as processed
                    driver.execute_script("arguments[0].setAttribute('data-processed', 'true')", card)

                    # Extract data
                    name, rating, reviews, info_text, category = extract_restaurant_info(card)

                    # Always add the restaurant, even if <4.5
                    if name:
                        restaurants_data.append({
                            "name": name,
                            "rating": rating,
                            "reviews": reviews,
                            "info": info_text,
                            "category": category,
                        })

                attempts += 1

            # Store data for this neighborhood
            neighborhood_restaurants[nb] = restaurants_data

            # Optional: return to the main Maps page for the next iteration
            driver.get("https://maps.google.com")
            time.sleep(3)

    finally:
        # --- F. Clean Up ---
        driver.quit()

    return neighborhood_restaurants


def extract_restaurant_info(card):
    """
    Extract name, rating, reviews, info and category from a single <div class="Nv2PK"> card.
    Returns (name, rating, reviews, info_text, category).
    """
    name, rating, reviews, info_text, category = None, None, None, None, None

    # 1) Restaurant Name
    try:
        name_el = card.find_element(By.CSS_SELECTOR, "div.qBF1Pd.fontHeadlineSmall")
        name = name_el.text.strip()
    except:
        pass

    # 2) Rating & Reviews
    try:
        rating_el = card.find_element(By.CSS_SELECTOR, "span.ZkP5Je")
        rating_val = rating_el.find_element(By.CSS_SELECTOR, "span.MW4etd").text.strip()
        reviews_val = rating_el.find_element(By.CSS_SELECTOR, "span.UY7F9").text.strip()
        reviews_val = reviews_val.replace("(", "").replace(")", "")
        rating = rating_val
        reviews = reviews_val
    except:
        pass

    # 3) Cuisine/Type & Address
    try:
        info_el = card.find_element(By.CSS_SELECTOR, "div.W4Efsd")
        info_text = info_el.text.strip()
    except:
        pass

    # 4) Category (text under star rating)
    try:
        category_el = card.find_element(By.CSS_SELECTOR, "div.fontBodyMedium")
        category = category_el.text.strip()
    except:
        pass

    return name, rating, reviews, info_text, category


