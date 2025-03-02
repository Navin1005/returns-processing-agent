import os
import av
from PIL import Image

# Define input and output folders
INPUT_FOLDER = r"C:\Users\navee\Assignments\Final_Capstone_Project\coding\product_images"
OUTPUT_FOLDER = r"C:\Users\navee\Assignments\Final_Capstone_Project\coding\converted_images"

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def convert_avif_to_jpg():
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".avif"):
            file_path = os.path.join(INPUT_FOLDER, filename)
            output_path = os.path.join(OUTPUT_FOLDER, filename.replace(".avif", ".jpg"))

            try:
                # Open AVIF file using pyav (FFmpeg)
                container = av.open(file_path)
                for frame in container.decode(video=0):
                    img = frame.to_image()
                    img = img.convert("RGB")  # Convert to RGB
                    img.save(output_path, "JPEG")  # Save as JPG
                    print(f"✅ Converted: {filename} -> {output_path}")
                    break  # Only save the first frame

            except Exception as e:
                print(f"❌ Failed to convert {filename}: {e}")

# Run the conversion
convert_avif_to_jpg()
print("✅ All AVIF images converted to JPG!")
