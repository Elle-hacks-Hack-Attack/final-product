import cv2
import os

# Define asset paths
image_paths = [
    "assets/path.jpg",
    "assets/vine.webp",
    "assets/fallen_tree.webp",
    "assets/coin.png"
]

# Check if each file exists
for img_path in image_paths:
    if not os.path.exists(img_path):
        print(f"❌ File not found: {img_path}")
    else:
        img = cv2.imread(img_path)
        if img is None:
            print(f"❌ OpenCV could not read: {img_path}")
        else:
            print(f"✅ Successfully loaded: {img_path}")
