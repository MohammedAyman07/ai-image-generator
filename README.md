# AI Image Generator

A lightweight, high-performance web application that generates stunning images from text descriptions using the Hugging Face FLUX.1 neural network model.

## Overview

**🚀 Live Demo:** [https://ai-image-generator-three-iota.vercel.app/](https://ai-image-generator-three-iota.vercel.app/)

This project was built to provide an accessible, fast, and highly customizable AI art generation tool. It leverages state-of-the-art machine learning models via the Hugging Face Inference API and provides a clean, responsive, and glassmorphic UI for users to seamlessly generate, view, and download their creations. 

## Features

- **Advanced AI Generation:** Powered by `black-forest-labs/FLUX.1-schnell` for rapid, high-fidelity image synthesis.
- **Dynamic Styling Options:** Built-in prompt engineering logic for various art styles (Photorealistic, Anime, Cinematic, Digital Illustration, Logo).
- **Aspect Ratio Control:** Allows users to visualize how their prompt fits into 1:1, 16:9, or 9:16 canvases.
- **Rate Limiting:** Custom IP-based rate limiting to prevent API abuse and manage backend server load.
- **Glassmorphic UI:** A modern, fully responsive frontend with skeleton loading states for a premium user experience.

## Tech Stack

- **Backend:** Python 3, Flask, Waitress/Werkzeug
- **AI/ML Integration:** Hugging Face Inference Hub (`huggingface_hub`)
- **Frontend:** Vanilla HTML5, CSS3, JavaScript (ES6+)
- **Image Processing:** Pillow (PIL)
- **Deployment:** Vercel (Serverless Functions)

## Architecture

The application follows a standard client-server architecture with serverless capabilities:
1. **Client:** Sends a JSON payload containing the prompt and styling data to the server asynchronously.
2. **Server:** A Flask backend processes the request, validates input, applies rate-limiting rules, and communicates with the Hugging Face API using a secure backend token.
3. **Response:** The generated image bytes are converted into a Base64 string and sent back to the client for immediate rendering and downloading.

## Installation

### Prerequisites
- Python 3.8+
- A Hugging Face account and Access Token

### Local Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/MohammedAyman07/ai-image-generator.git
   cd ai-image-generator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory based on `.env.example`:
   ```env
   HF_TOKEN=your_hugging_face_token_here
   ```

## Running the Project

To start the development server locally, simply run:
```bash
python app.py
# OR use the provided batch script on Windows
.\run.bat
```
Navigate to `http://127.0.0.1:5000` in your browser.

## Configuration & Deployment (Vercel)

This project is configured out-of-the-box for serverless deployment on Vercel. 
The `vercel.json` file handles the routing of all requests to the Flask WSGI application.
When deploying, ensure you add `HF_TOKEN` to your Vercel Environment Variables.

## Testing

The project includes an automated test suite written in `pytest` to ensure core functionality and rate-limiting logic remain stable.

To run the tests:
```bash
pip install pytest pytest-flask
pytest test_app.py
```

## Technical Highlights

- **Server-Side Token Management:** The Hugging Face API key is strictly managed on the server side via environment variables, ensuring client-side security.
- **Asynchronous DOM Manipulation:** The frontend utilizes ES6 `async/await` and skeleton loading states to provide a non-blocking, smooth UX while the AI model processes the request.
- **In-Memory Rate Limiting:** Implemented a lightweight, dictionary-based rate limiter to protect the API from spam without requiring an external Redis cache, optimizing for serverless environments.

## License

This project is open-source and available under the [MIT License](LICENSE).
