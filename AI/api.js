const axios = require("axios");
const fs = require("fs");
const path = require("path");
const https = require("https");

const API_URL = "https://your-ngrok-url.ngrok.io/generate"; // Replace with Colab's ngrok URL

async function generateLinkedInPost(prompt) {
    try {
        const response = await axios.post(API_URL, { prompt });
        console.log("Generated Content:", response.data.content);
        console.log("Hashtags:", response.data.hashtags);
        console.log("Image URL:", response.data.image_url);

        // Download the image
        const imageUrl = response.data.image_url;
        const imagePath = path.join(__dirname, "generated_image.png");

        const file = fs.createWriteStream(imagePath);
        https.get(imageUrl, (res) => {
            res.pipe(file);
            file.on("finish", () => {
                file.close();
                console.log("Image downloaded:", imagePath);
            });
        });

    } catch (error) {
        console.error("Error:", error.response ? error.response.data : error.message);
    }
}

// Example usage
generateLinkedInPost("Hiring software engineers in Ahmedabad!");
