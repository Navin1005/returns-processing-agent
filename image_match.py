import os
import mysql.connector
import open_clip
import torch
from PIL import Image
import logging

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load CLIP Model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = open_clip.create_model("ViT-B/32", pretrained="openai")
preprocess = open_clip.image_transform(model.visual.image_size, is_train=False)
model.to(device)

# ✅ Fetch Product Images from Database
def get_product_images():
    try:
        conn = mysql.connector.connect(
            host="****",
            user="***",
            password="***",
            database="***"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, image_path FROM Products")
        products = cursor.fetchall()
        conn.close()
        
        if not products:
            logging.warning("⚠️ No product images found in database!")
        
        return products
    except mysql.connector.Error as e:
        logging.error(f"❌ Database error: {e}")
        return []

# ✅ Compare Uploaded Image with Stored Images
def compare_uploaded_image(uploaded_image_path):
    """Compare the uploaded image with stored product images and return the best match."""
    
    try:
        uploaded_image = preprocess(Image.open(uploaded_image_path)).unsqueeze(0).to(device)
        logging.info(f"✅ Uploaded image processed successfully: {uploaded_image.shape}")
    except Exception as e:
        logging.error(f"❌ Error processing uploaded image: {e}")
        return None, 0.0

    products = get_product_images()
    best_match = None
    best_score = 0.0

    if not products:
        return None, 0.0

    matched_count = 0
    unmatched_count = 0

    with torch.no_grad():
        uploaded_features = torch.nn.functional.normalize(model.encode_image(uploaded_image))
        logging.info(f"✅ Uploaded image features extracted successfully.")

        for product_id, image_path in products:
            # 🔹 Ensure the correct image path
            if not os.path.exists(image_path):
                logging.warning(f"⚠️ Image file not found: {image_path}")
                unmatched_count += 1
                continue

            try:
                product_image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
                product_features = torch.nn.functional.normalize(model.encode_image(product_image))

                similarity = torch.nn.functional.cosine_similarity(uploaded_features, product_features)
                score = similarity.item()

                logging.info(f"🔎 Comparing {uploaded_image_path} with {image_path} - Score: {score}")

                if score > best_score:
                    best_score = score
                    best_match = product_id
                    matched_count += 1

            except Exception as e:
                logging.error(f"❌ Error processing product image {image_path}: {e}")
                unmatched_count += 1
                continue

    logging.info(f"✅ Total Matches: {matched_count}, Unmatched: {unmatched_count}")
    logging.info(f"✅ Best match: {best_match}, Score: {best_score}")

    # **Threshold Adjustment for Better Matching**
    return (best_match, best_score) if best_score >= 0.80 else (None, best_score)
