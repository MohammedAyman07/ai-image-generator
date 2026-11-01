# Ayman Image Generation

**Live Demo:** https://ai-image-generator-three-iota.vercel.app/

## About

This is an AI image generator I built using Python, Flask and Cloudflare Workers AI.

You enter a text prompt, choose creative options, and the app sends the request to Cloudflare's FLUX.2 Klein 9B model. The generated image is then shown on the website and can be downloaded.

I built this project to learn more about connecting an AI model to a real web application and handling the backend part instead of only building the frontend.

## What I Built

- Generate images from text prompts
- Uses the `@cf/black-forest-labs/flux-2-klein-9b` model
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
Cloudflare Workers AI REST API
       ↓
FLUX.2 Klein 9B generates image
       ↓
Backend returns image
       ↓
Frontend displays image
```

The Cloudflare account ID and API token are stored as server-side environment variables and are never sent to the browser.

## Technologies Used

- Python
- Flask
- Cloudflare Workers AI REST API
- FLUX.2 Klein 9B
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

### 3. Set up free image generation

Create a free Cloudflare account and enable Workers AI. Cloudflare Workers AI currently includes 10,000 Neurons per day at no charge. At 1,024 × 1,024 resolution, FLUX.2 Klein 9B uses about 1,364 Neurons per image, so this is roughly seven images per day before other Workers AI usage. The quota resets daily and is shared by everyone using this deployment. Create a Workers AI API token from the Workers AI dashboard and copy your Account ID. The token needs Workers AI Read and Edit permissions.

Create a `.env` file using `.env.example`:

```env
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
CLOUDFLARE_API_TOKEN=your_workers_ai_api_token
```

Keep these values private and do not commit your real token to GitHub.

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

In Vercel, open **Project Settings → Environment Variables** and add `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN`. Apply them to the Production environment, then redeploy. Store them as server-side variables; never add them to frontend code.

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

The project uses the `@cf/black-forest-labs/flux-2-klein-9b` model through Cloudflare Workers AI.

I did not train the model myself. My work in this project was mainly around integrating the model into a web application, handling the API request, backend security, image processing, frontend interaction and deployment.

## Security

The Cloudflare API token and account ID are loaded from server-side environment variables using `python-dotenv`.

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
- Working with the Cloudflare Workers AI API
- Environment variables and API key security
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
