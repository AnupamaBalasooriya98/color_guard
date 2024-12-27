import colorsys
import json
import os
import sys
import tempfile
import cv2
from colorthief import ColorThief
import webcolors
from PIL import Image

# Convert RGB tuple to hexadecimal color
def rgb_to_hex(color):
    return "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])

def find_primary_and_secondary_colors(image_path):
    ct = ColorThief(image_path)
    palette = ct.get_palette(color_count = 2, quality = 1)
    return palette[0], palette[1]

def dominant_color_of_element(cropped_image):
    if cropped_image is None or cropped_image.size == 0:
        print("Empty or invalid cropped image, skipping color extraction.")
        return None

    rgb_cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)

    # Use temporary file to save cropped image
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        temp_filename = temp_file.name
        cv2.imwrite(temp_filename, rgb_cropped_image)

        try:
            ct = ColorThief(temp_filename)
            palette = ct.get_palette(color_count = 2, quality = 1)
            return palette[0]
        except Exception as e:
            print(f"Error extracting color: {e}")
            return None

def classify_element(contour, image_shape):
    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = w / float(h)
    area = cv2.contourArea(contour)
    image_height, image_width, _ = image_shape

    if y < 0.1 * image_height and w > 0.9 * image_width:
        return "Top App Bar"
    elif y > 0.85 * image_height and w > 0.9 * image_width:
        return "Bottom App Bar"
    elif 1.2 > aspect_ratio > 0.8 and 1000 < area < 8000:
        return "Button"
    elif aspect_ratio > 2.5 and area > 800:
        return "Label"
    else:
        return "Unknown"
    
# Get the closest color name using the webcolors library
def get_color_name(hex_color):
    try:
        # Convert hex to RGB
        rgb_color = webcolors.hex_to_rgb(hex_color)
        # Try to get the exact color name
        color_name = webcolors.rgb_to_name(rgb_color)
    except ValueError:
        # If there's no exact match, get the closest color name
        color_name = get_closest_color_name(rgb_color)
    
    return color_name

# Function to get the closest named color
def get_closest_color_name(requested_color):
    min_colors = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_color.red) ** 2
        gd = (g_c - requested_color.green) ** 2
        bd = (b_c - requested_color.blue) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]

def detect_clickable_elements(image_path):
    def is_within_app_bar(y, h, image_height, top_bar_height, bottom_bar_height):
        return (y < top_bar_height) or (y + h > image_height - bottom_bar_height)
    
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Image not found or unable to load: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    annotated_image = image.copy()
    element_data = []
    image_height, image_width = annotated_image.shape[:2]
    top_bar_height = int(0.05 * image_height)
    bottom_bar_height = int(0.05 * image_height)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)

        if area > 500 and not is_within_app_bar(y, h, image_height, top_bar_height, bottom_bar_height):
            element_type = classify_element(contour, annotated_image.shape)
            cv2.rectangle(annotated_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(annotated_image, element_type, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

            cropped_image = image[y:y + h, x:x + w]
            element_color = dominant_color_of_element(cropped_image)

            if element_color:
                color_hex = rgb_to_hex(element_color)
                element_data.append({
                    "type": element_type,
                    "color": color_hex,
                    "coords": (x, y, w, h)
                })

            cropped_path = os.path.join("uploads", f"cropped_element_{len(element_data)}.jpg")
            cv2.imwrite(cropped_path, cropped_image)

    annotated_image_path = os.path.join("uploads", "annotated_image.jpg")
    cv2.imwrite(annotated_image_path, annotated_image)

    with open(os.path.join("uploads", "element_data.json"), "w") as json_file:
        json.dump(element_data, json_file)

    return annotated_image, element_data


def main():
    image_path = sys.argv[1]

    im = Image.open(image_path)
    im = im.crop((0, 60, 1080, 1795))
    im.save('uploads/_0.png')

    primary_color, secondary_color = find_primary_and_secondary_colors('uploads/_0.png')
    print(rgb_to_hex(primary_color) if primary_color else "N/A")
    print(rgb_to_hex(secondary_color) if secondary_color else "N/A")

    detect_clickable_elements(image_path)


if __name__ == "__main__":
    main()
