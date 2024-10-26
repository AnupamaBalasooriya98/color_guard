import colorsys
import json
import os
import sys
import tempfile

import cv2
from colorthief import ColorThief


# Convert RGB tuple to hexadecimal color
def rgb_to_hex(color):
    return "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])


# Convert RGB to HSV and return brightness, hue, and saturation
def rgb_to_hsv(rgb):
    return colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)


def filter_palette(palette):
    """Filter out near-white and low-saturation colors."""
    filtered = []
    for color in palette:
        h, s, v = rgb_to_hsv(color)
        if v < 0.95 and s > 0.2:  # Ignore near-white and pale colors
            filtered.append(color)
    return filtered


def find_primary_and_secondary_colors(image_path):
    ct = ColorThief(image_path)

    # Extract a high-quality palette
    palette = ct.get_palette(color_count=12, quality=5)

    # Filter out irrelevant colors (near-white, low-saturation)
    filtered_palette = filter_palette(palette)

    if not filtered_palette:
        return (255, 255, 255), (0, 0, 0)  # Fallback to white and black

    # Sort by brightness (descending)
    filtered_palette.sort(key=lambda c: rgb_to_hsv(c)[2], reverse=True)

    primary_color = filtered_palette[0]
    secondary_color = filtered_palette[1] if len(filtered_palette) > 1 else (0, 0, 0)

    return primary_color, secondary_color


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
            element_color = ct.get_color(quality=1)
            return element_color
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


def detect_clickable_elements(image_path):
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

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)

        if area > 500:
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

    primary_color, secondary_color = find_primary_and_secondary_colors(image_path)
    print(rgb_to_hex(primary_color) if primary_color else "N/A")
    print(rgb_to_hex(secondary_color) if secondary_color else "N/A")

    detect_clickable_elements(image_path)


if __name__ == "__main__":
    main()
