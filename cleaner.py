import pandas as pd
import os
import glob

def clean_csv(original_csv, cleaned_csv):
    """
    1) Remove "Neighborhood" column
    2) In "info" column, keep only substring after '·'
    3) In "category", line 3 -> split on '·':
       category -> substring before '·'
       address  -> substring after '·'
    4) Save to new CSV; then delete original.
    """

    # 1. Read the original CSV
    df = pd.read_csv(original_csv)
    print("Columns in CSV:", df.columns)

    # 2. Drop "Neighborhood" if exists
    if "Neighborhood" in df.columns:
        df.drop(columns=["Neighborhood"], inplace=True)

    # 3. Clean the "info" column to keep substring after '·'
    def clean_info(val):
        if pd.isna(val):
            return val
        if "·" in val:
            return val.split("·")[-1].strip()
        return val
    if "info" in df.columns:
        df["info"] = df["info"].apply(clean_info)

    # 4. Parse the "category" column:
    #    - We'll parse line 3 (the third line) of the multiline text
    #    - Before the first '·' => new category
    #    - After the first '·' => new address
    #    - If there's no line 3 or no '·', fallback gracefully
    def parse_category(cell_text):
        if pd.isna(cell_text):
            return None, None

        lines = cell_text.splitlines()
        # Use line 3 if it exists, else fallback to last line
        if len(lines) < 3:
            line3 = lines[-1].strip()
        else:
            line3 = lines[2].strip()

        if "·" in line3:
            parts = line3.split("·", maxsplit=1)
            new_cat = parts[0].strip()
            address = parts[1].strip() if len(parts) > 1 else ""
        else:
            new_cat = line3
            address = ""

        return new_cat, address

    if "category" in df.columns:
        df["address"] = ""
        new_categories, new_addresses = [], []

        for val in df["category"]:
            c, a = parse_category(val)
            new_categories.append(c)
            new_addresses.append(a)

        df["category"] = new_categories
        df["address"] = new_addresses

    # 5. Write out the cleaned CSV
    df.to_csv(cleaned_csv, index=False)
    print(f"Saved cleaned CSV as: {cleaned_csv}")

    # 6. Delete the original CSV
    if os.path.exists(original_csv):
        os.remove(original_csv)
        print(f"Deleted the original CSV: {original_csv}")
    else:
        print(f"Could not delete {original_csv} (not found).")


if __name__ == "__main__":
    # Process ALL CSV files in the current directory
    csv_files = glob.glob("*.csv")
    for csv_file in csv_files:
        # Skip any file already ending with "_cleaned.csv"
        if csv_file.endswith("_cleaned.csv"):
            continue

        # Create the new name by adding "_cleaned" before .csv
        base, ext = os.path.splitext(csv_file)
        cleaned_csv_name = f"{base}_cleaned{ext}"

        # Clean it
        clean_csv(csv_file, cleaned_csv_name)
