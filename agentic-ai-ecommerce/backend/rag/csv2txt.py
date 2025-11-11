import pandas as pd
import os

csv_path = "data/kaggle_ecom.csv"
out_path = "data/rag_docs/products.txt"

os.makedirs(os.path.dirname(out_path), exist_ok=True)

# Adjust column names to match your CSV structure
# Common Kaggle e-commerce columns: name, title, product_name, category, brand, description, price
COLUMN_MAP = {
    "name": ["name", "product_name", "title"],  # Try these column names
    "category": ["category", "product_category"],
    "brand": ["brand", "manufacturer"],
    "description": ["description", "product_description"],
    "price": ["price", "product_price"]
}

def find_col(df, col_options):
    for col in col_options:
        if col in df.columns:
            return col
    return None

try:
    df = pd.read_csv(csv_path, encoding="utf-8", on_bad_lines="skip")
except UnicodeDecodeError:
    df = pd.read_csv(csv_path, encoding="latin1", on_bad_lines="skip")
print(f"CSV columns: {df.columns.tolist()}")

name_col = find_col(df, COLUMN_MAP["name"])
category_col = find_col(df, COLUMN_MAP["category"])
brand_col = find_col(df, COLUMN_MAP["brand"])
description_col = find_col(df, COLUMN_MAP["description"])
price_col = find_col(df, COLUMN_MAP["price"])

print(f"Mapped columns: name={name_col}, category={category_col}, brand={brand_col}, description={description_col}, price={price_col}")

with open(out_path, "w", encoding="utf-8") as f:
    for _, row in df.iterrows():
        f.write(f"Product: {row.get(name_col, '')}\n")
        f.write(f"Category: {row.get(category_col, '')}\n")
        f.write(f"Brand: {row.get(brand_col, '')}\n")
        f.write(f"Description: {row.get(description_col, '')}\n")
        f.write(f"Price: {row.get(price_col, '')}\n")
        f.write("\n")

print(f"✅ Generated {out_path} with {len(df)} entries.")
