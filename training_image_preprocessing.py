import os
from PIL import Image, ImageOps

def find_bounding_box(img):
    """Finds the bounding box of the non-background region more robustly."""
    img_gray = img.convert("L")
    threshold = 10  # Adjust for near-black pixels
    img_bin = img_gray.point(lambda p: 255 if p > threshold else 0)
    bbox = img_bin.getbbox()
    return img.crop(bbox) if bbox else img

def process_rgb_image(img):
    img = img.convert("RGB")
    pixels = img.load()
    width, height = img.size
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            if r < 20 and g < 20 and b < 20:
                pixels[x, y] = (255, 255, 255)  # Extreme black -> White
            elif r < 50 and g < 50 and b < 50:
                pixels[x, y] = (0, 0, 0)  # Close to black -> Black
    return find_bounding_box(img)

def process_label_image(img):
    img = img.convert("RGB")
    pixels = img.load()
    width, height = img.size
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            if r == 26 and g == 26 and b == 26:
                pixels[x, y] = (0, 0, 0)  # Grey -> Black
            elif r == 0 and g == 0 and b == 0:
                pixels[x, y] = (255, 255, 255)  # Black -> White
    return find_bounding_box(img)

def split_and_rename_images(input_folder, output_folder, patch_size=256):
    rgb_folder = os.path.join(output_folder, "X")
    label_folder = os.path.join(output_folder, "Y")
    os.makedirs(rgb_folder, exist_ok=True)
    os.makedirs(label_folder, exist_ok=True)
    
    patch_idx_X = 1
    patch_idx_Y = 1
    
    image_files = sorted([f for f in os.listdir(input_folder) if f.endswith(("RGB.jpg", "Label_image.png"))])

    for filename in image_files:
        img_path = os.path.join(input_folder, filename)
        try:
            with Image.open(img_path) as img:
                img = process_rgb_image(img) if "RGB.jpg" in filename else process_label_image(img)
                width, height = img.size
                step_size = patch_size // 2  # Overlapping patches to ensure coverage
                for y in range(0, height - patch_size + 1, step_size):
                    for x in range(0, width - patch_size + 1, step_size):
                        patch = img.crop((x, y, x + patch_size, y + patch_size))
                        if "RGB.jpg" in filename:
                            output_path = os.path.join(rgb_folder, f"{patch_idx_X}.png")
                            patch.save(output_path)
                            patch_idx_X += 1
                        else:
                            output_path = os.path.join(label_folder, f"{patch_idx_Y}.png")
                            patch.save(output_path)
                            patch_idx_Y += 1
        except Exception as e:
            print(f"Error processing {filename}: {e}")

input_folder = "C:/Users/wangz/Downloads/Sidewalk Concrete Slab Joint/Sidewalk Concrete Slab Joint"
output_folder = "C:/output_image"
split_and_rename_images(input_folder, output_folder)
