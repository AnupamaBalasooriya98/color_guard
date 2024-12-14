-- Create the database
CREATE
DATABASE color_picker;

-- Use the database
USE
color_picker;

-- Table to store uploaded images
CREATE TABLE images
(
    id         INT AUTO_INCREMENT PRIMARY KEY,     -- Unique image ID
    name       VARCHAR(255) NOT NULL,              -- Name of the uploaded image file
    path       VARCHAR(255) NOT NULL,              -- Path where the image is stored
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Timestamp of upload
);

-- Table to store primary and secondary colors
CREATE TABLE colors
(
    id              INT AUTO_INCREMENT PRIMARY KEY,      -- Unique ID for the colors entry
    image_id        INT         NOT NULL,                -- Reference to the image ID
    primary_color   VARCHAR(20) NOT NULL,                -- Primary color value
    secondary_color VARCHAR(20) NOT NULL,                -- Secondary color value
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp
    FOREIGN KEY (image_id) REFERENCES images (id) ON DELETE CASCADE
);

-- Table to store UI elements and their associated colors
CREATE TABLE ui_colors
(
    id         INT AUTO_INCREMENT PRIMARY KEY,      -- Unique ID for the UI element
    image_id   INT         NOT NULL,                -- Reference to the image ID
    ui_element VARCHAR(50) NOT NULL,                -- UI element name (e.g., Button, Radio Button)
    color      VARCHAR(50) NOT NULL,                -- Color for the UI element
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp
    FOREIGN KEY (image_id) REFERENCES images (id) ON DELETE CASCADE
);
