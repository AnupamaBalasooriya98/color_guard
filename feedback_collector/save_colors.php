<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "ui_elements";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Handle image upload
    if (isset($_FILES['image']) && $_FILES['image']['error'] === 0) {
        $imageName = basename($_FILES['image']['name']);
        $targetDir = "uploads/";
        $targetFile = $targetDir . $imageName;

        if (move_uploaded_file($_FILES['image']['tmp_name'], $targetFile)) {
            $stmt = $conn->prepare("INSERT INTO images (name, path) VALUES (?, ?)");
            $stmt->bind_param("ss", $imageName, $targetFile);
            $stmt->execute();
            $imageId = $conn->insert_id;
        } else {
            die("Image upload failed.");
        }
    } else {
        die("No image uploaded.");
    }

    // Save primary and secondary colors
    $primaryColor = $_POST['primaryColor'];
    $secondaryColor = $_POST['secondaryColor'];

    $stmt = $conn->prepare("INSERT INTO colors (image_id, primary_color, secondary_color) VALUES (?, ?, ?)");
    $stmt->bind_param("iss", $imageId, $primaryColor, $secondaryColor);
    $stmt->execute();

    // Save UI elements and colors
    $uiElements = $_POST['uiElement'];
    $colors = $_POST['color'];
    $customColors = $_POST['customColor'];

    foreach ($uiElements as $index => $element) {
        $color = $colors[$index] === "Other" ? $customColors[$index] : $colors[$index];
        $stmt = $conn->prepare("INSERT INTO ui_element_colors (image_id, ui_element, color) VALUES (?, ?, ?)");
        $stmt->bind_param("iss", $imageId, $element, $color);
        $stmt->execute();
    }

    echo "Data saved successfully!";
}

$conn->close();
?>
