# AI Image Generator

**Live Demo:** https://ai-image-generator-three-iota.vercel.app/

## About

This is an AI image generator I built using Python, Flask and the Hugging Face Inference API.

You enter a text prompt, choose some options and the app sends the request to a Hugging Face image generation model. The generated image is then shown on the website and can be downloaded.

I built this project to learn more about connecting an AI model to a real web application and handling the backend part instead of only building the frontend.

## What I Built

- Generate images from text prompts
- Uses the `black-forest-labs/FLUX.1-schnell` model
- Different style options such as photorealistic, anime and cinematic
- 1:1, 16:9 and 9:16 aspect ratio options
- Image preview and download
- Loading/skeleton state while the image is being generated
- Responsive frontend
- Backend rate limiting
- API key kept on the server

## How It Works

The basic flow is:

```text
User enters prompt
       ↓
Frontend sends request
       ↓
Flask backend
       ↓
Hugging Face Inference API
       ↓
FLUX.1-schnell generates image
       ↓
Backend returns image
       ↓
Frontend displays image
```

The Hugging Face token is stored in an environment variable, so it is not placed in the frontend code.

## Technologies Used

- Python
- Flask
- Hugging Face `huggingface_hub`
- FLUX.1-schnell
- Pillow
- HTML5
- CSS3
- JavaScript (ES6+)
- Vercel
- Pytest

## Project Structure

```text
.
├── app.py              # Flask backend
├── test_app.py         # Backend tests
├── requirements.txt    # Python dependencies
├── vercel.json         # Vercel configuration
├── .env.example        # Environment variable example
│
├── templates/
│   ├── index.html      # Main page
│   ├── about.html
│   ├── privacy.html
│   ├── terms.html
│   └── contact.html
│
└── static/
    ├── css/            # Styles
    ├── js/             # Frontend JavaScript
    └── images/         # Website images
```

## Local Setup

### 1. Clone the project

```bash
git clone https://github.com/MohammedAyman07/ai-image-generator.git
cd ai-image-generator
```

### 2. Install the dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your Hugging Face token

Create a `.env` file using `.env.example`:

```env
HF_TOKEN=your_hugging_face_token_here
```

Do not commit your real token to GitHub.

### 4. Run the app

```bash
python app.py
```

On Windows, you can also use:

```bash
.\run.bat
```

Then open:

```text
http://127.0.0.1:5000
```

## Vercel Deployment

The project can be deployed on Vercel using the included `vercel.json` configuration.

After deploying, add this environment variable in the Vercel project settings:

```text
HF_TOKEN=your_hugging_face_token
```

The token should only be stored as a server-side environment variable.

## Rate Limiting

I added a simple IP-based rate limiter to stop users from sending generation requests continuously.

At the moment it uses an in-memory Python dictionary with a 2-second cooldown between requests from the same IP.

This is suitable for this small project, but if I were scaling the application, I would use something like Redis or another shared store so the rate limit works across multiple server instances.

## Testing

The project has tests using `pytest`.

Run them with:

```bash
pytest test_app.py
```

The tests currently check things such as:

- Main page loading
- Other page routes
- Missing prompt validation
- Rate limiting behavior

## AI Model

The project uses the pretrained `black-forest-labs/FLUX.1-schnell` model through Hugging Face.

I did not train the model myself. My work in this project was mainly around integrating the model into a web application, handling the API request, backend security, image processing, frontend interaction and deployment.

## Security

The Hugging Face API token is loaded from an environment variable using `python-dotenv`.

The token is not included in the frontend JavaScript or HTML.

For a real production application, I would also improve the rate limiting, request validation, logging and monitoring before handling a large number of users.

## AI-Assisted Development

I used AI tools as a coding assistant during parts of this project.

I used AI for things such as debugging, understanding errors, implementation ideas, and improving some parts of the code and documentation.

I reviewed and tested the project and I am responsible for the final code in this repository.

## What I Learned

This project helped me learn more about:

- Connecting an AI model to a web application
- Python and Flask backend development
- Working with the Hugging Face API
- Environment variables and API key security
- Image processing with Pillow
- REST-style request handling
- Rate limiting
- Writing backend tests with pytest
- Deploying a Python application on Vercel

## Future Improvements

- Use Redis for shared rate limiting
- Add better request validation
- Add more automated tests
- Improve error handling for API failures
- Add image history for users
- Add better monitoring and logging
- Improve performance for larger generated images

## License

MIT License
