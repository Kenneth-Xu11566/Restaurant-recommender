import argparse
import math
import os
import pandas as pd

from restaurant_scraper import scrape_restaurants_in_neighborhoods

def main():
    """
    CLI entry point:
    1. Parse city name from user.
    2. Call scrape_restaurants_in_neighborhoods(city).
    3. For each neighborhood, prioritize by:
       - Rating (only restaurants with >250 reviews first).
       - Then by composite score (rating + ln(reviews)).
       - Save top 25 in a separate CSV per neighborhood.
    """
    parser = argparse.ArgumentParser(description="Scrape restaurants by city from Google Maps")
    parser.add_argument("city", type=str, help="City to search (e.g., Paris)")
    args = parser.parse_args()
    city_name = args.city

    # 1. Scrape Data
    data = scrape_restaurants_in_neighborhoods(city_name)

    # 2. Sort & Save One CSV per Neighborhood
    for nb, restaurants in data.items():
        df = pd.DataFrame(restaurants)
        if df.empty:
            continue

        # Convert rating to float
        df["rating"] = df["rating"].apply(lambda x: float(x) if x and x.strip() != "" else 0.0)

        # Convert reviews to int
        df["reviews"] = df["reviews"].str.replace(",", "", regex=False).fillna("0")
        df["reviews"] = df["reviews"].apply(lambda x: int(x) if x.isdigit() else 0)

        # Composite score = rating + ln(reviews)
        def composite_score(row):
            return row["rating"] + (math.log(row["reviews"]) if row["reviews"] > 0 else 0)

        df["composite_score"] = df.apply(composite_score, axis=1)

        # **Prioritization Logic**
        df["high_review_flag"] = df["reviews"] > 250  # Flag for restaurants with >250 reviews

        # Sort by:
        # 1. Restaurants with >250 reviews first (`high_review_flag`)
        # 2. Highest rating
        # 3. Composite score as tiebreaker
        df = df.sort_values(
            by=["high_review_flag", "rating", "composite_score"],
            ascending=[False, False, False]
        ).head(25)

        # Insert a Neighborhood column for clarity
        df.insert(0, "Neighborhood", nb)

        # Create a filename like "Paris-Le_Marais.csv"
        safe_nb = nb.replace(" ", "_").replace("/", "_")
        filename = f"bakeries-{city_name}-{safe_nb}.csv"

        # Write CSV (overwrite if exists)
        df.to_csv(filename, index=False, encoding="utf-8")
        print(f"Saved top 25 for neighborhood '{nb}' to file: {filename}")

    print("\nDone! One CSV file per neighborhood created.")

if __name__ == "__main__":
    main()
