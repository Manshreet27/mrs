import pandas as pd
import streamlit as st
import pickle
import requests

# Function to fetch movie poster
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=18379cbb9d00f61561a7d1d1a53afa91&language=en-US"
        response = requests.get(url, timeout=5)  # Timeout added
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

        data = response.json()
        poster_path = data.get('poster_path')

        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"

    except requests.exceptions.Timeout:
        st.error("Request timed out. Please check your internet connection.")
        return "https://via.placeholder.com/500x750?text=Timeout"

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/500x750?text=Error"

# Function to recommend movies
def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        recommended_movies_poster = []

        for i in movies_list:
            movie_id = movies.iloc[i[0]].movie_id  # Ensure correct column
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_movies_poster.append(fetch_poster(movie_id))

        return recommended_movies, recommended_movies_poster

    except IndexError:
        st.error("Movie not found in dataset or no recommendations available.")
        return [], []

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return [], []

# Load movie data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# Load similarity matrix
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit UI
st.title('🎬 Movie Recommender System')

selected_movies_name = st.selectbox("Type/Select a Movie:", movies['title'].values)

if st.button("Recommend"):
    names, posters = recommend(selected_movies_name)

    if names:  # Check if recommendations exist
        cols = st.columns(len(names))  # Create dynamic columns
        for i, col in enumerate(cols):  # Iterate safely over available recommendations
            with col:
                st.text(names[i])
                st.image(posters[i])
    else:
        st.warning("No recommendations found. Try another movie.")
