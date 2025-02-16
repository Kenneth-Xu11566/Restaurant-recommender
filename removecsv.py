import os
import glob

directory = "/Users/KennethXu/Personal_Projects/Restaurant_Scrape"  # Change this to your actual directory path

# Get all CSV files in the directory
csv_files = glob.glob(os.path.join(directory, "*.csv"))

# Loop through and remove each file
for file in csv_files:
    os.remove(file)

print("All CSV files removed successfully.")
