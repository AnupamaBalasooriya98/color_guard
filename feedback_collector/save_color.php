<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);
    if (isset($data['color1']) && isset($data['color2'])) {
        $color1 = $data['color1'];
        $color2 = $data['color2'];

        // Database connection
        $host = 'localhost';
        $db = 'image_colors';
        $user = 'root';
        $pass = '';

        $conn = new mysqli($host, $user, $pass, $db);

        if ($conn->connect_error) {
            die("Connection failed: " . $conn->connect_error);
        }

        // Check if a record already exists
        $query = "SELECT id FROM colors ORDER BY id DESC LIMIT 1";
        $result = $conn->query($query);

        if ($result->num_rows > 0) {
            // Update the latest record
            $row = $result->fetch_assoc();
            $stmt = $conn->prepare("UPDATE colors SET color1 = ?, color2 = ? WHERE id = ?");
            $stmt->bind_param("ssi", $color1, $color2, $row['id']);
        } else {
            // Insert new record
            $stmt = $conn->prepare("INSERT INTO colors (color1, color2) VALUES (?, ?)");
            $stmt->bind_param("ss", $color1, $color2);
        }

        if ($stmt->execute()) {
            echo "Colors saved or updated successfully!";
        } else {
            echo "Failed to save or update colors.";
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
