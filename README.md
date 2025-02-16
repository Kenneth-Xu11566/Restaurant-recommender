First, run: python driver.py {city_name (e.g. Paris)}

This will prompt a chromedriver to collect the most popular tourist neighborhoods of the given city.

For every neighborhood of the city, google maps will be scraped for restaurants/bakeries/shops above 4.5 stars in that given area:
<img width="1013" alt="Screenshot 2025-02-16 at 3 43 51 PM" src="https://github.com/user-attachments/assets/dc289d77-7779-4889-bd12-bc26fef71801" />

After each neighborhood is scraped, the data is ranked and cleaned based on rating and number of reviews, and the top 25 restaurants/bakeries/shops in each neighborhood and stored in a csv.

Run python cleaner.py to clean the csvs for better readibility.

The final product should be csvs that look like this:
<img width="1206" alt="Screenshot 2025-02-16 at 3 52 20 PM" src="https://github.com/user-attachments/assets/0e56bdbb-eea6-4553-9cc4-d3e1cc6a48c8" />


