# Micro Edu Tasks

A static web tool for comparing AI model responses on educational micro-tasks. Built for educators, developers, and policymakers to evaluate different AI models on real-world education scenarios.

Inspired from [Artificial Analysis MicroEvals page](https://artificialanalysis.ai/microevals)

## Overview

**Philosophy:** Static & Robust. Zero maintenance costs, high reliability, free hosting via GitHub Pages.

**How it works:**
1. Define tasks in a local JSON file
2. Run a Python script to generate AI responses (pre-computed)
3. Responses are saved as static JSON
4. A single-page web app displays the comparison UI

## Directory Structure

```
/project-root
├── /generator               # Private: Python generator
│   ├── tasks.json          # Source of truth for questions
│   ├── generate.py         # Generation engine
│   ├── requirements.txt    # Python dependencies
│   └── .env               # API keys (create from .env.example)
│
├── /docs                   # Public: The website
│   ├── index.html         # Single-page application
│   └── data.json          # Generated responses (auto-created)
│
└── README.md
```

## Setup Instructions

### 1. Clone and Setup Python Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd micro-edu-tasks

# Create a virtual environment
cd generator
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenRouter API key
# Get your key from: https://openrouter.ai/
```

Your `.env` file should look like:
```
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxx
```

### 3. Generate Responses

```bash
# Make sure you're in the generator directory with venv activated
cd generator
python generate.py
```

The script will:
- Load tasks from `tasks.json`
- Query AI models (API and/or local)
- Save responses to `../docs/data.json`
- Skip tasks that already have responses (incremental building)

**Options:**
- The script will ask if you want to include local models (Phi-3)
- By default, only API models are used (GPT-4o, Claude, Gemini)
- Local models require significant RAM and GPU is recommended

### 4. View the Website Locally

```bash
# From the project root
cd docs

# Start a simple HTTP server
# Python 3:
python -m http.server 8000

# Or use any other static file server
# Then open: http://localhost:8000
```

## Adding New Tasks

Edit `generator/tasks.json`:

```json
[
  {
    "id": "unique_id",
    "persona": "educator|developer|policymaker",
    "title": "Short Title",
    "prompt": "The full task prompt for the AI..."
  }
]
```

**Task Schema:**
- `id`: Unique identifier (e.g., "edu_01", "dev_01", "pol_01")
- `persona`: One of "educator", "developer", or "policymaker"
- `title`: Short, descriptive title shown in the UI
- `prompt`: The full prompt sent to AI models

After adding tasks, run `python generate.py` again to generate responses.

## Model Configuration

Edit the `MODELS` dictionary in `generate.py` to add/remove models:

```python
MODELS = {
    "gpt4o": {
        "type": "api",
        "id": "openai/gpt-4o",
        "display_name": "GPT-4o"
    },
    "phi3": {
        "type": "local",
        "id": "microsoft/Phi-3-mini-4k-instruct",
        "display_name": "Phi-3 Mini"
    }
}
```

**Model Types:**
- `"api"`: Uses OpenRouter API (requires API key and credits)
- `"local"`: Downloads and runs via Hugging Face Transformers

## Deployment to GitHub Pages

### 1. Create GitHub Repository

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit"

# Add remote and push
git remote add origin https://github.com/yourusername/micro-edu-tasks.git
git branch -M main
git push -u origin main
```

### 2. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under **Source**, select:
   - Branch: `main`
   - Folder: `/docs`
4. Click **Save**

Your site will be live at: `https://yourusername.github.io/micro-edu-tasks/`

### 3. Update Workflow

Whenever you add new tasks or want to update responses:

```bash
# 1. Edit tasks.json
# 2. Generate new responses
cd generator
python generate.py

# 3. Commit and push
cd ..
git add docs/data.json
git commit -m "Update task responses"
git push

# Site updates automatically in ~60 seconds
```

## Features

### Frontend Features
- **Landing Page**: Three-column layout for Educator/Developer/Policymaker personas
- **Task Browser**: Sidebar with filterable tasks by persona
- **Side-by-Side Comparison**: View responses from multiple models simultaneously
- **Simulated Loading**: Realistic "generating" animation for better UX
- **Markdown Rendering**: Rich text formatting with code blocks
- **Responsive Design**: Works on desktop and mobile

### Generator Features
- **Incremental Building**: Only generates missing responses (saves API costs)
- **Hybrid Execution**: Mix API models (fast) with local models (free)
- **Error Handling**: Graceful failures with detailed logging
- **Progress Tracking**: Live progress bars with tqdm
- **Rate Limiting**: Automatic delays for API calls

## Cost Estimation

**API Costs (via OpenRouter):**
- GPT-4o: ~$0.005-0.015 per task
- Claude 3.5 Sonnet: ~$0.003-0.012 per task
- Gemini 1.5 Pro: ~$0.001-0.004 per task

For 6 tasks × 3 models = **~$0.20-0.50 total**

**Local Models:**
- Free, but requires 8-16GB RAM
- GPU highly recommended for reasonable speed

## Troubleshooting

### "Failed to load data.json"
- Make sure you've run `generate.py` at least once
- Check that `docs/data.json` exists

### API Errors
- Verify your OpenRouter API key in `.env`
- Check your account has credits: https://openrouter.ai/credits
- Check internet connection

### Local Model Errors
- Ensure you have enough RAM (8GB minimum)
- Install PyTorch with CUDA if you have a GPU
- First run downloads models (~2-4GB), be patient

### Empty Responses in UI
- Check browser console for JavaScript errors
- Ensure `data.json` is valid JSON
- Try regenerating with `python generate.py`

## Tech Stack

**Generator:**
- Python 3.9+
- Transformers (Hugging Face)
- PyTorch
- OpenRouter API

**Frontend:**
- HTML5 / Vanilla JavaScript
- Tailwind CSS (CDN)
- Marked.js (Markdown rendering)
- FontAwesome icons

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Contact

For questions or issues, please open a GitHub issue.

---

Built with the philosophy: **Static & Robust**
