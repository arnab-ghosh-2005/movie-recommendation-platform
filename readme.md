# Movie Recommendation Platform

A movie discovery app with a **Streamlit** interface and a **FastAPI** backend. Search for a movie, view its details and artwork, and explore recommendations based on both local TF-IDF similarity and TMDB genres.

**Author:** Arnab

## Features

- Browse TMDB movie feeds: trending, popular, top rated, now playing, and upcoming.
- Search TMDB by keyword and choose from matching movie suggestions.
- View movie details, release date, genres, overview, poster, and backdrop.
- Get content-based recommendations from a precomputed TF-IDF movie dataset.
- Get genre-based recommendations from TMDB.
- Explore the FastAPI endpoints interactively through Swagger UI.

## How it works

1. The Streamlit frontend in `app.py` provides the search, home feed, movie details, and recommendation views.
2. The frontend sends HTTP requests to the FastAPI service in `main.py`. Its API URL is read from `API_BASE`; by default, it uses `http://127.0.0.1:8000`.
3. FastAPI calls TMDB for live movie search, details, posters, feeds, and genre recommendations. The TMDB API key is kept in an environment variable.
4. At startup, the API loads the local movie dataset and precomputed TF-IDF model files. It finds similar titles by comparing the selected movie's TF-IDF row against the other rows.
5. The frontend displays the returned movie cards and recommendations.

The TF-IDF model files are already included, so you do not need to run the notebook to start the app.

## Project files

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit frontend |
| `main.py` | FastAPI backend and TMDB/TF-IDF endpoints |
| `requirements.txt` | Python dependencies |
| `.python-version` | Python version used by Render (`3.11.9`) |
| `df.pkl` | Local movie DataFrame used for recommendation titles |
| `indices.pkl` | Normalized movie-title-to-row mapping |
| `tfidf_matrix.pkl` | Precomputed TF-IDF feature matrix |
| `tfidf.pkl` | Saved TF-IDF vectorizer |
| `movies_metadata.csv` | Movie metadata source file |
| `movies.ipynb` | Notebook for exploring or preparing the movie data |

Keep the four `.pkl` files in the project root: the API loads them when it starts.

## Requirements

- Python **3.11.9** for Render, or the Python version selected for Streamlit Community Cloud (the dependencies support Python 3.14)
- A TMDB API key
- Git

## Clone and install

Replace the example repository URL and folder name below with your GitHub repository's URL and name:

```powershell
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell cannot find `py`, install Python 3.11 and use its `python` command to create the virtual environment instead.

On macOS or Linux, create and activate the environment with:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configure TMDB

Create a file named `.env` in the project root. Get a TMDB API key from [TMDB API settings](https://www.themoviedb.org/settings/api), then add:

```dotenv
TMDB_API_KEY=replace_with_your_tmdb_api_key
API_BASE=http://127.0.0.1:8000
```

`API_BASE` is optional for local development; the frontend defaults to `http://127.0.0.1:8000`. It can be set to a deployed API URL when the frontend and backend run as separate services. The frontend reads it from `.env` locally or from Streamlit secrets in Community Cloud.

Do not commit `.env` or publish your API key. The repository's `.gitignore` excludes `.env`.

## Run locally

Run the backend and frontend in **separate terminals** from the project root, with the virtual environment activated in each.

**Terminal 1 — FastAPI backend:**

```powershell
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API loads the pickled model files during startup. Wait for `Application startup complete` before using the frontend.

**Terminal 2 — Streamlit frontend:**

```powershell
python -m streamlit run app.py
```

Open the local Streamlit URL printed in the terminal (usually <http://localhost:8501>). The backend API is available at <http://127.0.0.1:8000>, with interactive documentation at <http://127.0.0.1:8000/docs>.

Check that the API is running at <http://127.0.0.1:8000/health>; it should return:

```json
{"status":"ok"}
```

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | API welcome message |
| `GET` | `/health` | Health check |
| `GET` | `/home` | TMDB movie feed |
| `GET` | `/tmdb/search?query=batman` | Search TMDB movies |
| `GET` | `/movie/id/{tmdb_id}` | Get movie details |
| `GET` | `/recommend/genre?tmdb_id={id}` | Get genre-based recommendations |
| `GET` | `/recommend/tfidf?title={title}` | Get local TF-IDF recommendations |
| `GET` | `/movie/search?query={title}` | Get details and both types of recommendations |

Interactive API documentation is available at `/docs` while the backend is running.

## Deploy on Render

Deploy the FastAPI backend as a **Web Service**:

- **Python version:** `3.11.9` (from `.python-version`)
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment variable:** `TMDB_API_KEY` set to your TMDB API key

If you deploy the Streamlit frontend as a separate web service, set its `API_BASE` environment variable to the public URL of the FastAPI service, for example `https://your-api-service.onrender.com`. A suitable Streamlit start command is:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

The backend and frontend must be running as separate services (or processes). When hosted separately, the browser uses the deployed Streamlit URL, while the frontend sends API requests to the URL configured in `API_BASE`.

### Streamlit Community Cloud

Community Cloud selects its Python version in the app's **Advanced settings**; the repository's `.python-version` file does not select it there. The current dependency pins support Python 3.14, as well as Python 3.11. To configure the frontend to use the deployed FastAPI backend, add this to the app's **Secrets** settings, replacing the example URL with your backend's public URL:

```toml
API_BASE = "https://your-api-service.onrender.com"
```

Keep `TMDB_API_KEY` configured on the FastAPI backend service; the Streamlit frontend calls that service and does not need the key itself.

## Credits

Movie search, details, artwork, and genre discovery are provided by [The Movie Database (TMDB)](https://www.themoviedb.org/).
