<?php
// Enable error reporting
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Database credentials
$servername = "localhost"; // Ensure this matches your MySQL host
$username = "root";        // Replace with your MySQL username
$password = "";            // Replace with your MySQL password
$dbname = "color_picker";  // Ensure the database exists and matches this name

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Database connection failed: " . $conn->connect_error);
}

// Check if the request is POST
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Handle image upload
    if (isset($_FILES['image']) && $_FILES['image']['error'] === 0) {
        $imageName = basename($_FILES['image']['name']);
        $targetDir = "uploads/";
        $targetFile = $targetDir . $imageName;

        // Ensure the uploads directory exists
        if (!is_dir($targetDir)) {
            mkdir($targetDir, 0777, true);
        }

        if (move_uploaded_file($_FILES['image']['tmp_name'], $targetFile)) {
            // Save image info to the database
            $stmt = $conn->prepare("INSERT INTO images (name, path) VALUES (?, ?)");
            $stmt->bind_param("ss", $imageName, $targetFile);
            if (!$stmt->execute()) {
                error_log("Image insert error: " . $stmt->error);
                die("Failed to save image to the database.");
            }
            $imageId = $stmt->insert_id; // Get the inserted image ID
        } else {
            die("Failed to upload the image.");
        }
    } else {
        die("No image uploaded or there was an error.");
    }

    // Collect primary and secondary colors
    $primaryColor = $_POST['primaryColor'] ?? null;
    $secondaryColor = $_POST['secondaryColor'] ?? null;

    if (!$primaryColor || !$secondaryColor) {
        die("Primary and secondary colors are required.");
    }

    // Save primary and secondary colors to the colors table
    $stmt = $conn->prepare("INSERT INTO colors (image_id, primary_color, secondary_color) VALUES (?, ?, ?)");
    $stmt->bind_param("iss", $imageId, $primaryColor, $secondaryColor);
    if (!$stmt->execute()) {
        error_log("Color insert error: " . $stmt->error);
        die("Failed to save colors to the database.");
    }

    // Handle UI Elements and Colors
    if (isset($_POST['uiElement']) && is_array($_POST['uiElement'])) {
        $uiElements = $_POST['uiElement'];
        $colors = $_POST['color'];
        $customColors = $_POST['customColor'];

        foreach ($uiElements as $index => $element) {
            $color = ($colors[$index] === "Other") ? $customColors[$index] : $colors[$index];
            $stmt = $conn->prepare("INSERT INTO ui_colors (image_id, ui_element, color) VALUES (?, ?, ?)");
            $stmt->bind_param("iss", $imageId, $element, $color);
            if (!$stmt->execute()) {
                error_log("UI element insert error: " . $stmt->error);
                die("Failed to save UI elements to the database.");
            }
        }
    } else {
        die("No UI elements provided.");
    }

    echo "Data saved successfully!";
} else {
    die("Invalid request method.");
}

// Close connection
$conn->close();
?>
