<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);
    if (isset($data['color1']) && isset($data['color2']) && isset($data['option'])) {
        $color1 = $data['color1'];
        $color2 = $data['color2'];
        $option = $data['option'];

        // Database connection
        $host = 'localhost';
        $db = 'image_colors';
        $user = 'root';
        $pass = '';

        $conn = new mysqli($host, $user, $pass, $db);

        if ($conn->connect_error) {
            die("Connection failed: " . $conn->connect_error);
        }

        // Insert the record into the database
        $stmt = $conn->prepare("INSERT INTO colors (color1, color2, option_value) VALUES (?, ?, ?)");
        $stmt->bind_param("sss", $color1, $color2, $option);

        if ($stmt->execute()) {
            echo "Colors and option saved successfully!";
        } else {
            echo "Failed to save colors and option.";
        }

        $stmt->close();
        $conn->close();
    } else {
        echo "Invalid data.";
    }
} else {
    echo "Invalid request.";
}
?>
