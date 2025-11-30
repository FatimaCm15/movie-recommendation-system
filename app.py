import streamlit as st
import pandas as pd
import pickle
import requests
import time
import gdown
import pickle
import os

def load_similarity(file_path, file_url):
    if not os.path.exists(file_path):
        gdown.download(file_url, file_path, quiet=False)
    with open(file_path, 'rb') as f:
        return pickle.load(f)

similarity = load_similarity(
    "similarity.pkl",
    "https://drive.google.com/file/d/1ZC45QXuuCqQmFq0sYxiy8xtwxjm7NnG-/view?usp=drive_link"
)

# ------------------------
@st.cache_data
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=c9f33c3aff90e52b77b68217f47746a1&language=en-US"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Poster"
    except:
        return "https://via.placeholder.com/500x750?text=Error"


# ------------------------
# Recommend movies
# ------------------------
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), key=lambda x: x[1], reverse=True)[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in distances:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)

        poster = fetch_poster(movie_id)
        recommended_movies_posters.append(poster)

        time.sleep(0.25)  # Delay to prevent TMDb rate-limit issues

    return recommended_movies, recommended_movies_posters


# ------------------------
# Load movie data and similarity matrix
# ------------------------
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# ------------------------
# Streamlit UI
# ------------------------
st.title('Movie Recommendation System')

selected_movie_name = st.selectbox(
    'Select a movie:',
    movies['title'].values
)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.text(name)
            st.image(poster)
