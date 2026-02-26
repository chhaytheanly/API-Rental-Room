import os
import re
import shutil

# validate the type of the uploaded file
allowed_image_types = ["image/jpeg", "image/png", "image/gif", "image/jpg", "image/webp"]
directory = "uploads/images"

os.makedirs(directory, exist_ok=True)

def get_image(image):
    if image.content_type not in allowed_image_types:
        raise ValueError("Invalid image type")
    
    original_filename = image.filename
    safe_filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", original_filename)
    print("Safe filename:", safe_filename)
    
    file_path = os.path.join(directory, safe_filename)
    if os.path.exists(file_path):
        base, ext = os.path.splitext(safe_filename)
        counter = 1
        while os.path.exists(file_path):
            safe_filename = f"{base}_{counter}{ext}"
            file_path = os.path.join(directory, safe_filename)
            counter += 1

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return file_path