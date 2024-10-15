import pickle
import json
import sys

def load_model(model_path):
    try:
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
        print("Model loaded successfully.")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def rgb_to_hex(color):
    return "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def generate_ui_tips(element_data, primary_color_hex, secondary_color_hex):
    primary_color = hex_to_rgb(primary_color_hex)
    secondary_color = hex_to_rgb(secondary_color_hex)

    guidelines = {
        'TOP APP BAR': [primary_color],
        'BOTTOM APP BAR': [primary_color],
        'BACKDROP_BACK': [primary_color],
        'BACKDROP_FRONT': [(255, 255, 255)],
        'SHEET_SURFACE': [(255, 255, 255)],
        'MODAL_SHEET': [(255, 255, 255), primary_color, secondary_color],
        'CARD': [(255, 255, 255)],
        'BUTTON': [primary_color],
        'RADIO_BUTTON': [(255, 255, 255)],
        'CHECK_BOX': [(255, 255, 255)],
        'FAB': [secondary_color],
        'SELECTION_CONTROL': [secondary_color],
        'ICON': [primary_color],
        'TEXT_INPUT': [secondary_color],
        'LABEL': [primary_color]
    }

    tips = []
    for element in element_data:
        element_type = element['type']
        element_color_hex = element['color']
        element_color = hex_to_rgb(element_color_hex)

        expected_colors = guidelines.get(element_type.upper(), [])

        if expected_colors:
            if element_color in expected_colors:
                tip = f"The {element_type} color is as per guidelines."
            else:
                expected_colors_hex = [rgb_to_hex(c) for c in expected_colors]
                tip = (f"The {element_type} color {element_color_hex} does not match the guideline colors "
                       f"{', '.join(expected_colors_hex)}. Consider updating it.")
        else:
            tip = f"No guidelines available for {element_type}. Consider reviewing its color."

        tips.append({
            'element_type': element_type,
            'color': element_color_hex,
            'tip': tip
        })
    return tips

def main():
    element_data_file = sys.argv[1]
    primary_color_hex = sys.argv[2]
    secondary_color_hex = sys.argv[3]

    model = load_model('model.pkl')

    with open(element_data_file, 'r') as f:
        element_data = json.load(f)

    tips = generate_ui_tips(element_data, primary_color_hex, secondary_color_hex)

    tips_output_file = 'uploads/ui_tips.json'
    with open(tips_output_file, 'w') as f:
        json.dump(tips, f, indent=4)

    print(f"UI improvement tips generated and saved to {tips_output_file}")

if __name__ == '__main__':
    main()
