import os

import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError

# =============================
# CONFIG
# =============================
load_dotenv()
try:
    api_base_secret = st.secrets.get("API_BASE")
except StreamlitSecretNotFoundError:
    api_base_secret = None

API_BASE = (
    os.getenv("API_BASE")
    or api_base_secret
    or "https://movie-recommendation-platform-1.onrender.com"
).rstrip("/")
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# =============================
# STYLES
# =============================
st.markdown(
    """
<style>
.stApp {
    background: radial-gradient(ellipse at top, #18243b 0%, #0b1120 48%, #080c15 100%);
    color: #e5e7eb;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: #0b1220; border-right: 1px solid #1d2940; }
.block-container { max-width: 1440px; padding-top: 1.6rem; padding-bottom: 3rem; }
h1, h2, h3 { letter-spacing: -0.035em; }
[data-testid="stMarkdownContainer"] p { color: #dbe4f0; }
[data-testid="stCaptionContainer"] { color: #a6b2c7; }
[data-testid="stTextInput"] input {
    background: #111a2b; border: 1px solid #34425d; border-radius: 12px;
    min-height: 3rem; color: #f8fafc;
}
[data-testid="stTextInput"] input:focus { border-color: #f97316; box-shadow: 0 0 0 1px #f97316; }
[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #26344d; border-radius: 16px; background: rgba(15, 23, 42, 0.72);
}
.stButton > button {
    background: #172237; border-color: #34425d; border-radius: 10px;
    color: #e5e7eb; transition: all 150ms ease;
}
.stButton > button:hover { border-color: #fb923c; color: #fdba74; }
.muted { color: #a6b2c7; }
.eyebrow { color: #fb923c; font-size: .78rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; }
</style>
""",
    unsafe_allow_html=True,
)

# =============================
# STATE + ROUTING (single-file pages)
# =============================
if "view" not in st.session_state:
    st.session_state.view = "home"  # home | details
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None
if "watchlist" not in st.session_state:
    st.session_state.watchlist = {}
if "home_section" not in st.session_state:
    st.session_state.home_section = "Discover"

qp_view = st.query_params.get("view")
qp_id = st.query_params.get("id")
if qp_view in ("home", "details"):
    st.session_state.view = qp_view
if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except:
        pass


def goto_home():
    st.session_state.view = "home"
    st.session_state.home_section = "Discover"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_watchlist():
    st.session_state.view = "home"
    st.session_state.home_section = "Watchlist"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


def toggle_watchlist(movie):
    tmdb_id = movie.get("tmdb_id")
    if not tmdb_id:
        return
    tmdb_id = int(tmdb_id)
    if tmdb_id in st.session_state.watchlist:
        del st.session_state.watchlist[tmdb_id]
    else:
        st.session_state.watchlist[tmdb_id] = movie


# =============================
# API HELPERS
# =============================
@st.cache_data(ttl=30)  # short cache for autocomplete
def api_get_json(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"


def poster_grid(cards, cols=5, key_prefix="grid"):
    if not cards:
        st.info("No movies to show.")
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        colset = st.columns(cols)
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]
            idx += 1

            tmdb_id = m.get("tmdb_id")
            title = m.get("title", "Untitled")
            poster = m.get("poster_url")

            with colset[c]:
                with st.container(border=True):
                    if poster:
                        st.image(poster, width="stretch")
                    else:
                        st.write("🎞️ Poster unavailable")

                    st.text(title)
                    release_date = m.get("release_date") or ""
                    year = release_date[:4]
                    rating = m.get("vote_average")
                    rating_label = (
                        f"★ {rating:.1f}"
                        if isinstance(rating, (int, float)) and rating > 0
                        else ""
                    )
                    metadata = [value for value in (year, rating_label) if value]
                    if metadata:
                        st.caption(" · ".join(metadata))

                    if st.button(
                        "Open",
                        key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}",
                        width="stretch",
                    ):
                        if tmdb_id:
                            goto_details(tmdb_id)

                    if tmdb_id:
                        saved = int(tmdb_id) in st.session_state.watchlist
                        if st.button(
                            "♥ Saved" if saved else "♡ Save",
                            key=f"watch_{key_prefix}_{r}_{c}_{idx}_{tmdb_id}",
                            help="Remove from your watchlist" if saved else "Add to your watchlist",
                            width="stretch",
                        ):
                            toggle_watchlist(m)


def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append(
                {
                    "tmdb_id": tmdb["tmdb_id"],
                    "title": tmdb.get("title") or x.get("title") or "Untitled",
                    "poster_url": tmdb.get("poster_url"),
                }
            )
    return cards


# =============================
# IMPORTANT: Robust TMDB search parsing
# Supports BOTH API shapes:
# 1) raw TMDB: {"results":[{id,title,poster_path,...}]}
# 2) list cards: [{tmdb_id,title,poster_url,...}]
# =============================
def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    """
    Returns:
      suggestions: list[(label, tmdb_id)]
      cards: list[{tmdb_id,title,poster_url}]
    """
    keyword_l = keyword.strip().lower()

    # A) If API returns dict with 'results'
    if isinstance(data, dict) and "results" in data:
        raw = data.get("results") or []
        raw_items = []
        for m in raw:
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            poster_path = m.get("poster_path")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                    "release_date": m.get("release_date", ""),
                    "vote_average": m.get("vote_average"),
                }
            )

    # B) If API returns already as list
    elif isinstance(data, list):
        raw_items = []
        for m in data:
            # might be {tmdb_id,title,poster_url}
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title = (m.get("title") or "").strip()
            poster_url = m.get("poster_url")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": poster_url,
                    "release_date": m.get("release_date", ""),
                    "vote_average": m.get("vote_average"),
                }
            )
    else:
        return [], []

    # Word-match filtering (contains)
    matched = [x for x in raw_items if keyword_l in x["title"].lower()]

    # If nothing matched, fallback to raw list (so never blank)
    final_list = matched if matched else raw_items

    # Suggestions = top 10 labels
    suggestions = []
    for x in final_list[:10]:
        year = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    # Cards = top N
    cards = [
        {
            "tmdb_id": x["tmdb_id"],
            "title": x["title"],
            "poster_url": x["poster_url"],
            "release_date": x.get("release_date", ""),
            "vote_average": x.get("vote_average"),
        }
        for x in final_list[:limit]
    ]
    return suggestions, cards


# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.markdown("## 🎬 Reel Finder")
    if st.button("🏠 Home"):
        goto_home()
    if st.button("♡ Watchlist"):
        goto_watchlist()

    st.markdown("---")
    st.markdown("### Discover")
    home_category = st.selectbox(
        "Category",
        ["trending", "popular", "top_rated", "now_playing", "upcoming"],
        index=0,
    )
    grid_cols = st.slider("Grid columns", 3, 6, 5)
    st.caption("Your watchlist is saved for this browsing session.")

# =============================
# HEADER
# =============================
st.markdown(
    "<div class='eyebrow'>Your next movie starts here</div>",
    unsafe_allow_html=True,
)
st.title("Find a film worth staying in for.")
st.markdown(
    "<p class='muted'>Search the movie universe, save your picks, and discover "
    "what to watch next.</p>",
    unsafe_allow_html=True,
)

# ==========================================================
# VIEW: HOME
# ==========================================================
if st.session_state.view == "home":
    with st.container(border=True):
        typed = st.text_input(
            "Search by movie title",
            placeholder="Try Dune, Batman, or The Godfather",
            key="movie_search",
        )
        st.caption(
            "Start typing to see movie suggestions. "
            "Choose a suggestion to open its details."
        )

    if st.session_state.home_section == "Watchlist":
        st.markdown("### Your watchlist")
        saved_movies = list(st.session_state.watchlist.values())
        if saved_movies:
            poster_grid(saved_movies, cols=grid_cols, key_prefix="watchlist")
        else:
            st.info(
                "Your watchlist is empty. Save movies from Discover to keep them "
                "here for this session."
            )
        st.stop()

    # SEARCH MODE (live suggestions below the search field)
    if typed.strip():
        query = typed.strip()
        if len(query) < 2:
            st.caption("Enter at least 2 characters to search.")
        else:
            data, err = api_get_json("/tmdb/search", params={"query": query})

            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                suggestions, cards = parse_tmdb_search_to_cards(data, query, limit=24)

                if suggestions:
                    st.markdown("### Suggestions")
                    with st.container(border=True):
                        suggestion_cols = st.columns(2)
                        for index, (label, tmdb_id) in enumerate(suggestions):
                            with suggestion_cols[index % len(suggestion_cols)]:
                                if st.button(
                                    f"🎬  {label}",
                                    key=f"suggestion_{tmdb_id}_{index}",
                                    width="stretch",
                                ):
                                    goto_details(tmdb_id)
                else:
                    st.info("No suggestions found. Try another movie title.")

                st.markdown("### Matching movies")
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")

        st.stop()

    # HOME FEED MODE
    st.markdown(f"### {home_category.replace('_', ' ').title()} movies")

    home_cards, err = api_get_json(
        "/home", params={"category": home_category, "limit": 24}
    )
    if err or not home_cards:
        st.error(f"Home feed failed: {err or 'Unknown error'}")
        st.stop()

    poster_grid(home_cards, cols=grid_cols, key_prefix="home_feed")

# ==========================================================
# VIEW: DETAILS
# ==========================================================
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("← Back to Home"):
            goto_home()
        st.stop()

    # Top bar
    a, b = st.columns([3, 1])
    with a:
        st.markdown("### Movie details")
    with b:
        if st.button("← Back to Home"):
            goto_home()

    # Details (your FastAPI safe route)
    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    saved = tmdb_id in st.session_state.watchlist
    if st.button(
        "♥ Saved" if saved else "♡ Save to watchlist",
        help="Toggle this movie in your watchlist",
    ):
        toggle_watchlist(
            {
                "tmdb_id": tmdb_id,
                "title": data.get("title", "Untitled"),
                "poster_url": data.get("poster_url"),
                "release_date": data.get("release_date", ""),
                "vote_average": data.get("vote_average"),
            }
        )
        st.rerun()

    # Layout: Poster LEFT, Details RIGHT
    left, right = st.columns([1, 2.4], gap="large")

    with left:
        with st.container(border=True):
            if data.get("poster_url"):
                st.image(
                    data["poster_url"],
                    width="stretch",
                )
            else:
                st.write("🎞️ Poster unavailable")

    with right:
        with st.container(border=True):
            st.subheader(data.get("title") or "")
            release = data.get("release_date") or "-"
            genres = ", ".join([g["name"] for g in data.get("genres", [])]) or "-"
            st.caption(f"Release: {release} · Genres: {genres}")
            st.divider()
            st.markdown("### Overview")
            st.write(data.get("overview") or "No overview available.")

    if data.get("backdrop_url"):
        st.markdown("#### Backdrop")
        st.image(
            data["backdrop_url"],
            width="stretch",
        )

    st.divider()
    st.markdown("### ✅ Recommendations")

    # Recommendations (TF-IDF + Genre) via your bundle endpoint
    title = (data.get("title") or "").strip()
    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            st.markdown("#### 🔎 Similar Movies (TF-IDF)")
            poster_grid(
                to_cards_from_tfidf_items(bundle.get("tfidf_recommendations")),
                cols=grid_cols,
                key_prefix="details_tfidf",
            )

            st.markdown("#### 🎭 More Like This (Genre)")
            poster_grid(
                bundle.get("genre_recommendations", []),
                cols=grid_cols,
                key_prefix="details_genre",
            )
        else:
            st.info("Showing Genre recommendations (fallback).")
            genre_only, err3 = api_get_json(
                "/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18}
            )
            if not err3 and genre_only:
                poster_grid(
                    genre_only, cols=grid_cols, key_prefix="details_genre_fallback"
                )
            else:
                st.warning("No recommendations available right now.")
    else:
        st.warning("No title available to compute recommendations.")
