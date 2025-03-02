import os
import mysql.connector
import open_clip
import torch
from PIL import Image

# Load CLIP Model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = open_clip.create_model("ViT-B/32", pretrained="openai")
preprocess = open_clip.image_transform(model.visual.image_size, is_train=False)
model.to(device)

# Connect to MySQL
def get_product_images():
    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="returns_db")
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, image_path FROM Products")
    products = cursor.fetchall()
    conn.close()
    return products

# Compare uploaded image with stored images
def compare_uploaded_image(uploaded_image_path):
    uploaded_image = preprocess(Image.open(uploaded_image_path)).unsqueeze(0).to(device)

    products = get_product_images()
    best_match = None
    best_score = 0.0

    for product_id, image_path in products:
        if os.path.exists(image_path):
            product_image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
            with torch.no_grad():
                uploaded_features = model.encode_image(uploaded_image)
                product_features = model.encode_image(product_image)
                similarity = torch.nn.functional.cosine_similarity(uploaded_features, product_features)

            score = similarity.item()
            print(f"DEBUG: Comparing {uploaded_image_path} with {image_path}, Score: {score}")

            if score > best_score:
                best_score = score
                best_match = product_id

    print(f"✅ Best match: {best_match}, Score: {best_score}")

    # Adjusting Threshold (Previously Too Strict)
    if best_score >= 0.85:  # Lowered to 0.85 for better match detection
        return best_match, best_score
    else:
        return None, best_score
