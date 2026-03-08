# Real Fitbuddy Project

Real Fitbuddy is an AI-powered fitness planner web app that generates a personalized 7-day workout and diet plan based on user details.

## Features

- User profile form (name, age, weight, gender, diet preference, goal, intensity)
- AI-generated 7-day fitness + diet plan
- Diet-aware planning:
  - `vegetarian` users get vegetarian-only meal suggestions
  - `non-vegetarian` users get non-veg options included
- Plan display on frontend in a user-friendly format
- Feedback submission (rating, realism, comments)
- Local data storage using SQLite

## Tech Stack

- Frontend: `HTML`, `CSS`, `JavaScript`
- Backend: `Python`, `FastAPI`
- AI: `Google Gemini` (`gemini-2.5-flash`)
- Database: `SQLite` with `SQLAlchemy`
- Validation: `Pydantic`
- ASGI Server: `Uvicorn`

## Project Structure

- `index.html` - Frontend UI
- `main.py` - FastAPI backend and AI integration
- `requirements.txt` - Python dependencies
- `start_project.bat` - Starts frontend + backend
- `stop_project.bat` - Stops servers on ports `5500` and `8000`
- `fitness.db` - SQLite database (created automatically)

## Requirements

- Python 3.x
- Internet connection (required for Gemini API calls)
- Gemini API key in `.env`

## Environment Setup

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run the Application

### Option 1 (Recommended)

Run:

```bat
start_project.bat
```

This will:
- Ensure `pip` is available
- Install/update required packages
- Start backend on `127.0.0.1:8000`
- Start frontend on `localhost:5500`

### Option 2 (Manual)

Start backend:

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Start frontend (in another terminal):

```bash
python -m http.server 5500
```

## Access URLs

- Frontend: `http://localhost:5500`
- Backend API docs: `http://127.0.0.1:8000/docs`

## How It Works

1. User fills the form on frontend (`index.html`).
2. Frontend sends data to backend endpoint `POST /users/`.
3. Backend validates input via Pydantic.
4. Backend calls Gemini API to generate structured JSON plan.
5. Plan is saved in SQLite database and returned to frontend.
6. Frontend renders the 7-day plan.
7. User submits feedback to `POST /feedback/`.

## API Endpoints

- `POST /users/` - Create user profile and generate AI plan
- `POST /feedback/` - Submit user feedback

## Notes

- `.env`, `.venv`, and cache files are excluded from Git for security and cleanliness.
- If PowerShell blocks script activation, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
