<html>
<head>
    <link rel="icon" type="image/png" href="img/logo.png">
    <title>Annotation results</title>
    <style>
        .color-block {
            display: inline-block;
            width: 50px;
            height: 50px;
            margin-right: 10px;
            border: 1px solid #000;
        }
        .color-container {
            margin-bottom: 20px;
        }
        .element-container {
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }
        .element-container img {
            width: 100px;
            height: auto;
            margin-right: 10px;
        }
        .element-details {
            display: inline-block;
            vertical-align: top;
        }
        .annotated-image {
            max-width: 80%; 
            height: auto; 
            margin-bottom: 30px;
            display: block;
        }
    </style>
</head>
<body>
    <?php
        function delete_all($folder_path) {
            $files = glob($folder_path . '/*');
            foreach ($files as $file) {
                if (is_dir($file)) {
                    delete_all($file);
                    rmdir($file);
                } else {
                    unlink($file);
                }
            }
        }

        if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_FILES['screenshot'])) {
            delete_all("uploads");
            $target_dir = "uploads/";
            $target_file = $target_dir . basename($_FILES["screenshot"]["name"]);

            if (move_uploaded_file($_FILES["screenshot"]["tmp_name"], $target_file)) {
                $python_path = 'C:\\Users\\Anupama\\AppData\\Local\\Programs\\Python\\Python312\\python.exe';
                $escaped_target_file = escapeshellarg($target_file);

                // Run the Python annotation script to extract primary and secondary colors
                $command = escapeshellcmd("$python_path annotate_image.py $escaped_target_file");
                exec($command . ' 2>&1', $output, $result_code);

                if ($result_code === 0) {
                    $primary_color = trim($output[0] ?? "#000000");
                    $secondary_color = trim($output[1] ?? "#FFFFFF");

                    // Display primary and secondary colors
                    echo "<h2>Primary and Secondary Colors</h2>";
                    echo "<div class='color-container'>";
                    echo "<div class='color-block' style='background-color: " . htmlspecialchars($primary_color) . ";'></div>";
                    echo "<p><strong>Primary Color:</strong> " . htmlspecialchars($primary_color) . "</p>";
                    echo "<div class='color-block' style='background-color: " . htmlspecialchars($secondary_color) . ";'></div>";
                    echo "<p><strong>Secondary Color:</strong> " . htmlspecialchars($secondary_color) . "</p>";
                    echo "</div>";

                    // Display the whole annotated image
                    echo "<h2>Annotated Image</h2>";
                    echo "<img src='uploads/annotated_image.jpg' alt='Annotated Image' class='annotated-image'>";

                    // Run the generate_tips.py script with extracted colors
                    $generate_tips_command = escapeshellcmd("$python_path generate_tips.py uploads/element_data.json $primary_color $secondary_color");
                    exec($generate_tips_command, $tips_output, $tips_status);

                    if ($tips_status === 0) {
                        $tips_json = file_get_contents('uploads/ui_tips.json');
                        $tips_data = json_decode($tips_json, true);

                        echo "<h2>Annotated Elements with Improvement Tips</h2>";
                        foreach ($tips_data as $index => $tip) {
                            $cropped_image_path = "uploads/cropped_element_" . ($index + 1) . ".jpg";
                            echo "<div class='element-container'>";
                            echo "<img src='" . htmlspecialchars($cropped_image_path) . "' alt='Element'>";
                            echo "<div class='element-details'>";
                            echo "<p><strong>Element:</strong> " . htmlspecialchars($tip['element_type']) . "</p>";
                            echo "<p><strong>Color:</strong> " . htmlspecialchars($tip['color']) . "</p>";
                            echo "<p><strong>Tip:</strong> " . htmlspecialchars($tip['tip']) . "</p>";
                            echo "</div>";
                            echo "</div>";
                        }
                    } else {
                        echo "<p>Error generating UI improvement tips.</p>";
                    }
                } else {
                    echo "<p>Failed to annotate the image. Please try again.</p>";
                }
            } else {
                echo "<p>Error uploading the file.</p>";
            }
        } else {
            echo "<p>No file uploaded. Please try again.</p>";
        }
    ?>
</body>
</html>
