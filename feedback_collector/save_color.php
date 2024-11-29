<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Decode the JSON payload sent from the JavaScript
    $data = json_decode(file_get_contents('php://input'), true);

    // Check for required color fields in the received data
    if (isset($data['primary']) && isset($data['secondary'])) {
        $primaryColor = $data['primary'];
        $secondaryColor = $data['secondary'];
        $topAppBar = $data['top_app_bar'] ?? null;
        $bottomAppBar = $data['bottom_app_bar'] ?? null;

        // Database connection settings
        $host = 'localhost';
        $db = 'color_picker';
        $user = 'root';
        $pass = '';

        // Establish database connection
        $conn = new mysqli($host, $user, $pass, $db);

        // Check connection
        if ($conn->connect_error) {
            die("Connection failed: " . $conn->connect_error);
        }

        // Prepare and execute the SQL query
        $stmt = $conn->prepare("INSERT INTO colors (primary_color, secondary_color, top_app_bar, bottom_app_bar) VALUES (?, ?, ?, ?)");
        $stmt->bind_param("ssss", $primaryColor, $secondaryColor, $topAppBar, $bottomAppBar);

        if ($stmt->execute()) {
            echo "Colors saved successfully!";
        } else {
            echo "Failed to save colors: " . $stmt->error;
        }

        // Close the statement and connection
        $stmt->close();
        $conn->close();
    } else {
        echo "Invalid data. Both primary and secondary colors are required.";
    }
} else {
    echo "Invalid request method.";
}
?>
