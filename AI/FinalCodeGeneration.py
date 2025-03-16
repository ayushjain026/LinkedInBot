# Install dependencies
!pip install flask flask_cors transformers diffusers torch torchvision pillow pyngrok -q

import torch
from transformers import pipeline
from diffusers import StableDiffusionPipeline
from PIL import Image
import os
import uuid
import json
import time
import subprocess
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pyngrok import ngrok

# Authenticate ngrok (Replace with your actual auth token)
NGROK_AUTH_TOKEN = "2u1MRAQP8r0arJoo6QnXK0lvx73_6aVfvUHMS8utKYNnSCuqP"
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

# Start ngrok tunnel
print("Starting ngrok tunnel...")
http_tunnel = ngrok.connect(5000)
public_url = http_tunnel.public_url
print(f"Public URL: {public_url}")

# Global variable for ngrok URL
global ngrok_url
ngrok_url = public_url

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# Initialize text generation model
print("Loading text generation model...")
text_generator = pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B")

def generate_linkedin_content(prompt):
    try:
        response = text_generator(prompt, max_length=1000, num_return_sequences=1)
        return response[0]["generated_text"].strip()
    except Exception as e:
        print("Error in text generation:", str(e))
        return "Error generating text."

def generate_hashtags(prompt):
    keywords = prompt.lower().split()
    hashtags = ["#" + word.capitalize() for word in keywords if len(word) > 3]
    return " ".join(hashtags[:5])

# Load Stable Diffusion model
print("Loading Stable Diffusion model...")
try:
    model_id = "stabilityai/stable-diffusion-2-1"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe.to("cuda")
    print("Model loaded successfully!")
except Exception as e:
    print("Error loading Stable Diffusion model:", str(e))
    pipe = None  # Handle model loading failure gracefully

# Ensure static directory exists
os.makedirs("static", exist_ok=True)

def generate_image(prompt):
    if pipe is None:
        print("Image generation model not loaded.")
        return None
    
    try:
        print(f"Generating image for: {prompt}")
        image = pipe(prompt).images[0]
        filename = f"generated_{uuid.uuid4().hex}.png"
        filepath = os.path.join("static", filename)
        image.save(filepath)
        return filepath
    except Exception as e:
        print("Error in image generation:", str(e))
        return None

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get("prompt", "").strip()
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    print(f"Received prompt: {prompt}")
    
    content = generate_linkedin_content(prompt)
    hashtags = generate_hashtags(prompt)
    image_path = generate_image(prompt)
    
    if not image_path:
        return jsonify({"error": "Image generation failed."}), 500
    
    return jsonify({
        "postContent": f"{content}\n\n{hashtags}",
        "generatePostImage": f"{ngrok_url}/static/{os.path.basename(image_path)}"
    })

@app.route('/static/<filename>')
def serve_image(filename):
    return send_file(os.path.join("static", filename), mimetype="image/png")

if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0")
