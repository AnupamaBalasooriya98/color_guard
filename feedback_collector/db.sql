CREATE TABLE images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    path VARCHAR(255) NOT NULL
);

CREATE TABLE ui_colors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_id INT NOT NULL,
    ui_element VARCHAR(50) NOT NULL,
    color VARCHAR(20) NOT NULL,
    FOREIGN KEY (image_id) REFERENCES images(id)
);