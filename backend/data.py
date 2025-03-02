import mysql.connector
import pandas as pd
from datetime import datetime
from PIL import Image
import os
import cv2
import numpy as np
import imageio.v3 as iio
import os

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",  
    user="root",  
    password="root",  # Change if you have a MySQL password
    database="returns_db"
)
cursor = conn.cursor()

# Load products data
df_products = pd.read_excel("products.xlsx")

# Insert data into MySQL
#for _, row in df_products.iterrows():
#    cursor.execute("""
#        INSERT INTO Products (product_id, product_name, return_window_days, acceptable_packaging, acceptable_defects, image_path) 
#        VALUES (%s, %s, %s, %s, %s, %s)
#    """, (row["product_id"], row["product_name"], row["return_window_days"], 
#          row["acceptable_packaging"], row["acceptable_defects"], f'product_images/product_{row["product_id"]}.jpg'))

#conn.commit()
#print("✅ Products data inserted successfully!")

# Load Customers Data

df_customers = pd.read_csv("customers.csv")

#for _, row in df_customers.iterrows():
#    cursor.execute("""
#        INSERT INTO Customers (customer_id, customer_name, email) 
#        VALUES (%s, %s, %s)
#    """, (row["customer_id"], row["customer_name"], row["email"]))

#conn.commit()
#print("✅ Customers data inserted successfully!")


# Load purchases data
#df_purchases = pd.read_csv("purchases.csv")

# Convert 'purchase_date' to correct format (YYYY-MM-DD)
#df_purchases["purchase_date"] = df_purchases["purchase_date"].apply(lambda x: datetime.strptime(str(x), "%m/%d/%Y").strftime("%Y-%m-%d"))

# Insert data into MySQL
#for _, row in df_purchases.iterrows():
#    cursor.execute("""
#        INSERT INTO Purchases (purchase_id, customer_id, product_id, purchase_date) 
#        VALUES (%s, %s, %s, %s)
#    """, (row["purchase_id"], row["customer_id"], row["product_id"], row["purchase_date"]))

#conn.commit()

#print("✅ Purchases data inserted successfully with correct date format!")

#df_policies = pd.read_csv("Generated_Return_Policies.csv")

#for _, row in df_policies.iterrows():
#    cursor.execute("""
#        INSERT INTO ReturnPolicy (product_id, return_window_days, accepted_defects, packaging_required) 
#        VALUES (%s, %s, %s, %s)
#    """, (row["product_id"], row["return_window_days"], row["accepted_defects"], row["packaging_required"]))#

#conn.commit()
#print("✅ Return Policies data inserted successfully!")
# Update image paths to use .avif instead of .jpg
update_query = """
UPDATE Products 
SET image_path = REPLACE(image_path, '.avif', '.jpg');;
"""


#cursor.execute(update_query)
#conn.commit()

#cursor.close()
#conn.close()

#print("✅ Image paths updated to .avif in the database!")

